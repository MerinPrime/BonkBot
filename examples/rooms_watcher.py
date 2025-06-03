import asyncio

from bonkbot.core.bot import BonkAPI
from bonkbot.types import Mode

'''
This example implements a room watcher.
It monitors all active rooms and logs only available VTOL rooms.
I use BonkAPI instead of BonkBot because we need only an API without the need for room joining.
'''

bonk_api = BonkAPI()

async def main() -> None:
    print('Rooms watcher started')

    previous_rooms = set()
    while True:
        current_rooms = await bonk_api.fetch_rooms()
        current_rooms = {
            room for room in current_rooms
            if room.mode == Mode.VTOL
               and room.players < room.max_players
               and not room.has_password
        }
        new_rooms = current_rooms - previous_rooms
        for room in new_rooms:
            print(f'New VTOL room: {room.name}')
        previous_rooms = current_rooms
        await asyncio.sleep(30)

bonk_api.event_loop.run_until_complete(main())
