import asyncio
from typing import TYPE_CHECKING

from bonkbot.core.bot import BonkBot
from bonkbot.types import Inputs, Mode

if TYPE_CHECKING:
    from bonkbot.core.room import Player, Room
    from bonkbot.types import PlayerMove

"""
This example implements a MirrorBot.
The bot copies inputs of players like mirror.
VTOL, Arrows and Death Arrows can cause an "unmirror".
"""


class MirrorBot(BonkBot):
    async def on_ready(self, bot: 'BonkBot') -> None:
        print('MirrorBot started')
        await self.update_server()
        room = self.create_room(name='MirrorBot', unlisted=True)
        await room.connect()
        await room.wait_for_connection()
        print(f'Link: {room.join_link}')

    async def on_player_join(self, room: 'Room', player: 'Player') -> None:
        if not room.bot_player.is_host:
            return
        await asyncio.sleep(5)
        if player.is_left:
            return
        await player.give_host()

    async def on_host_left(
        self,
        room: 'Room',
        old_host: 'Player',
        new_host: 'Player',
        timestamp: int,
    ) -> None:
        if not new_host.is_bot:
            return
        if room.players_count == 1:
            return
        await asyncio.sleep(5)
        for player in room.players:
            if player.is_bot or player.is_left:
                continue
            await player.give_host()
            break

    async def on_player_move(
        self,
        room: 'Room',
        player: 'Player',
        move: 'PlayerMove',
    ) -> None:
        frame = move.frame
        inputs = move.inputs
        right = inputs.right
        left = inputs.left
        if right and left:
            if room.mode not in [Mode.ARROWS, Mode.DEATH_ARROWS, Mode.VTOL]:
                right = True
                left = True
        elif right:
            right = False
            left = True
        elif left:
            right = True
            left = False
        mirrored_inputs = Inputs(
            left,
            right,
            inputs.up,
            inputs.down,
            inputs.heavy,
            inputs.special,
        )
        await room.move(frame, mirrored_inputs)

    async def on_move_revert(
        self,
        room: 'Room',
        player: 'Player',
        move: 'PlayerMove',
    ) -> None:
        candidates = [
            bot_move
            for bot_move in room.bot_player.moves.values()
            if bot_move.frame < move.frame
        ]
        if not candidates:
            last_inputs = Inputs()
            sequence = None
        else:
            last_move = max(candidates, key=lambda move: move.frame)
            last_inputs = last_move.inputs
            sequence = last_move.sequence
        await room.move(move.frame, last_inputs, sequence)


bot = MirrorBot()
bot.event_loop.run_until_complete(bot.login_as_guest('MirrorBot'))
bot.event_loop.run_forever()
