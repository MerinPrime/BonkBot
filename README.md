# BonkBot
Inspired by [bonk_bot](https://github.com/Zuzunito/bonk_bot)  
User-friendly async python framework for writing bots in bonk.io.  
Supported python versions: 3.8+

## Features
- `async`/`await` based API for concurrent connection and request management.
- Support for different bonk.io servers.
- Flexible event handling system using decorators (`@bot.event`) or class inheritance (`BonkBot`).
- Enhanced network performance.
- Support for peer connections and time synchronization.

## Installing
### Using PyPI
Package is currently unavailable on PyPI.
### From github
```bash
pip install https://github.com/MerinPrime/BonkBot.git
```

## Bot examples
- [Rooms Watcher ( Decorators )](examples/rooms_watcher.py)
- [Rooms Watcher ( Class based )](examples/oop_rooms_watcher.py)
- [XP Farm](examples/xp_farm.py)
- [MirrorBot](examples/mirror_bot.py)

## Documentation
In the future i want to write docstrings but idk what i should to write in them
