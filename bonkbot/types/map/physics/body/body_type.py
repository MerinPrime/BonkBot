import enum


class BodyType(enum.Enum):
    DYNAMIC = 'd'
    STATIC = 's'
    KINEMATIC = 'k'

    @staticmethod
    def from_name(name: str) -> 'BodyType':
        for body_type in BodyType:
            if body_type.value == name:
                return body_type
