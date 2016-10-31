import random

class MissionModel:
    # Information needed to track the status of a mission.
    def __init__(self, width=5, height=2):
        self.grid_width = width
        self.grid_height = height

        self.fox_entity = None

        self.all_entities_by_id = {}

        self.collisions = []
        """Stores all collisions calculated."""

        self.all_ai_by_id = {}
        """All of the entity AI. Note these ids are different from the entity_id."""

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

    def ask_all_ai_for_next_move(self):
        """Ask for all ai controllers to process and figure out their next moves.
        """
        for ai_controller in self.all_ai_by_id.values():
            ai_controller.determine_next_moves()

    def clear_all_ai_for_moves(self):
        """Clear all AI moves.
        """
        for ai_controller in self.all_ai_by_id.values():
            ai_controller.clear_all_ai_moves()

    def get_mission_status(self):
        """Returns a string indicating if the player won, lost, or is still inprogress.
        Returns one of 'player win', 'player lose', 'not finished'
        """
        win_string = 'player win'
        lose_string = 'player lose'
        not_finished_string = 'not finished'

        # Count the number of Foxes and Geese on the map. Also count how many of them are dead.
        fox_count = 0
        dead_fox_count = 0
        goose_count = 0
        dead_goose_count = 0
        for entity in self.all_entities_by_id.values():
            if entity.entity_type == "fox":
                fox_count += 1
                if entity.is_dead:
                    dead_fox_count += 1
            if entity.entity_type == "goose":
                goose_count += 1
                if entity.is_dead:
                    dead_goose_count += 1

        # If there are no Fox or Geese, the mission cannot end.
        if fox_count == 0 or goose_count == 0:
            return not_finished_string

        # If the fox is dead, the player lost.
        if dead_fox_count > 0:
            return lose_string

        # If all of the geese are dead, the player won.
        if dead_goose_count == goose_count:
            return win_string

        # Otherwise the fox and at least 1 goose is alive. It's not finished.
        return not_finished_string

class MissionController():
    """Uses a mission controller and processes actions. Keeps track of a state.
    """
    def __init__(self, mission_model=None):

        # The mission model will track the map and any entities inside.
        self.mission_model = mission_model

        self.fox_moved = False
        self.other_entity_move_results = {}
        self.player_desired_direction = None
        self.mission_complete_status = None

    def get_status(self):
        """Returns a dictionary giving the status of the last action.

        map initialized: Boolean that tells you if it's ok to draw the map and entities.
        mission complete: string that is one of 3 values. See MissionModel.get_mission_status
        fox moved: A boolean.
        other entities moves: A dictionary containing the result of the other Entity movements. Keys are the entity_id, the values are dictionaries:
                x: x coordinate of the entity
                y: y coordinate of the entity
                is dead: Boolean indicating if the entity died.
        player input: A string indicating the player's movement (w is wait, u d l r may be combined to form the 8 cardinal directions)
        """

        # If there is no mission model, return False.
        map_initialized = self.mission_model != None

        return {
            'map initialized': map_initialized,
            'mission complete': self.mission_complete_status,
            'fox moved': self.fox_moved,
            'other entities moves' : self.other_entity_move_results,
            'player input': self.player_desired_direction,
        }

    def player_input(self, player_desired_direction):
        """Player has chosen to move in a given direction. Update the model and the status.
        player_desired_direction: a string indicating what the player wants to do hthis turn.
        """

        player_desired_direction = player_desired_direction.lower()

        # Tell the model to move the fox unit
        self.mission_model.all_ai_by_id['fox'].add_instruction(player_desired_direction)

        # Clear the results of other movement.
        self.other_entity_move_results = {}

        #Note the fox tried to move.
        self.fox_moved = True
        self.player_desired_direction = player_desired_direction

    def move_ai_entities(self):
        """Tells the mission model to move all AI controlled Entities.
        """
        # Tell the ai to figure out their next move.
        self.mission_model.ask_all_ai_for_next_move()

        # Collect the moves the ai wants to do.
        entity_moves = {}

        for ai_controller in self.mission_model.all_ai_by_id.values():
            entity_moves.update(ai_controller.get_next_moves())

        # Move all units on the map.
        for entity_id, direction in entity_moves.iteritems():
            self.mission_model.try_to_move_entity(
                id=entity_id,
                direction=direction
            )
        self.mission_model.move_all_entities()

        # Resolve collisions
        self.mission_model.clear_collisions()
        self.mission_model.find_collisions()
        self.mission_model.resolve_collisions()

        # Record all of the units position and status.
        for entity_id in self.mission_model.all_entities_by_id:
            entity = self.mission_model.all_entities_by_id[entity_id]
            self.other_entity_move_results[entity_id] = {
                'x': entity.position_x,
                'y': entity.position_y,
                'is dead': entity.is_dead
            }

        # Check the mission status.
        self.mission_complete_status = self.mission_model.get_mission_status()
