from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .capture_zone import CaptureZone
    from .map_metadata import MapMetadata
    from .map_properties import MapProperties
    from .physics.map_physics import MapPhysics
    from .spawn import Spawn


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/map/types/IMap.ts
class Map:
    version: int
    metadata: 'MapMetadata'
    properties: 'MapProperties'
    physics: 'MapPhysics'
    spawns: List['Spawn']
    cap_zones: List['CaptureZone']
