from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Union

from bonkbot.pson import ByteBuffer
from bonkbot.types.avatar.avatar import Avatar
from bonkbot.types.friend import Friend
from bonkbot.types.settings import Settings


@dataclass
class BotData:
    name: str = ''
    token: str = ''
    dbid: Union[int, None] = None
    xp: Union[int, None] = None
    avatar: Avatar = None
    active_avatar: int = 0
    avatars: List[Avatar] = field(default_factory=list)
    friends: List[Friend] = field(default_factory=list)
    legacy_friends: List[Friend] = field(default_factory=list)
    settings: Settings = None

    @staticmethod
    def from_login_response(json_data: dict) -> 'BotData':
        data = BotData()
        data.name = json_data['username']
        data.token = json_data['token']
        data.dbid = json_data['id']
        data.xp = json_data['xp']
        data.avatar = Avatar.from_buffer(ByteBuffer().from_base64(json_data['avatar'], uri_encoded=True))
        data.active_avatar = json_data['activeAvatarNumber']
        data.avatars = [
            Avatar.from_buffer(ByteBuffer().from_base64(json_data['avatar1'], uri_encoded=True)),
            Avatar.from_buffer(ByteBuffer().from_base64(json_data['avatar2'], uri_encoded=True)),
            Avatar.from_buffer(ByteBuffer().from_base64(json_data['avatar3'], uri_encoded=True)),
            Avatar.from_buffer(ByteBuffer().from_base64(json_data['avatar4'], uri_encoded=True)),
            Avatar.from_buffer(ByteBuffer().from_base64(json_data['avatar5'], uri_encoded=True))
        ]
        data.friends = [Friend(
            name=friend['name'],
            dbid=friend['id'],
            room_id=friend['roomid']
        ) for friend in json_data['friends']]
        data.legacy_friends = [Friend(name=friend, dbid=None, room_id=None) for friend in json_data['legacyFriends'].split('#')]
        data.settings = Settings.from_buffer(ByteBuffer().from_base64(json_data['controls'], uri_encoded=False))
        return data
