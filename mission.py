class Entity:
    def __init__(self):
        self.position_x = None
        self.position_y = None
        self.resource_id = None

class MissionModel:
    # Information needed to track the status of a mission.
    def __init__(self):
        self.grid_width = 5
        self.grid_height = 5

        self.fox_entity = None

        self.all_entities_by_id = {}
        self.all_entities_by_id['fox'] = None
