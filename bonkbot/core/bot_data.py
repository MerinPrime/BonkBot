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
    avatar: Avatar = None
    active_avatar: int = 0
    avatars: List[Avatar] = field(default_factory=list)
    friends: List[Friend] = field(default_factory=list)
    legacy_friends: List[Friend] = field(default_factory=list)
    settings: Settings = None

    @staticmethod
    def from_login_response(json_data: dict) -> 'BotData':
        data = BotData(
            name = json_data['username'],
            token = json_data['token'],
            id= json_data['id'],
            is_guest = False,
            xp = json_data['xp'],
            avatar = Avatar.from_buffer(ByteBuffer().from_base64(json_data['avatar'], uri_encoded=True)),
            active_avatar = json_data['activeAvatarNumber'],
            avatars = [
                Avatar.from_buffer(ByteBuffer().from_base64(json_data['avatar1'], uri_encoded=True)),
                Avatar.from_buffer(ByteBuffer().from_base64(json_data['avatar2'], uri_encoded=True)),
                Avatar.from_buffer(ByteBuffer().from_base64(json_data['avatar3'], uri_encoded=True)),
                Avatar.from_buffer(ByteBuffer().from_base64(json_data['avatar4'], uri_encoded=True)),
                Avatar.from_buffer(ByteBuffer().from_base64(json_data['avatar5'], uri_encoded=True))
            ],
            friends = [Friend(
                name=friend['name'],
                dbid=friend['id'],
                room_id=friend['roomid']
            ) for friend in json_data['friends']],
            legacy_friends = [Friend(name=friend, dbid=None, room_id=None) for friend in json_data['legacyFriends'].split('#')],
            settings = Settings.from_buffer(ByteBuffer().from_base64(json_data['controls'], uri_encoded=False)) if json_data['controls'] else Settings()
        )
        return data
