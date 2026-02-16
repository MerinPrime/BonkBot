from typing import List

from attrs import define, field

from ...pson.bytebuffer import ByteBuffer
from ...utils.validation import validate_int, validate_type, validate_type_list
from .capture_zone import CaptureZone
from .map_metadata import MapMetadata
from .map_properties import MapProperties
from .physics.body.body import Body
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

MAP_VERSION = 15


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IMap.ts
@define(slots=True, auto_attribs=True)
class BonkMap:
    version: int = field(default=MAP_VERSION, validator=validate_int(1))
    metadata: 'MapMetadata' = field(
        factory=MapMetadata,
        validator=validate_type(MapMetadata),
    )
    properties: 'MapProperties' = field(
        factory=MapProperties,
        validator=validate_type(MapProperties),
    )
    physics: 'MapPhysics' = field(
        factory=MapPhysics,
        validator=validate_type(MapPhysics),
    )
    spawns: List['Spawn'] = field(factory=list, validator=validate_type_list(Spawn))
    cap_zones: List['CaptureZone'] = field(
        factory=list,
        validator=validate_type_list(CaptureZone),
    )

    # TODO: Make user-friendly
    # TODO: And maybe split to_json, from_json, decode_from_database to MapMetadata, MapProperties, MapPhysics etc.

    def to_json(self) -> dict:
        data = {
            'v': self.version,
            'm': self.metadata.to_json(),
            's': self.properties.to_json(),
            'physics': {
                'bodies': [],
                'fixtures': [],
                'joints': [],
                'shapes': [],
                'bro': self.physics.bro.copy(),
                'ppm': self.physics.ppm,
            },
            'spawns': [],
            'capZones': [],
        }
        for body in self.physics.bodies:
            data['physics']['bodies'].append(body.to_json())
        for fixture in self.physics.fixtures:
            data['physics']['fixtures'].append(fixture.to_json())
        for joint in self.physics.joints:
            data['physics']['joints'].append(joint.to_json())
        for shape in self.physics.shapes:
            data['physics']['shapes'].append(shape.to_json())
        for spawn in self.spawns:
            data['spawns'].append(spawn.to_json())
        for capture_zone in self.cap_zones:
            data['capZones'].append(capture_zone.to_json())

        return data

    def encode_to_database(self) -> 'BonkMap':
        buffer = ByteBuffer()
        buffer.set_big_endian()

        buffer.write_int16(MAP_VERSION)
        self.properties.to_buffer(buffer)
        self.metadata.to_buffer(buffer)
        buffer.write_int16(self.physics.ppm)

        buffer.write_int16(len(self.physics.bro))
        for bro in self.physics.bro:
            buffer.write_int16(bro)

        buffer.write_int16(len(self.physics.shapes))
        for shape in self.physics.shapes:
            if isinstance(shape, BoxShape):
                buffer.write_int16(1)
            elif isinstance(shape, CircleShape):
                buffer.write_int16(2)
            elif isinstance(shape, PolygonShape):
                buffer.write_int16(3)
            shape.to_buffer(buffer)

        buffer.write_int16(len(self.physics.fixtures))
        for fixture in self.physics.fixtures:
            fixture.to_buffer(buffer)
        buffer.write_int16(len(self.physics.bodies))
        for body in self.physics.bodies:
            body.to_buffer(buffer)
        buffer.write_int16(len(self.spawns))
        for spawn in self.spawns:
            spawn.to_buffer(buffer)
        buffer.write_int16(len(self.cap_zones))
        for cap_zone in self.cap_zones:
            cap_zone.to_buffer(buffer)

        buffer.write_int16(len(self.physics.joints))
        for joint in self.physics.joints:
            if isinstance(joint, RevoluteJoint):
                buffer.write_int16(1)
            elif isinstance(joint, DistanceJoint):
                buffer.write_int16(2)
            elif isinstance(joint, LPJJoint):
                buffer.write_int16(3)
            elif isinstance(joint, LSJJoint):
                buffer.write_int16(4)
            elif isinstance(joint, GearJoint):
                buffer.write_int16(5)
            joint.to_buffer(buffer)

        return buffer.to_base64(lz_encode=True)

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
            bonk_map.physics.fixtures.append(
                Fixture().from_buffer(buffer, bonk_map.version),
            )
        body_count = buffer.read_int16()
        for _ in range(body_count):
            bonk_map.physics.bodies.append(Body().from_buffer(buffer, bonk_map.version))
        spawn_count = buffer.read_int16()
        for _ in range(spawn_count):
            bonk_map.spawns.append(Spawn().from_buffer(buffer))
        cap_zone_count = buffer.read_int16()
        for _ in range(cap_zone_count):
            bonk_map.cap_zones.append(
                CaptureZone().from_buffer(buffer, bonk_map.version),
            )
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
            bonk_map.physics.bodies.append(Body().from_json(body_data))
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


DEFAULT_MAP = BonkMap.decode_from_database(
    'ILAcJAhBFBjBzCIDCAbAcgBwEYA1IDOAWgMrAAeAJgFYCiwytlAjEQGLoAMsAtm50gCmAdwbBIbACoBDAOrNh2AOIBVeAFlcATXIBJZAAtURJak4BpaMAASJAExsCW2eQPTRkACJFdITwDMANRB6RhZ2Ll5+JCgAdhjgX08PGKsYa0gE8WB0LLz8goKrCGZA7B4AVgNsWUCAa10OAHstfFR-AGoAeh7envAbLoA3Pr7O0d7waWxMOyzM4DYALxBhKjp4FSVXSiUiId4BQuO8roAWfOQugYTPLsl1JcfnlZO394-Pk7TgaFpMv4QegQZDCNh1LKeYAAeWKXwKMH+vyQgUksCUbAAzNg6pAiHlhJ4IfDCioAcCQGwVJjIAZKHYLkggA',
)
