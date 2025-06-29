import asyncio
from asyncio import AbstractEventLoop
from typing import TYPE_CHECKING

from bonkbot.core.bot import BonkBot
from bonkbot.types.errors import ApiError, ErrorType

if TYPE_CHECKING:
    from bonkbot.core.room import Room

'''
This example implements an XP farm.
For each account it starts a bot to farm XP.
'''

accounts = [
    ('name', 'password'),
]

RESTART_DELAY_SECONDS = 30
RATE_LIMIT_RESTART_DELAY_SECONDS = 600
XP_GAIN_INTERVAL_SECONDS = 10 # Interval to prevent rate limiting
XP_GAIN_CYCLE_SECONDS = 1000 # Need to be 1200 in total ( cycle + interval * 20 = 1200 )
CONNECTION_TIMEOUT_SECONDS = 15
XP_FARM_START_DELAY = 10 # Delay to prevent rate limiting

async def farming_loop(bot: 'BonkBot') -> None:
    await asyncio.sleep(XP_FARM_START_DELAY)
    print(f'Bot {bot.name} started XP Farm')
    while bot.is_logged:
        for _ in range(20):
            if not bot.is_logged or not bot.rooms:
                return
            await bot.rooms[0].gain_xp()
            await asyncio.sleep(XP_GAIN_INTERVAL_SECONDS)
        if bot.is_logged:
            await asyncio.sleep(XP_GAIN_CYCLE_SECONDS)


async def run_bot_lifecycle(name: str, password: str, event_loop: AbstractEventLoop) -> None:
    while True:
        bot = BonkBot(event_loop=event_loop)
        exception_future = event_loop.create_future()
        rate_limited = False
        remember_token = None
        
        try:
            @bot.event
            async def on_ready(bot: 'BonkBot') -> None:
                print(f'{bot.name}: Started with Level: {bot.level:.02f}, XP: {bot.xp}')
            
            @bot.event
            async def on_xp_gain(room: 'Room', xp: int) -> None:
                print(f'{room.bot.name}: Gained xp, Level: {room.bot.level:.02f}, XP: {room.bot.xp}')
            
            @bot.event
            async def on_room_disconnect(room: 'Room') -> None:
                nonlocal exception_future
                if not exception_future.done():
                    exception_future.set_exception(ConnectionAbortedError(f'{name}: Disconnected from room.'))
            
            @bot.event
            async def on_error(bot: 'BonkBot', err: Exception) -> None:
                nonlocal rate_limited, exception_future
                if not exception_future.done():
                    exception_future.set_exception(err)
            
            print(f'{name}: Trying to login')
            if remember_token is None:
                remember_token = await bot.login_with_password(name, password, remember=True)
            else:
                await bot.login_with_token(remember_token)
            
            print(f'{name}: Trying to create room')
            room = bot.create_room(f"{name}'s XP Farm", unlisted=True, max_players=1)
            await room.connect()

            connection_task = event_loop.create_task(room.wait_for_connection())

            done_conn, pending_conn = await asyncio.wait(
                [connection_task, exception_future],
                return_when=asyncio.FIRST_COMPLETED,
                timeout=CONNECTION_TIMEOUT_SECONDS,
            )
            
            if exception_future in done_conn:
                connection_task.cancel()
                exception_future.result()
            
            if not done_conn:
                for task in pending_conn:
                    task.cancel()
                raise asyncio.TimeoutError(f'{name}: Room creating timed out.')
            
            farming_task = asyncio.create_task(farming_loop(bot))
            done, pending = await asyncio.wait(
                [farming_task, exception_future],
                return_when=asyncio.FIRST_COMPLETED,
            )
            
            if exception_future in done:
                farming_task.cancel()
                exception_future.result()
            else:
                exception_future.cancel()
        except ApiError as e:
            if e.error_type == ErrorType.RATE_LIMITED:
                rate_limited = True
        except Exception as e:
            print(f'{name}: Thrown an error: {e}')
        finally:
            if bot.is_logged:
                print(f'{name}: Logged out.')
                await bot.logout()
            delay = RESTART_DELAY_SECONDS
            if rate_limited:
                delay = RATE_LIMIT_RESTART_DELAY_SECONDS
            print(f'{name}: Will restart in {delay} seconds')
            await asyncio.sleep(delay)

async def main() -> None:
    event_loop = asyncio.get_running_loop()
    
    print('--- Initializing bots lifecycle ---')
    lifecycles = [run_bot_lifecycle(name, password, event_loop) for name, password in accounts]
    
    print('--- Starting bots lifecycle ---')
    await asyncio.gather(*lifecycles)

if __name__ == '__main__':
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
            event_loop.run_until_complete(asyncio.gather(main_task, return_exceptions=True))
        print('--- XP farm stopped ---')
