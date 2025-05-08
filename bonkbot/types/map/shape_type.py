import enum


class ShapeType(enum.Enum):
    BOX = 'bx'
    CIRCLE = 'ci'
    POLYGON = 'po'
    CHAIN = 'ch'

    @staticmethod
    def from_name(name: str) -> 'ShapeType':
        for shape_type in ShapeType:
            if name == shape_type.value:
                return shape_type
