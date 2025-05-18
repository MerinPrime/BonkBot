import asyncio
from typing import TYPE_CHECKING

from bonkbot.core.bot.bot import BonkBot
from bonkbot.types import Inputs

if TYPE_CHECKING:
    from bonkbot.core import Room
    from bonkbot.core.player import Player
    from bonkbot.types.player_move import PlayerMove

'''
This example implements a MirrorBot.
The bot copies inputs of players like mirror.
Modes like VTOL and Arrows can cause an "unmirror".
'''

class MirrorBot(BonkBot):
    def __init__(self) -> None:
        event_loop = asyncio.get_event_loop()
        super().__init__(event_loop)
        self.room = None

    async def on_ready(self, bot: 'BonkBot') -> None:
        print('MirrorBot started')
        await self.update_server()
        self.room = bot.create_room(name='MirrorBot', unlisted=True)
        await self.room.connect()
        await self.room.wait_for_connection()
        print(f'Link: {self.room.join_link}')

    async def on_player_join(self, room: 'Room', player: 'Player') -> None:
        if room.bot_player.is_host:
            await asyncio.sleep(2)
            await player.give_host()

    async def on_host_left(self, room: 'Room', player: 'Player') -> None:
        if room.bot_player.is_host:
            await asyncio.sleep(2)
            if room.player_count == 1:
                return
            for player in room.players:
                if player.is_bot:
                    continue
                await player.give_host()
                break

    async def on_player_move(self, room: 'Room', player: 'Player', move: 'PlayerMove') -> None:
        frame = move.frame
        inputs = move.inputs
        right = inputs.right
        left = inputs.left
        if right and left:
            inputs.right = True
            inputs.left = False
        elif right:
            inputs.right = False
            inputs.left = True
        elif left:
            inputs.right = True
            inputs.left = False
        await room.move(frame, inputs)

    async def on_move_revert(self, room: 'Room', player: 'Player', move: 'PlayerMove') -> None:
        candidates = [s for s in room.bot_player.moves if s < move.sequence]
        if not candidates:
            last_inputs = Inputs()
            sequence = None
        else:
            closest_key = max(candidates)
            last_move = room.bot_player.moves[closest_key]
            last_inputs = last_move.inputs
            sequence = last_move.sequence
        await room.move(move.frame, last_inputs, sequence)



bot = MirrorBot()
bot.event_loop.run_until_complete(bot.login_as_guest('MirrorBot'))
bot.event_loop.run_forever()
