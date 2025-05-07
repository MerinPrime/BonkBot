from dataclasses import dataclass


@dataclass(frozen=True)
class RoomJoinParams:
    room_id: int
    password: str = ''
    bypass: str = ''
