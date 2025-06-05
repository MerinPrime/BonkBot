import asyncio
from typing import TYPE_CHECKING

from bonkbot.core.bot import BonkBot

if TYPE_CHECKING:
    from bonkbot.core.room import Room

'''
This example implements an XP farm.
For each account it starts a bot to farm XP.
'''

accounts = [
    ('name', 'password'),
]

async def main() -> None:
    event_loop = asyncio.get_running_loop()
    bots = [BonkBot(event_loop=event_loop) for _ in accounts]

    print('--- Initializing bots ---')
    login_tasks = []

    for account, bot in zip(accounts, bots):
        name, password = account

        @bot.event
        async def on_ready(bot: 'BonkBot') -> None:
            print(f'Bot started: {bot.name}, Level: {bot.level:.02f}, XP: {bot.xp}')

        @bot.event
        async def on_xp_gain(room: 'Room', xp: int) -> None:
            print(f'Bot: {room.bot.name}, Level: {room.bot.level:.02f}, XP: {room.bot.xp}')

        @bot.event
        async def on_error(bot: 'BonkBot', error: Exception) -> None:
            # bot.name is not available if bot is not logged in
            if not bot.is_logged:
                print(f'Error: {error}')
                bots.remove(bot)
            else:
                print(f'Bot: {bot.name}, Error: {error}')

        login_tasks.append(bot.login_with_password(name, password))

    await asyncio.gather(*login_tasks)


    print('--- Creating rooms ---')
    connect_tasks = []

    for bot in bots:
        room = bot.create_room(name='XP Farm', unlisted=True, max_players=1)
        connect_tasks.append(room.connect())

    await asyncio.gather(*connect_tasks)


    print('--- Wait to rooms connection ---')
    await asyncio.gather(*[bot.wait_for_connection() for bot in bots])


    print('--- Started XP farm ---')
    await asyncio.sleep(10)
    while True:
        for _ in range(20):
            gain_xp_tasks = []
            for bot in bots.copy():
                if not bot.rooms:
                    print(f'Bot logged out: {bot.name}')
                    await bot.logout()
                if not bot.is_logged:
                    bots.remove(bot)
                    continue
                gain_xp_tasks.append(bot.rooms[0].gain_xp())
            await asyncio.gather(*gain_xp_tasks)
            await asyncio.sleep(10)
        if not bots:
            print('--- No bots available  ---')
            break
        await asyncio.sleep(1000)

event_loop = asyncio.get_event_loop()
main_task = None
try:
    main_task = event_loop.create_task(main())
    event_loop.run_until_complete(main_task)
except KeyboardInterrupt:
    print('KeyboardInterrupt')
finally:
    if main_task and not main_task.done():
        main_task.cancel()
    print('XP farm stopped.')
