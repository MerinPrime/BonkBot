from typing import List, Optional, cast, final

from attrs import define, field


@define(slots=True, auto_attribs=True, frozen=True)
class Server:
    name: str = field()
    latitude: Optional[float] = field()
    longitude: Optional[float] = field()
    country: Optional[str] = field()


@final
class ServerList:
    WARSAW = Server('b2warsaw1', 52.2370, 21.0175, 'PL')
    PARIS = Server('b2paris1', 48.8647, 2.3490, 'FR')
    STOCKHOLM = Server('b2stockholm1', 59.3346, 18.0632, 'SE')
    FRANKFURT = Server('b2frankfurt1', 50.1109, 8.6821, 'DE')
    AMSTERDAM = Server('b2amsterdam1', 52.3779, 4.8970, 'NL')
    LONDON = Server('b2london1', 51.5098, -0.1180, 'UK')
    SEOUL = Server('b2seoul1', 37.5326, 127.0246, 'KR')
    SEATTLE = Server('b2seattle1', 47.6080, -122.3352, 'US')
    SAN_FRANCISCO = Server('b2sanfrancisco1', 37.7740, -122.4312, 'US')
    MISSISSIPPI = Server('b2river1', 35.5147, -89.9125, 'US')
    DALLAS = Server('b2dallas1', 32.7792, -96.8089, 'US')
    NEW_YORK = Server('b2ny1', 40.7306, -73.9352, 'US')
    ATLANTA = Server('b2atlanta1', 33.7537, -84.3863, 'US')
    SYDNEY = Server('b2sydney1', -33.8651, 151.2099, 'AU')
    BRAZIL = Server('b2brazil1', -22.9083, -43.1963, 'BR')

    @classmethod
    def all(cls) -> List['Server']:
        values = cast('List[object]', list(cls.__dict__.values()))
        return [v for v in values if isinstance(v, Server)]

    @classmethod
    def from_name(cls, name: str) -> Server:
        for s in cls.all():
            if s.name == name:
                return s
        return Server(name, None, None, None)
