class Entity:
    def __init__(self, position={'x':None, 'y':None}):
        self.position_x = position['x']
        self.position_y = position['y']

        self.pending_position_x = None
        self.pending_position_y = None

        self.resource_id = None

class MissionModel:
    # Information needed to track the status of a mission.
    def __init__(self, width=5, height=2):
        self.grid_width = width
        self.grid_height = height

        self.fox_entity = None

        self.all_entities_by_id = {}
        self.all_entities_by_id['fox'] = None

    def try_to_move_entity(self, id, direction):
        # Set up a pending move for the given Entity.
        # Does not actually move all units until you call move_all_units()
        entity_to_move = self.all_entities_by_id[id]
        direction_code = direction.upper()
        code_valid = False

        # Move left if possible.
        if direction_code in ['UL', 'L', 'DL']:
            entity_to_move.pending_position_x = entity_to_move.position_x - 1
            code_valid = True

        # Move right if possible.
        if direction_code in ['UR', 'R', 'DR']:
            entity_to_move.pending_position_x = entity_to_move.position_x + 1
            code_valid = True

        # Move up if possible.
        if direction_code in ['UL', 'U', 'UR']:
            entity_to_move.pending_position_y = entity_to_move.position_y + 1
            code_valid = True

        # Move down if possible.
        if direction_code in ['DL', 'D', 'DR']:
            entity_to_move.pending_position_y = entity_to_move.position_y - 1
            code_valid = True

        # If the unit wants to wait, do not move.
        if direction_code == 'W':
            entity_to_move.pending_position_x = entity_to_move.position_x
            entity_to_move.pending_position_y = entity_to_move.position_y
            code_valid = True

        # If you recieved a valid movement direction, make sure each pending direction is set.
        if code_valid:
            if entity_to_move.pending_position_x == None:
                entity_to_move.pending_position_x = entity_to_move.position_x
            if entity_to_move.pending_position_y == None:
                entity_to_move.pending_position_y = entity_to_move.position_y

    def move_all_entities(self):
        # All Entities with a pending move are moved.
        for entity_id in self.all_entities_by_id:
            entity = self.all_entities_by_id[entity_id]
            if entity.pending_position_x != None \
                and entity.pending_position_y != None:
                entity.position_x = entity.pending_position_x
                entity.position_y = entity.pending_position_y
            # Ensure the Entity is on the map.
            if entity.position_x < 0:
                entity.position_x = 0
            if entity.position_y < 0:
                entity.position_y = 0
            if entity.position_x >= self.grid_width:
                entity.position_x = self.grid_width-1
            if entity.position_y >= self.grid_height:
                entity.position_y = self.grid_height-1
            # Clear the pending position.
            entity.pending_position_x = None
            entity.pending_position_y = None
