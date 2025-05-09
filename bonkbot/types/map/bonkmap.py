from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List

from ...pson.bytebuffer import ByteBuffer
from ..mode import Mode
from .capture_zone import CaptureType, CaptureZone
from .map_metadata import MapMetadata
from .map_properties import MapProperties
from .physics.body.body import Body
from .physics.body.body_type import BodyType
from .physics.body.force_zone import ForceZoneType
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

if TYPE_CHECKING:
    from .physics.joint.joint import Joint


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IMap.ts
@dataclass
class BonkMap:
    version: int = 1
    metadata: 'MapMetadata' = field(default_factory=MapMetadata)
    properties: 'MapProperties' = field(default_factory=MapProperties)
    physics: 'MapPhysics' = field(default_factory=MapPhysics)
    spawns: List['Spawn'] = field(default_factory=list)
    cap_zones: List['CaptureZone'] = field(default_factory=list)
    joints: List['Joint'] = field(default_factory=list)

    @staticmethod
    def decode_from_database(encoded_data: str) -> 'BonkMap':
        buffer = ByteBuffer().from_base64(encoded_data, lz_encoded=True)

        bonk_map = BonkMap()
        bonk_map.version = buffer.read_int16()
        if bonk_map.version > 15:
            raise NotImplementedError('Future map version.')

        # region Properties
        bonk_map.properties.respawn_on_death = buffer.read_bool()
        bonk_map.properties.players_dont_collide = buffer.read_bool()

        if bonk_map.version >= 3:
            bonk_map.properties.complex_physics = buffer.read_int16() == 2

        if 4 <= bonk_map.version <= 12:
            bonk_map.properties.grid_size = buffer.read_int16()
        elif bonk_map.version >= 13:
            bonk_map.properties.grid_size = buffer.read_float32()

        if bonk_map.version >= 9:
            bonk_map.properties.players_can_fly = buffer.read_bool()
        # endregion
        # region MetaData
        bonk_map.metadata.original_name = buffer.read_utf()
        bonk_map.metadata.original_author = buffer.read_utf()
        bonk_map.metadata.original_database_id = buffer.read_uint32()
        bonk_map.metadata.original_database_version = buffer.read_int16()
        bonk_map.metadata.name = buffer.read_utf()
        bonk_map.metadata.author = buffer.read_utf()

        if bonk_map.version >= 10:
            bonk_map.metadata.votes_up = buffer.read_uint32()
            bonk_map.metadata.votes_down = buffer.read_uint32()

        if bonk_map.version >= 4:
            bonk_map.metadata.contributors = []
            contributors_count = buffer.read_int16()
            for _ in range(contributors_count):
                bonk_map.metadata.contributors.append(buffer.read_utf())

        if bonk_map.version >= 5:
            bonk_map.metadata.mode = Mode.from_mode_code(buffer.read_utf())
            bonk_map.metadata.database_id = buffer.read_int32()

        if bonk_map.version >= 7:
            bonk_map.metadata.is_published = buffer.read_bool()

        if bonk_map.version >= 8:
            bonk_map.metadata.database_version = buffer.read_int32()
        # endregion
        # region Physics
        bonk_map.physics.ppm = buffer.read_int16()

        bro_count = buffer.read_int16()
        for _ in range(bro_count):
            bonk_map.physics.bro.append(buffer.read_int16())

        shapes_count = buffer.read_int16()
        for _ in range(shapes_count):
            shape_id = buffer.read_int16()
            if shape_id == 1:
                shape = BoxShape()
                shape.width = buffer.read_float64()
                shape.height = buffer.read_float64()
                shape.position = (buffer.read_float64(), buffer.read_float64())
                shape.angle = buffer.read_float64()
                shape.shrink = buffer.read_bool()
            elif shape_id == 2:
                shape = CircleShape()
                shape.radius = buffer.read_float64()
                shape.position = (buffer.read_float64(), buffer.read_float64())
                shape.shrink = buffer.read_bool()
            elif shape_id == 3:
                shape = PolygonShape()
                shape.scale = buffer.read_float64()
                shape.angle = buffer.read_float64()
                shape.position = (buffer.read_float64(), buffer.read_float64())
                shape.vertices = []
                vertices_count = buffer.read_int16()
                for _ in range(vertices_count):
                    shape.vertices.append((buffer.read_float64(), buffer.read_float64()))
            else:
                raise ValueError(f'Invalid shape id: {shape_id}')
            bonk_map.physics.shapes.append(shape)

        fixtures_count = buffer.read_int16()
        for _ in range(fixtures_count):
            fixture = Fixture(shape_id=-1)
            fixture.shape_id = buffer.read_int16()
            fixture.name = buffer.read_utf()

            fixture.friction = buffer.read_float64()
            if fixture.friction == 1.7976931348623157e+308:
                fixture.friction = None

            friction_players = buffer.read_int16()
            if friction_players == 0:
                fixture.friction_players = None
            elif friction_players == 1:
                fixture.friction_players = False
            elif friction_players == 2:
                fixture.friction_players = True

            fixture.restitution = buffer.read_float64()
            if fixture.restitution == 1.7976931348623157e+308:
                fixture.restitution = None

            fixture.density = buffer.read_float64()
            if fixture.density == 1.7976931348623157e+308:
                fixture.density = None

            fixture.color = buffer.read_uint32()
            fixture.death = buffer.read_bool()
            fixture.no_physics = buffer.read_bool()

            if bonk_map.version >= 11:
                fixture.no_grapple = buffer.read_bool()
            if bonk_map.version >= 12:
                fixture.inner_grapple = buffer.read_bool()
            bonk_map.physics.fixtures.append(fixture)

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
            body.force.force_x = buffer.read_float64()
            body.force.force_y = buffer.read_float64()
            body.force.torque = buffer.read_float64()
            body.force.is_relative = buffer.read_bool()
            body.shape.collide_group = buffer.read_int16()
            body.shape.collide_mask = CollideFlag.NONE
            if buffer.read_bool():
                body.shape.collide_mask = body.shape.collide_mask | CollideFlag.A
            if buffer.read_bool():
                body.shape.collide_mask = body.shape.collide_mask | CollideFlag.B
            if buffer.read_bool():
                body.shape.collide_mask = body.shape.collide_mask | CollideFlag.C
            if buffer.read_bool():
                body.shape.collide_mask = body.shape.collide_mask | CollideFlag.D
            if bonk_map.version >= 2 and buffer.read_bool():
                body.shape.collide_mask = body.shape.collide_mask | CollideFlag.PLAYERS
            if bonk_map.version >= 14:
                body.force_zone.enabled = buffer.read_bool()
                if body.force_zone.enabled:
                    body.force_zone.force = (buffer.read_float64(), buffer.read_float64())
                    body.force_zone.push_players = buffer.read_bool()
                    body.force_zone.push_bodies = buffer.read_bool()
                    body.force_zone.push_arrows = buffer.read_bool()
                    if bonk_map.version >= 15:
                        body.force_zone.type = ForceZoneType.from_id(buffer.read_int16())
                        body.force_zone.center = buffer.read_float64()
            fixtures_count = buffer.read_int16()
            for _ in range(fixtures_count):
                body.fixtures.append(buffer.read_int16())
            bonk_map.physics.bodies.append(body)
        # endregion
        # region Spawns
        spawn_count = buffer.read_int16()
        for _ in range(spawn_count):
            spawn = Spawn()
            spawn.position = (buffer.read_float64(), buffer.read_float64())
            spawn.velocity = (buffer.read_float64(), buffer.read_float64())
            spawn.priority = buffer.read_int16()
            spawn.red = buffer.read_bool()
            spawn.ffa = buffer.read_bool()
            spawn.blue = buffer.read_bool()
            spawn.green = buffer.read_bool()
            spawn.yellow = buffer.read_bool()
            spawn.name = buffer.read_utf()
            bonk_map.spawns.append(spawn)
        # endregion
        # region Capture zones
        cap_zone_count = buffer.read_int16()
        for _ in range(cap_zone_count):
            cap_zone = CaptureZone()
            cap_zone.name = buffer.read_utf()
            cap_zone.seconds = buffer.read_float64()
            cap_zone.shape_id = buffer.read_int16()
            if bonk_map.version >= 6:
                cap_zone.type = CaptureType.from_id(buffer.read_int16())
            bonk_map.cap_zones.append(cap_zone)
        # endregion
        # region Joints
        joint_count = buffer.read_int16()
        for _ in range(joint_count):
            joint_type_id = buffer.read_int16()
            if joint_type_id == 1:
                joint = RevoluteJoint()
                joint.from_angle = buffer.read_float64()
                joint.to_angle = buffer.read_float64()
                joint.turn_force = buffer.read_float64()
                joint.motor_speed = buffer.read_float64()
                joint.enable_limit = buffer.read_bool()
                joint.enable_motor = buffer.read_bool()
                joint.pivot = (buffer.read_float64(), buffer.read_float64())
            elif joint_type_id == 2:
                joint = DistanceJoint()
                joint.softness = buffer.read_float64()
                joint.damping = buffer.read_float64()
                joint.pivot = (buffer.read_float64(), buffer.read_float64())
                joint.attach = (buffer.read_float64(), buffer.read_float64())
            elif joint_type_id == 3:
                joint = LPJJoint()
                joint.position = (buffer.read_float64(), buffer.read_float64())
                joint.angle = buffer.read_float64()
                joint.force = buffer.read_float64()
                joint.pl = buffer.read_float64()
                joint.pu = buffer.read_float64()
                joint.length = buffer.read_float64()
                joint.speed = buffer.read_float64()
            elif joint_type_id == 4:
                joint = LSJJoint()
                joint.position = (buffer.read_float64(), buffer.read_float64())
                joint.force = buffer.read_float64()
                joint.length = buffer.read_float64()
            elif joint_type_id == 5:
                joint = GearJoint()
                joint.name = buffer.read_utf()
                joint.ratio = buffer.read_float64()
                joint.joint_a_id = buffer.read_int16()
                joint.joint_b_id = buffer.read_int16()
            else:
                raise ValueError(f'Invalid joint id: {joint_type_id}')
            if joint_type_id != 5:
                joint.shape_a_id = buffer.read_int16()
                joint.shape_b_id = buffer.read_int16()
                joint.col_attached = buffer.read_bool()
                joint.break_force = buffer.read_float64()
                joint.draw_line = buffer.read_bool()
            bonk_map.physics.joints.append(joint)
        # endregion

        return bonk_map
