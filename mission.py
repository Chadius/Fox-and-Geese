class Entity:
    def __init__(self):
        self.position_x = None
        self.position_y = None

class MissionModel:
    # Information needed to track the status of a mission.
    def __init__(self):
        self.grid_width = 5
        self.grid_height = 5

        self.fox_entity = None

