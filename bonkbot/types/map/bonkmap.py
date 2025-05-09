from dataclasses import field
from typing import TYPE_CHECKING, List

from ...pson import ByteBuffer

if TYPE_CHECKING:
    from .capture_zone import CaptureZone
    from .map_metadata import MapMetadata
    from .map_properties import MapProperties
    from .physics.map_physics import MapPhysics
    from .spawn import Spawn


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IMap.ts
class BonkMap:
    version: int = 1
    metadata: 'MapMetadata' = field(default_factory=MapMetadata)
    properties: 'MapProperties' = field(default_factory=MapProperties)
    physics: 'MapPhysics' = field(default_factory=MapPhysics)
    spawns: List['Spawn'] = field(default_factory=list)
    cap_zones: List['CaptureZone'] = field(default_factory=list)

    @classmethod
    def decode(cls, buffer: ByteBuffer):
        pass
