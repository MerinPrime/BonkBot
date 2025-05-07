from dataclasses import dataclass

from .map_metadata import MapMetadata
from .map_properties import MapProperties


class Map:
    version: int = 1
    metadata: MapMetadata
    properties: MapProperties