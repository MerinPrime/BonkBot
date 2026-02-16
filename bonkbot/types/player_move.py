from attr import define, field

from .input import Inputs


@define(slots=True, auto_attribs=True, frozen=True)
class PlayerMove:
    frame: int = 0
    inputs: 'Inputs' = field(factory=Inputs)
    sequence: int = 0
    time: float = 0
    by_socket: bool = False
    by_peer: bool = False
    reverted: bool = False
    unreverted: bool = False
    peer_ignored: bool = False

    @property
    def valid(self) -> bool:
        return not self.reverted or (self.reverted and self.unreverted)
