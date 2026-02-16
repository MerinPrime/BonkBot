class BotNotLoggedInError(Exception):
    def __init__(self) -> None:
        super().__init__('Bot not logged in.')
