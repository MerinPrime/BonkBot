import enum


class JointType(enum.Enum):
    LPJ = 'lpj'
    LSJ = 'lsj'
    GEAR = 'g'
    PRISMATIC = 'p'
    DISTANCE = 'd'
    REVOLUTE = 'rv'

    @staticmethod
    def from_name(name: str) -> 'JointType':
        for joint_type in JointType:
            if name == joint_type.value:
                return joint_type
