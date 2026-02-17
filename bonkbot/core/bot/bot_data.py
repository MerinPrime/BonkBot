from typing import Any, Dict, List, Optional

from attrs import define, field

from ...pson.bytebuffer import ByteBuffer
from ...types.avatar.avatar import Avatar
from ...types.friend import Friend
from ...types.settings import Settings


@define(slots=True, auto_attribs=True)
class BotData:
    name: str
    token: Optional[str] = None
    remember_token: Optional[str] = None
    is_guest: bool = True
    id: int = 0
    xp: int = 0
    avatars: List['Avatar'] = field(factory=lambda: [Avatar() for _ in range(5)])
    active_avatar: 'Avatar' = field(factory=Avatar)
    active_avatar_id: int = 0
    bonk_v1_friends: List['Friend'] = field(factory=list)
    bonk_v2_friends: List['Friend'] = field(factory=list)
    friends: List['Friend'] = field(factory=list)
    settings: Optional['Settings'] = None

    @staticmethod
    def from_login_response(json_data: Dict[str, Any]) -> 'BotData':
        avatar = (
            Avatar.from_base64(json_data['avatar'])
            if 'avatar' in json_data
            else Avatar()
        )

        avatars: list[Avatar] = []
        for i in range(5):
            key = f'avatar{i + 1}'
            if key in json_data:
                avatars.append(Avatar.from_base64(json_data[key]))
            else:
                avatars.append(Avatar())

        bonk_v2_friends = [
            Friend(
                name=friend_data['name'],
                dbid=friend_data['id'],
                room_id=friend_data['roomid'],
            )
            for friend_data in json_data.get('friends', [])
        ]

        bonk_v1_friends = [
            Friend(name=name, dbid=None, room_id=None)
            for name in json_data.get('legacyFriends', '').split('#')
            if name
        ]

        friends = bonk_v2_friends + bonk_v1_friends

        settings = (
            Settings.from_base64(json_data['controls'])
            if json_data.get('controls')
            else None
        )

        return BotData(
            name=json_data['username'],
            token=json_data['token'],
            remember_token=json_data.get('remember_token'),
            is_guest=False,
            id=int(json_data['id']),
            xp=int(json_data['xp']),
            active_avatar=avatar,
            avatars=avatars,
            active_avatar_id=json_data['activeAvatarNumber'],
            bonk_v2_friends=bonk_v2_friends,
            bonk_v1_friends=bonk_v1_friends,
            friends=friends,
            settings=settings
        )
