from dataclasses import dataclass, field

from .input import Inputs


@dataclass
class PlayerMove:
    frame: int = 0
    inputs: Inputs = field(default_factory=Inputs)
    sequence: int = 0
    time: float = 0
    by_socket: bool = False
    by_peer: bool = False
    reverted: bool = False
    unreverted: bool = False
    peer_ignored: bool = False

    def to_json(self) -> dict:
        return {
            'f': self.frame,
            'i': self.inputs.flags,
            'c': self.sequence,
        }
