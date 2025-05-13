import asyncio

from bonkbot.core.bonkbot import BonkBot
from bonkbot.types import Mode

'''
This example implements a room watcher.
The bot monitors all active rooms and logs only available VTOL rooms.
Using class inheriting to events.
'''

class RoomsWatcherBot(BonkBot):
    async def on_ready(self, bot: 'BonkBot') -> None:
        print('Rooms watcher started')

        previous_rooms = set()
        while True:
            current_rooms = await self.fetch_rooms()
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


bot = RoomsWatcherBot()
bot.event_loop.run_until_complete(bot.login_as_guest('Kalalak'))
