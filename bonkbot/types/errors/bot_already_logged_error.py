

class BotAlreadyLoggedInError(Exception):
    def __init__(self) -> None:
        super().__init__('Bot already logged in.')
