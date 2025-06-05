from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...core.room.room import Room


class RoomAlreadyConnected(Exception):
    def __init__(self, room: 'Room'):
        self.room = room
        super().__init__(f"Room '{room.name}' already connected.")
