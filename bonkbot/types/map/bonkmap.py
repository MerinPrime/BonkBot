from typing import List

from attrs import define, field

from ...core.constants import MAP_VERSION
from ...pson.bytebuffer import ByteBuffer
from ...utils.validation import validate_int, validate_type, validate_type_list
from .capture_zone import CaptureZone
from .map_metadata import MapMetadata
from .map_properties import MapProperties
from .physics import CollideGroup
from .physics.body.body import Body
from .physics.body.body_type import BodyType
from .physics.collide import CollideFlag
from .physics.fixture import Fixture
from .physics.joint.distance_joint import DistanceJoint
from .physics.joint.gear_joint import GearJoint
from .physics.joint.lpj_joint import LPJJoint
from .physics.joint.lsj_joint import LSJJoint
from .physics.joint.revolute_joint import RevoluteJoint
from .physics.map_physics import MapPhysics
from .physics.shape.box_shape import BoxShape
from .physics.shape.circle_shape import CircleShape
from .physics.shape.polygon_shape import PolygonShape
from .spawn import Spawn


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IMap.ts
@define(slots=True, auto_attribs=True)
class BonkMap:
    version: int = field(default=MAP_VERSION, validator=validate_int(1))
    metadata: 'MapMetadata' = field(factory=MapMetadata, validator=validate_type(MapMetadata))
    properties: 'MapProperties' = field(factory=MapProperties, validator=validate_type(MapProperties))
    physics: 'MapPhysics' = field(factory=MapPhysics, validator=validate_type(MapPhysics))
    spawns: List['Spawn'] = field(factory=list, validator=validate_type_list(Spawn))
    cap_zones: List['CaptureZone'] = field(factory=list, validator=validate_type_list(CaptureZone))

    # TODO: Make user-friendly
    # TODO: And maybe split to_json, from_json, decode_from_database to MapMetadata, MapProperties, MapPhysics etc.

    def to_json(self) -> dict:
        data = {
            'v': self.version,
            'm': {},
            's': {},
            'physics': {
                'bodies': [],
                'fixtures': [],
                'joints': [],
                'shapes': [],
                'bro': [],
            },
            'spawns': [],
            'capZones': [],
        }
        data['s'] = self.properties.to_json()
        data['m'] = self.metadata.to_json()
        for body in self.physics.bodies:
            body_data = {}
            if body.name is not None:
                body_data['n'] = body.name
            body_data['a'] = body.angle
            body_data['av'] = body.angular_velocity
            body_data['fx'] = body.fixtures
            body_data['p'] = body.position
            body_data['lv'] = body.linear_velocity
            body_data['cf'] = body.force.to_json()
            body_data['fz'] = body.force_zone.to_json()
            body_data['s'] = body.shape.to_json()
            data['physics']['bodies'].append(body_data)
        for fixture in self.physics.fixtures:
            data['physics']['fixtures'].append(fixture.to_json())
        for joint in self.physics.joints:
            data['physics']['joints'].append(joint.to_json())
        for shape in self.physics.shapes:
            data['physics']['shapes'].append(shape.to_json())
        data['physics']['bro'] = self.physics.bro.copy()
        data['physics']['ppm'] = self.physics.ppm
        for spawn in self.spawns:
            data['spawns'].append(spawn.to_json())
        for capture_zone in self.cap_zones:
            data['capZones'].append(capture_zone.to_json())
        
        return data

    @staticmethod
    def decode_from_database(encoded_data: str) -> 'BonkMap':
        buffer = ByteBuffer().from_base64(encoded_data, lz_encoded=True)

        bonk_map = BonkMap()
        bonk_map.version = buffer.read_int16()
        if bonk_map.version > MAP_VERSION:
            raise NotImplementedError('Future map version.')

        bonk_map.properties.from_buffer(buffer, bonk_map.version)
        bonk_map.metadata.from_buffer(buffer, bonk_map.version)
        bonk_map.physics.ppm = buffer.read_int16()

        bro_count = buffer.read_int16()
        for _ in range(bro_count):
            bonk_map.physics.bro.append(buffer.read_int16())

        shapes_count = buffer.read_int16()
        for _ in range(shapes_count):
            shape_id = buffer.read_int16()
            if shape_id == 1:
                shape = BoxShape()
                shape.from_buffer(buffer)
            elif shape_id == 2:
                shape = CircleShape()
                shape.from_buffer(buffer)
            elif shape_id == 3:
                shape = PolygonShape()
                shape.from_buffer(buffer)
            else:
                raise ValueError(f'Invalid shape id: {shape_id}')
            bonk_map.physics.shapes.append(shape)

        fixtures_count = buffer.read_int16()
        for _ in range(fixtures_count):
            bonk_map.physics.fixtures.append(Fixture().from_buffer(buffer, bonk_map.version))

        body_count = buffer.read_int16()
        for _ in range(body_count):
            body = Body()
            body.shape.body_type = BodyType.from_name(buffer.read_utf())
            body.shape.name = buffer.read_utf()
            body.position = (buffer.read_float64(), buffer.read_float64())
            body.angle = buffer.read_float64()
            body.shape.friction = buffer.read_float64()
            body.shape.friction_players = buffer.read_bool()
            body.shape.restitution = buffer.read_float64()
            body.shape.density = buffer.read_float64()
            body.linear_velocity = (buffer.read_float64(), buffer.read_float64())
            body.angular_velocity = buffer.read_float64()
            body.shape.linear_damping = buffer.read_float64()
            body.shape.angular_damping = buffer.read_float64()
            body.shape.fixed_rotation = buffer.read_bool()
            body.shape.anti_tunnel = buffer.read_bool()
            body.force.from_buffer(buffer)
            body.shape.collide_group = CollideGroup.from_id(buffer.read_int16())
            body.shape.collide_mask = CollideFlag.from_buffer(buffer, bonk_map.version)
            if bonk_map.version >= 14:
                body.force_zone.from_buffer(buffer, bonk_map.version)
            fixtures_count = buffer.read_int16()
            for _ in range(fixtures_count):
                body.fixtures.append(buffer.read_int16())
            bonk_map.physics.bodies.append(body)
        spawn_count = buffer.read_int16()
        for _ in range(spawn_count):
            bonk_map.spawns.append(Spawn().from_buffer(buffer))
        cap_zone_count = buffer.read_int16()
        for _ in range(cap_zone_count):
            bonk_map.cap_zones.append(CaptureZone().from_buffer(buffer, bonk_map.version))
        joint_count = buffer.read_int16()
        for _ in range(joint_count):
            joint_type_id = buffer.read_int16()
            if joint_type_id == 1:
                joint = RevoluteJoint()
                joint.from_buffer(buffer)
            elif joint_type_id == 2:
                joint = DistanceJoint()
                joint.from_buffer(buffer)
            elif joint_type_id == 3:
                joint = LPJJoint()
                joint.from_buffer(buffer)
            elif joint_type_id == 4:
                joint = LSJJoint()
                joint.from_buffer(buffer)
            elif joint_type_id == 5:
                joint = GearJoint()
                joint.from_buffer(buffer)
            else:
                raise ValueError(f'Invalid joint id: {joint_type_id}')
            bonk_map.physics.joints.append(joint)

        return bonk_map

    @classmethod
    def from_json(cls, json_data: dict) -> 'BonkMap':
        bonk_map = BonkMap()
        bonk_map.version = json_data['v']
        bonk_map.properties.from_json(json_data['s'])
        bonk_map.metadata.from_json(json_data['m'])
        for body_data in json_data['physics']['bodies']:
            body = Body()
            if body_data.get('n') is not None:
                body.name = body_data['n']
            body.angle = body_data['a']
            body.angular_velocity = body_data['av']
            body.fixtures = body_data['fx']
            body.position = (body_data['p'][0], body_data['p'][1])
            body.linear_velocity = (body_data['lv'][0], body_data['lv'][1])
            body.force.from_json(body_data['cf'])
            body.force_zone.from_json(body_data['fz'])
            body.shape.from_json(body_data['s'])
            bonk_map.physics.bodies.append(body)
        for fixture_data in json_data['physics']['fixtures']:
            bonk_map.physics.fixtures.append(Fixture().from_json(fixture_data))
        for joint_data in json_data['physics']['joints']:
            if joint_data['type'] == 'rv':
                joint = RevoluteJoint()
                joint.from_json(joint_data)
            elif joint_data['type'] == 'd':
                joint = DistanceJoint()
                joint.from_json(joint_data)
            elif joint_data['type'] == 'lpj':
                joint = LPJJoint()
                joint.from_json(joint_data)
            elif joint_data['type'] == 'lsj':
                joint = LSJJoint()
                joint.from_json(joint_data)
            elif joint_data['type'] == 'g':
                joint = GearJoint()
                joint.from_json(joint_data)
            else:
                raise ValueError(f'Invalid joint type: {joint_data["type"]}')
            bonk_map.physics.joints.append(joint)
        for shape_data in json_data['physics']['shapes']:
            if shape_data['type'] == 'bx':
                shape = BoxShape()
                shape.from_json(shape_data)
            elif shape_data['type'] == 'ci':
                shape = CircleShape()
                shape.from_json(shape_data)
            elif shape_data['type'] == 'po':
                shape = PolygonShape()
                shape.from_json(shape_data)
            else:
                raise ValueError(f'Invalid shape type: {shape_data["type"]}')
            bonk_map.physics.shapes.append(shape)
        bonk_map.physics.bro = json_data['physics']['bro'].copy()
        bonk_map.physics.ppm = json_data['physics']['ppm']
        for spawn_data in json_data['spawns']:
            bonk_map.spawns.append(Spawn().from_json(spawn_data))
        for capture_zone_data in json_data['capZones']:
            bonk_map.cap_zones.append(CaptureZone().from_json(capture_zone_data))
        return bonk_map

DEFAULT_MAP = BonkMap.decode_from_database('ILAcJAhBFBjBzCIDCAbAcgBwEYA1IDOAWgMrAAeAJgFYCiwytlAjEQGLoAMsAtm50gCmAdwbBIbACoBDAOrNh2AOIBVeAFlcATXIBJZAAtURJak4BpaMAASJAExsCW2eQPTRkACJFdITwDMANRB6RhZ2Ll5+JCgAdhjgX08PGKsYa0gE8WB0LLz8goKrCGZA7B4AVgNsWUCAa10OAHstfFR-AGoAeh7envAbLoA3Pr7O0d7waWxMOyzM4DYALxBhKjp4FSVXSiUiId4BQuO8roAWfOQugYTPLsl1JcfnlZO394-Pk7TgaFpMv4QegQZDCNh1LKeYAAeWKXwKMH+vyQgUksCUbAAzNg6pAiHlhJ4IfDCioAcCQGwVJjIAZKHYLkggA')
