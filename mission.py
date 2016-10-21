import random

class MissionModel:
    # Information needed to track the status of a mission.
    def __init__(self, width=5, height=2):
        self.grid_width = width
        self.grid_height = height

        self.fox_entity = None

        self.all_entities_by_id = {}
        self.all_entities_by_id['fox'] = None

        self.collisions = []

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

            # Push the previous position to the history
            entity.position_history.append({'x': entity.position_x, 'y': entity.position_y})

            # If a pending position was set, move the Entity to the new location.
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

    def find_collisions(self):
        # Looks at all objects (most are Entities) to find any that are at the same location.
        # This will add to this.collisions. Each collision adds a dictionary:
        # 'colliding objects' : a tuple of colliding objects, usually an Entity
        # 'x': x coordinate of the collision
        # 'y': y coordinate of the collision

        all_objects_by_x_y = {}

        # Record each object's location in a dictionary
        for entity_id in self.all_entities_by_id:
            entity = self.all_entities_by_id[entity_id]
            pos_x = entity.position_x
            pos_y = entity.position_y

            if not pos_x in all_objects_by_x_y:
                all_objects_by_x_y[pos_x] = {}
            if not pos_y in all_objects_by_x_y[pos_x]:
                all_objects_by_x_y[pos_x][pos_y] = []
            all_objects_by_x_y[pos_x][pos_y].append(entity)

        # For each location
        for pos_x in all_objects_by_x_y:
            for pos_y in all_objects_by_x_y[pos_x]:
                # If there are 2 or more items there
                if len(all_objects_by_x_y[pos_x][pos_y]) >= 2:
                    # Create a new collision
                    new_collision = {
                        'colliding objects':all_objects_by_x_y[pos_x][pos_y],
                        'x':pos_x,
                        'y':pos_y
                    }
                    # Add new collision to existing ones
                    self.collisions.append(new_collision)

    def clear_collisions(self):
        # Clear the collision data.
        del self.collisions[:]

    def resolve_collisions(self):
        # Based on self.collisions, each object that collided is asked to interact with the objects it collided with.

        collision_resolutions = {}
        # For each collision,
        for collision_info in self.collisions:
            # For each entity in the collision,
            for entity in collision_info['colliding objects']:
                # Ask the entity resolve its collision and collect the results
                if not entity in collision_info:
                    collision_resolutions[entity] = []
                results = entity.resolve_collisions(collision_info)
                collision_resolutions[entity] += (results)

        # For each entity with a resolution
        retreat_collisions = {}
        for entity in collision_resolutions:
            for resolution in collision_resolutions[entity]:
                if not resolution:
                    continue
                # If the entity wants to die, mark it as dead
                if resolution['action'] == 'kill self':
                    entity.is_dead = True

                # If the entity wants to retreat, we need to track the collision. Just store one set for each collision.
                if resolution['action'] == 'retreat':
                    x = resolution['x']
                    y = resolution['y']
                    if not x in retreat_collisions:
                        retreat_collisions[x] = {}
                    if not y in retreat_collisions[x]:
                        retreat_collisions[x][y] = {'x':x , 'y':y, 'entities': resolution['retreating objects']}

        # Some results say units need to retreat.
        # For each result resolution
        for x in retreat_collisions:
            for y in retreat_collisions[x]:
                # One Entity should NOT retreat.
                advancing_entity = self._get_retreating_entity_that_should_stay(retreat_collisions[x][y]['entities'])

                # For all units in the resolution
                for entity in retreat_collisions[x][y]['entities']:
                    # Skip if it's not the Entity that should retreat
                    if entity == advancing_entity:
                        continue

                    # The Entity should move back one space.
                    entity.position_x = entity.position_history[-1]['x']
                    entity.position_y = entity.position_history[-1]['y']

    def _get_retreating_entity_that_should_stay(self, retreating_entities):
        # Given information on Entities that want to retreat, return the Entity that should NOT retreat.
        # retreating_entities is a list of Entities.

        for entity in retreating_entities:
            # If the entity was waiting last turn, then something walked into it. It should advance.
            if (
                    (len(entity.position_history) == 0)
                    or (
                        entity.position_history[-1]['x'] == entity.position_x
                        and entity.position_history[-1]['y'] == entity.position_y
                    )
            ):
                return entity

        return self._get_random_entity(retreating_entities)

    def _get_random_entity(self, entities):
        # Just choose a random entity
        return random.choice(entities)

