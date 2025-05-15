

class BotNotLoggedInError(Exception):
    def __init__(self) -> None:
        super().__init__('Trying to get BonkBot.data when bot not logged in.')
