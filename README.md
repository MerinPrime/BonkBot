# BonkBot
**A user-friendly and performant Python framework for creating Bonk.io bots.**  
Inspired by [bonk_bot](https://github.com/Zuzunito/bonk_bot)  

## Features
* **Async Architecture:** Built on `asyncio` for high-performance, concurrent connection management and responsive event handling.
* **Simplified API:** Write bots easily using intuitive event decorators (`@bot.event`) or class-based inheritance.
* **Optimized Network:** Enhanced network layer designed for stability and speed.
* **Advanced Networking:** Support for peer connections and precise time synchronization.
* **User-Friendly:** Designed with developer experience in mind, abstracting away low-level network complexities.

## Supported Python Versions

Requires Python 3.8 or newer.

## Status & Roadmap
* **Current Status (Beta):** The core framework providing connection, event handling, and basic game interactions is implemented.
* **Pending Features:** Some features, such as specific methods like `fetch_friends`, are not yet implemented, but are planned for future releases.

Report any issues or suggest new features on the [GitHub Issues page](https://github.com/MerinPrime/BonkBot/issues).

## Installation

[//]: # (### Using PyPI &#40; Recommended &#41;)
[//]: # (```bash)
[//]: # ()
[//]: # (```)
### From github
```bash
pip install git+https://github.com/MerinPrime/BonkBot.git
```
> PyPI distribution is planned for the future.

## Examples
* [Rooms Watcher (API)](examples/rooms_watcher.py)
* [Rooms Watcher (Class based)](examples/oop_rooms_watcher.py)
* [XP Farm](examples/xp_farm.py)
* [Mirror Bot](examples/mirror_bot.py)

## Documentation
Documentation is currently planned.  
Docstrings will be added to cover all public APIs.  
Your contributions and suggestions for documentation are welcome via [GitHub Issues page](https://github.com/MerinPrime/BonkBot/issues).
