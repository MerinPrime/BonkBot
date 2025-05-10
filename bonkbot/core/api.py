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
        READY_RESET = 9
        PLAYER_MUTED = 10
        PLAYER_UNMUTED = 11
        PLAYER_NAME_CHANGE = 12
        GAME_END = 13
        GAME_START = 15
        STATUS = 16
        PLAYER_TEAM_CHANGE = 18
        TEAM_LOCK = 19
        MESSAGE = 20
        INFORM_IN_LOBBY = 21
        ON_KICK = 24
        MODE_CHANGE = 26
        ROUNDS_CHANGE = 27
        MAP_CHANGE = 29
        AFK_WARN = 32
        LEVEL_UP = 45
        XP_GAIN = 46
        ROOM_ID_OBTAIN = 49

    class Outgoing(enum.IntEnum):
        PING_DATA = 1
        MOVE = 4
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
PSON_KEYS = ['physics', 'shapes', 'fixtures', 'bodies', 'bro', 'joints', 'ppm', 'lights', 'spawns', 'lasers', 'capZones', 'type', 'w', 'h', 'c', 'a', 'v', 'l', 's', 'sh', 'fr', 're', 'de', 'sn', 'fc', 'fm', 'f', 'd', 'n', 'bg', 'lv', 'av', 'ld', 'ad', 'fr', 'bu', 'cf', 'rv', 'p', 'd', 'bf', 'ba', 'bb', 'aa', 'ab', 'axa', 'dr', 'em', 'mmt', 'mms', 'ms', 'ut', 'lt', 'New body', 'Box Shape', 'Circle Shape', 'Polygon Shape', 'EdgeChain Shape', 'priority', 'Light', 'Laser', 'Cap Zone', 'BG Shape', 'Background Layer', 'Rotate Joint', 'Slider Joint', 'Rod Joint', 'Gear Joint', 65535, 16777215]
