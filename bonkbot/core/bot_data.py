from dataclasses import dataclass, field
from typing import List

from ..pson.bytebuffer import ByteBuffer
from ..types.avatar.avatar import Avatar
from ..types.friend import Friend
from ..types.settings import Settings


@dataclass
class BotData:
    name: str = ''
    token: str = ''
    id: int = 0
    is_guest: bool = True
    xp: int = 0
    active_avatar: int = 0
    avatar: Avatar = field(default_factory=Avatar)
    avatars: List[Avatar] = field(default_factory=lambda: [Avatar() for _ in range(5)])
    friends: List[Friend] = field(default_factory=list)
    legacy_friends: List[Friend] = field(default_factory=list)
    settings: Settings = field(default_factory=Settings)

    @staticmethod
    def from_login_response(json_data: dict) -> 'BotData':
        data = BotData(
            name = json_data['username'],
            token = json_data['token'],
            id = json_data['id'],
            xp = json_data['xp'],
            active_avatar = json_data['activeAvatarNumber'],
            is_guest = False,
        )

        if 'avatar' in json_data:
            data.avatar = Avatar.from_buffer(ByteBuffer().from_base64(json_data['avatar'], uri_encoded=True))

        for i in range(5):
            key = f'avatar{i+1}'
            if key in json_data:
                data.avatars[i] = Avatar.from_buffer(ByteBuffer().from_base64(json_data[key], uri_encoded=True))

        if 'friends' in json_data:
            for friend_data in json_data['friends']:
                data.friends.append(Friend(
                    name=friend_data['name'],
                    dbid=friend_data['id'],
                    room_id=friend_data['roomid'],
                ))

        if 'legacyFriends' in json_data:
            for friend_name in json_data['legacyFriends'].split('#'):
                data.legacy_friends.append(Friend(name=friend_name, dbid=None, room_id=None))

        if 'controls' in json_data and json_data['controls'] != False:
            data.settings = Settings.from_buffer(ByteBuffer().from_base64(json_data['controls'], uri_encoded=False))

        return data
