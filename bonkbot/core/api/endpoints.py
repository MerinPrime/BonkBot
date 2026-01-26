from typing import Optional


class Endpoints:
    BASE_URL: str = 'https://bonk2.io'
    SCRIPTS: str = f'{BASE_URL}/scripts'

    LOGIN_LEGACY: str = f'{SCRIPTS}/login_legacy.php'
    LOGIN_AUTO: str = f'{SCRIPTS}/login_auto.php'
    GET_ROOMS: str = f'{SCRIPTS}/getrooms.php'
    GET_FRIENDS: str = f'{SCRIPTS}/friends.php'
    GET_MATCHMAKING_SERVER: str = f'{SCRIPTS}/matchmaking_query.php'
    GET_ROOM_ADDRESS: str = f'{SCRIPTS}/getroomaddress.php'
    GET_OWN_MAPS: str = f'{SCRIPTS}/map_getown.php'
    AUTO_JOIN: str = f'{SCRIPTS}/autojoin.php'

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

