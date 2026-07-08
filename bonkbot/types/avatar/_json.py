from typing import List, Optional

from typing_extensions import TypedDict


class LayerJson(TypedDict):
    id: int
    scale: float
    angle: float
    x: float
    y: float
    flipX: bool
    flipY: bool
    color: int


class AvatarJson(TypedDict):
    bc: int  # base_color
    layers: List[Optional[LayerJson]]
