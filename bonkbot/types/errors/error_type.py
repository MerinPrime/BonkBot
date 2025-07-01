import enum


class ErrorType(enum.Enum):
    """
    Enum of error codes.
    """

    # Bonk Errors

    RATE_LIMITED = ('ratelimited', 'rate_limit')
    '''
    You did something too fast.
    Possible reasons:
    * Changing password more than one in 24 hours
    * Sending friend request too fast
    May be another reasons.
    '''
    HOST_CHANGE_RATE_LIMITED = ('host change rate limited',)
    '''
    You are transferring host too quickly. Please wait before trying again.
    '''
    PASSWORD = ('password',)
    '''
    Invalid account password.
    '''
    USERNAME_INVALID = ('username_invalid', 'username_fail', 'invalid guest name')
    '''
    Invalid username. Possible reasons include:
    * Too short
    * Too long
    * Contains non-ASCII characters
    * Contains invalid characters (only letters, numbers, spaces, and underscores are allowed)
    * Starts with a space
    
    If this is an account name, additional reasons include:
    * Starts with a underscore
    * Contains multiple spaces in a row
    '''
    NOT_HOST = ('not_host',)
    '''
    Occurs when a non-host player attempts to:
    * Kick or ban another player
    * Change the player balance
    * Change the map
    * Change mode or rounds
    * Etc.
    '''
    INVALID_BALANCE = ('invalid_balance',)
    '''
    Trying to change balance of player to invalid.
    Balance should be in range [-100; 100]
    '''
    ROOM_NOT_FOUND = ('roomnotfound','room_not_found')
    '''
    Room not found.
    '''
    NEW_HOST_NOT_PRESENT = ('new_host_not_present',)
    '''
    New host not present in host transfer.
    '''
    AVATAR_DATA_INVALID = ('avatar_data_invalid',)
    '''
    Avatar data invalid.
    '''
    MAP_UNPUBLISHED = ('map_unpublished',)
    '''
    Couldn't unfavourite map because it isn't public.
    '''
    NOT_FAVED = ('not_faved',)
    '''
    This map isn't in your favourites
    '''

    # Custom Errors

    UNDEFINED = ('undefined',)
    '''
    Unknown error.
    '''

    USERNAME_MUST_BE_ASCII = ('username_must_be_ascii',)
    '''
    Username must contain only ASCII characters.
    '''
    USERNAME_TOO_SHORT = ('username_too_short')
    '''
    Username must be at least 2 characters long.
    '''
    USERNAME_TOO_LONG = ('username_too_long',)
    '''
    Username must be at most 15 characters long.
    '''
    USERNAME_INVALID_CHARS = ('username_invalid_chars',)
    '''
    Username may contain only letters, numbers, underscores, and spaces.
    '''
    USERNAME_INVALID_START = ('username_invalid_start',)
    '''
    Username cannot start with a space.
    For account usernames, underscores at the beginning are also not allowed.
    '''

    @staticmethod
    def from_string(code: str) -> 'ErrorType':
        for error_type in ErrorType:
            if code in error_type.value:
                return error_type
        print(f'Undefined error {code}.')
        return ErrorType.UNDEFINED
