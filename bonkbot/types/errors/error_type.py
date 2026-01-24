import enum
import logging


class ErrorType(enum.Enum):
    """
    Enum of error codes.
    """

    # Bonk Errors

    RATE_LIMITED = ('ratelimited', 'rate_limited', 'rate_limit')
    """
    You did something too fast.
    Possible reasons:
    * Changing password more than one in 24 hours
    * Sending friend request too fast
    May be another reasons.
    """
    RATE_LIMIT_PONG = ('rate_limit_pong',)
    """
    You sent the ping packet too quickly.
    """
    HOST_CHANGE_RATE_LIMITED = ('host change rate limited',)
    """
    You are transferring host too quickly. Please wait before trying again.
    """
    PASSWORD = ('password',)
    """
    Invalid account password.
    """
    USERNAME_INVALID = ('username_invalid', 'invalid guest name')
    """
    Invalid username. Possible reasons include:
    * Too short
    * Too long
    * Contains non-ASCII characters
    * Contains invalid characters (only letters, numbers, spaces, and underscores are allowed)
    * Starts with a space

    If this is an account name, additional reasons include:
    * Starts with a underscore
    * Contains multiple spaces in a row
    """
    NOT_HOST = ('not_host', 'not_hosting')
    """
    Occurs when a non-host player attempts to:
    * Kick or ban another player
    * Change the player balance
    * Change the map
    * Change mode or rounds
    * Etc.
    """
    INVALID_BALANCE = ('invalid_balance',)
    """
    Trying to change balance of player to invalid.
    Balance should be in range [-100; 100]
    """
    ROOM_NOT_FOUND = ('roomnotfound', 'room_not_found')
    """
    Room not found.
    """
    ROOM_FULL = ('room_full',)
    """
    Room is full.
    """
    ALREADY_IN_THIS_ROOM = ('already_in_this_room',)
    """
    Bot already in this room.
    """
    JOIN_RATE_LIMITED = ('join_rate_limited',)
    """
    TODO: Idk
    """
    PASSWORD_WRONG = ('password_wrong',)
    """
    Entered password is incorrect when joining a room.
    """
    NEW_HOST_NOT_PRESENT = ('new_host_not_present',)
    """
    New host not present in host transfer.
    """
    AVATAR_DATA_INVALID = ('avatar_data_invalid',)
    """
    Avatar data invalid.
    """
    MAP_UNPUBLISHED = ('map_unpublished', 'map_private')
    """
    Map is private, it must be published.
    """
    NOT_FAVED = ('not_faved',)
    """
    This map isn't in your favourites.
    """
    ALREADY_FAVED = ('already_faved',)
    """
    This map is already in your favourites.
    """
    USERNAME_TAKEN = ('username_taken',)
    """
    Username is already taken. ( Account registration )
    """
    DATA_MISSING = ('data_missing',)
    """
    Please enter both a username and password. ( Account registration )
    """
    PASSWORD_WEAK = ('password_weak',)
    """
    This password is too weak. Make it stronger. ( Account registration )
    """
    USERNAME_NOT_FOUND = ('username_fail', 'username_not_found')
    """
    No account with that username.
    """
    BANNED = ('banned',)
    """
    Account banned.
    """
    PASSWORD_INCORRECT = ('password',)
    """
    Password incorrect.
    """
    TOKEN = ('token',)
    """
    Please log out and in again and try again. ( Password changing )
    """
    SERVER_ERROR = ('server_error_1', 'server_error_2')
    """
    Please try again. ( Password changing )
    """
    OLD_PASSWORD_INCORRECT = ('oldpass_wrong',)
    """
    Old password is incorrect. ( Password changing )
    """
    CANT_FRIEND_SELF = ('cant_friend_self',)
    """
    Cant friend yourself.
    """
    ALREADY_FRIENDS = ('already_friends',)
    """
    You are already friends.
    """
    ALREADY_SENT_REQUEST = ('already_sent_request',)
    """
    You have already sent them a friend request.
    """
    NOT_LOGGED_IN = ('not_logged_in',)
    """
    You are guest.
    """
    INVALID_MAPID = ('invalid_mapid',)
    """
    Map issue.
    """
    INVALID_COMMENT = ('invalid_comment',)
    """
    Comment invalid.
    """
    COMMENT_TOO_LONG = ('comment_too_long',)
    """
    Comment too long.
    """
    INVALID_DBV = ('invalid_dbv',)
    """
    Map issue.
    """
    UNAUTHORISED = ('unauthorised',)
    """
    You dont have those privileges.
    """
    NO_CLIENT_ENTRY = ('no_client_entry',)
    """
    You tried to do an action, but you are not in a room.
    """
    INVALID_PARAMS = ('invalid_params',)
    """
    Invalid params?
    """
    PLAYERS_XP_TOO_HIGH = ('players_xp_too_high',)
    """
    Level higher than setted in room.
    """
    PLAYERS_XP_TOO_LOW = ('players_xp_too_low',)
    """
    Level lower than setted in room.
    """
    GUESTS_NOT_ALLOWED = ('guests_not_allowed',)
    """
    Level lower than setted in room.
    """

    # Custom Errors

    UNDEFINED = ('undefined',)
    """
    Unknown error.
    """

    USERNAME_MUST_BE_ASCII = ('username_must_be_ascii',)
    """
    Username must contain only ASCII characters.
    """
    USERNAME_TOO_SHORT = ('username_too_short',)
    """
    Username must be at least 2 characters long.
    """
    USERNAME_TOO_LONG = ('username_too_long',)
    """
    Username must be at most 15 characters long.
    """
    USERNAME_INVALID_CHARS = ('username_invalid_chars',)
    """
    Username may contain only letters, numbers, underscores, and spaces.
    """
    USERNAME_INVALID_START = ('username_invalid_start',)
    """
    Username cannot start with a space.
    For account usernames, underscores at the beginning are also not allowed.
    """

    ROOM_LINK_INVALID = ('room_link_invalid',)
    """
    Room link invalid.
    """

    @staticmethod
    def from_string(code: str) -> 'ErrorType':
        for error_type in ErrorType:
            if code in error_type.value:
                return error_type
        logging.getLogger(__name__).warning(f'Undefined error: {code}.')
        return ErrorType.UNDEFINED

