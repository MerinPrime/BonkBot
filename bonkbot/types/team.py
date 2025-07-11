import enum


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/Team.ts
class Team(enum.IntEnum):
    SPECTATOR = 0
    FFA = 1
    RED = 2
    BLUE = 3
    GREEN = 4
    YELLOW = 5

    @staticmethod
    def from_number(value: int) -> 'Team':
        for team in Team:
            if value == team.value:
                return team
        return Team.SPECTATOR


class TeamState(enum.IntEnum):
    FFA = 0
    TEAMS = 1
