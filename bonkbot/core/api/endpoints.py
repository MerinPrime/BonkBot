from typing import Optional, final


@final
class Endpoints:
    BASE_URL = 'https://bonk2.io'
    SCRIPTS = f'{BASE_URL}/scripts'

    LOGIN_LEGACY = f'{SCRIPTS}/login_legacy.php'
    LOGIN_AUTO = f'{SCRIPTS}/login_auto.php'
    GET_ROOMS = f'{SCRIPTS}/getrooms.php'
    GET_FRIENDS = f'{SCRIPTS}/friends.php'
    GET_MATCHMAKING_SERVER = f'{SCRIPTS}/matchmaking_query.php'
    GET_ROOM_ADDRESS = f'{SCRIPTS}/getroomaddress.php'
    GET_OWN_MAPS = f'{SCRIPTS}/map_getown.php'
    AUTO_JOIN = f'{SCRIPTS}/autojoin.php'

    @staticmethod
    def socket_api(server_id: str) -> str:
        return f'https://{server_id}.bonk.io'

    @staticmethod
    def peer_api(server_id: str) -> str:
        return f'{server_id}.bonk.io'

    @staticmethod
    def room_link(room_id: str, bypass: Optional[str] = None) -> str:
        code = room_id
        if bypass is not None:
            code += bypass
        return f'https://bonk.io/{code}'
