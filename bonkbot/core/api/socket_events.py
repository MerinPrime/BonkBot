import enum


class SocketEvents:
    class Incoming(enum.IntEnum):
        PING_DATA = 1
        ROOM_CREATE = 2
        ROOM_JOIN = 3
        PLAYER_JOIN = 4
        PLAYER_LEFT = 5
        HOST_LEFT = 6
        PLAYER_MOVE = 7
        READY_CHANGE = 8
        READY_RESET = 9
        PLAYER_MUTE = 10
        PLAYER_UNMUTE = 11
        PLAYER_NAME_CHANGE = 12
        GAME_END = 13
        GAME_START = 15
        STATUS = 16
        PLAYER_TEAM_CHANGE = 18
        TEAM_LOCK = 19
        MESSAGE = 20
        INFORM_IN_LOBBY = 21
        TIME_SYNC = 23
        KICK = 24
        MODE_CHANGE = 26
        ROUNDS_CHANGE = 27
        MAP_CHANGE = 29
        AFK_WARN = 32
        MAP_SUGGEST_HOST = 33
        MAP_SUGGEST_CLIENT = 34
        SET_BALANCE = 36
        TEAMS_TOGGLE = 39
        REPLAY_RECORD = 40
        HOST_CHANGE = 41
        FRIEND_REQUEST = 42
        COUNTDOWN = 43
        COUNTDOWN_ABORT = 44
        LEVEL_UP = 45
        XP_GAIN = 46
        INFORM_IN_GAME = 48
        ROOM_ID_OBTAIN = 49
        PLAYER_TABBED = 52
        ROOM_NAME_CHANGE = 58
        ROOM_PASS_CHANGE = 59

    class Outgoing(enum.IntEnum):
        PING_DATA = 1
        MOVE = 4
        GAME_START = 5
        SET_TEAM = 6
        SET_TEAM_LOCK = 7
        BAN = 9
        SEND_MESSAGE = 10
        INFORM_IN_LOBBY = 11
        CREATE_ROOM = 12
        JOIN_ROOM = 13
        SET_READY = 16
        RESET_READY = 17
        TIME_SYNC = 18
        SET_MODE = 20
        SET_ROUNDS = 21
        SET_BALANCE = 29
        SET_TEAM_STATE = 32
        RECORD_REPLAY = 33
        GIVE_HOST = 34
        FRIEND_REQUEST = 35
        XP_GAIN = 38
        SET_TABBED = 44
        END_ROOM = 50
        CHANGE_ROOM_NAME = 52
        CHANGE_ROOM_PASS = 53
