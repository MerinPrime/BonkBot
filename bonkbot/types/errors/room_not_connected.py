from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...core.room import Room


class RoomNotRunning(Exception):
    def __init__(self, room: 'Room'):
        self.room = room
        super().__init__(f"Room '{room.name}' is not running.")
