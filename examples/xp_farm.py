import asyncio

from bonkbot.core import Room
from bonkbot.core.bonkbot import BonkBot

accounts = [('name', 'password')]

async def main():
    event_loop = asyncio.get_running_loop()
    bots = [BonkBot(event_loop=event_loop) for _ in accounts]

    print('--- Initializing bots ---')
    login_tasks = []

    for account, bot in zip(accounts, bots):
        name, password = account

        @bot.event
        async def on_ready(bot: BonkBot):
            print(f'Bot started: {bot.name}, Level: {bot.level:.02f}, XP: {bot.xp}')

        @bot.event
        async def on_xp_gain(room: Room, xp: int):
            print(f'Bot: {room.bot.name}, Level: {room.bot.level:.02f}, XP: {room.bot.xp}')

        @bot.event
        async def on_error(bot: BonkBot, error: Exception):
            print(f'Bot: {bot.name}, Error: {error}')

        login_tasks.append(bot.login_with_password(name, password))

    await asyncio.gather(*login_tasks)


    print('--- Creating rooms ---')
    rooms = []
    connect_tasks = []

    for bot in bots:
        room = bot.create_room(name='XP Farm', unlisted=True, max_players=1)
        rooms.append(room)
        connect_tasks.append(room.connect())

    await asyncio.gather(*connect_tasks)


    print('--- Wait to rooms connection ---')
    await asyncio.gather(*[room.wait_for_connection() for room in rooms])


    print('--- Started XP farm ---')
    while True:
        for _ in range(20):
            gain_xp_tasks = [room.gain_xp() for room in rooms]
            await asyncio.gather(*gain_xp_tasks)
            await asyncio.sleep(5)
        await asyncio.sleep(20 * 55)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("XP Farming stopped.")
