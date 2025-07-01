import enum
from dataclasses import dataclass

from attrs.setters import frozen
from attrs import define, field

from build.lib.bonkbot.utils.validation import validate_str, validate_float


@define
class ServerInfo:
    name: str = field(validator=validate_str(), on_setattr=frozen)
    latitude: float = field(validator=validate_float(), on_setattr=frozen)
    longitude: float = field(validator=validate_float(), on_setattr=frozen)
    country: str = field(validator=validate_str(), on_setattr=frozen)


class Server(enum.Enum):
    WARSAW = ServerInfo('b2warsaw1', 52.2370, 21.0175, 'PL')
    PARIS = ServerInfo('b2paris1', 48.8647, 2.3490, 'FR')
    STOCKHOLM = ServerInfo('b2stockholm1', 59.3346, 18.0632, 'SE')
    FRANKFURT = ServerInfo('b2frankfurt1', 50.1109, 8.6821, 'DE')
    AMSTERDAM = ServerInfo('b2amsterdam1', 52.3779, 4.8970, 'NL')
    LONDON = ServerInfo('b2london1', 51.5098, -0.1180, 'UK')
    SEOUL = ServerInfo('b2seoul1', 37.5326, 127.0246, 'KR')
    SEATTLE = ServerInfo('b2seattle1', 47.6080, -122.3352, 'US')
    SAN_FRANCISCO = ServerInfo('b2sanfrancisco1', 37.7740, -122.4312, 'US')
    MISSISSIPPI = ServerInfo('b2river1', 35.5147, -89.9125, 'US')
    DALLAS = ServerInfo('b2dallas1', 32.7792, -96.8089, 'US')
    NEW_YORK = ServerInfo('b2ny1', 40.7306, -73.9352, 'US')
    ATLANTA = ServerInfo('b2atlanta1', 33.7537, -84.3863, 'US')
    SYDNEY = ServerInfo('b2sydney1', -33.8651, 151.2099, 'AU')
    BRAZIL = ServerInfo('b2brazil1', -22.9083, -43.1963, 'BR')

    @property
    def name(self) -> str:
        return self.value.name

    @property
    def latitude(self) -> float:
        return self.value.latitude

    @property
    def longitude(self) -> float:
        return self.value.longitude

    @property
    def country(self) -> str:
        return self.value.country

    @staticmethod
    def from_name(name: str) -> 'Server':
        for server in Server:
            if server.name == name:
                return server
        raise ValueError(f"No server with api name '{name}' found.")
