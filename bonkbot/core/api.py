import enum

PROTOCOL_VERSION = 49
MAP_VERSION = 49
login_legacy_api = 'https://bonk2.io/scripts/login_legacy.php'
login_auto_api = 'https://bonk2.io/scripts/login_auto.php'
get_rooms_api = 'https://bonk2.io/scripts/getrooms.php'
get_server_api = 'https://bonk2.io/scripts/matchmaking_query.php'
bonk_socket_api = 'https://{}.bonk.io'
bonk_peer_api = '{}.bonk.io'
room_link_api = 'https://bonk.io/{}{}'

class SocketEvents:
    class Incoming(enum.IntEnum):
        PING_DATA = 1
        ROOM_CREATE = 2
        ROOM_JOIN = 3
        PLAYER_JOIN = 4
        PLAYER_LEFT = 5
        HOST_LEFT = 6
        PLAYER_INPUT = 7
        READY_CHANGE = 8
        GAME_END = 13
        GAME_START = 15
        STATUS = 16
        LEVEL_UP = 45
        XP_GAIN = 46
        ROOM_ID_OBTAIN = 49

    class Outgoing(enum.IntEnum):
        PING_DATA = 1
        BAN = 9
        INFORM_IN_LOBBY = 11
        CREATE_ROOM = 12
        SET_BALANCE = 29
        GIVE_HOST = 34
        FRIEND_REQUEST = 35
        XP_GAIN = 38

RATE_LIMIT_PONG = 'rate_limit_pong'
CRITICAL_API_ERRORS = [
    'room_not_found',
    'room_full',
    'banned',
    'no_client_entry',
    'already_in_this_room',
    'join_rate_limited',
    'password_wrong',
    'invalid_params',
    'players_xp_too_high',
    'players_xp_too_low',
    'guests_not_allowed',
    'avatar_data_invalid',
]
