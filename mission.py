"""Requires the PyYAML module.

class_data = open('classData.yaml')
classes_yaml = yaml.load(class_data)

"""
import random

import yaml

import ai_controllers
from entity import Entity, FoxCollisionResolver, GooseCollisionResolver

class MissionModel:
    # Information needed to track the status of a mission.
    def __init__(self, width=5, height=2):
        self.reset()
        self.grid_width = width
        self.grid_height = height

    def reset(self):
        """Reset all variables.
        """
        self.fox_entity = None

        self.all_entities_by_id = {}

        self.collisions = []
        """Stores all collisions calculated."""

        self.all_ai_by_id = {}
        """All of the entity AI. Note these ids are different from the entity_id."""

    def load_mission(self, mission_id, yaml_document):
        """Populate the mission model based on the mission_id and the provided yaml_document.
        """
        # Clear all fields that maintain state.
        self.reset()

        # Find the mission yaml located in the document.
        yaml_object = yaml.load(yaml_document)
        mission_data = yaml_object['missions'][mission_id]

        # Get the height and width.
        self.grid_height = mission_data['map height']
        self.grid_width = mission_data['map width']

        # Find the Fox's starting position.
        fox_data = mission_data['fox']
        fox_position_x = fox_data['position']['x']
        fox_position_y = fox_data['position']['y']

        # Add a Fox.
        fox_entity = Entity(position={'x':2, 'y':0}, entity_type='fox')
        fox_entity.collision_behavior = FoxCollisionResolver(fox_entity)
        self.all_entities_by_id['fox'] = fox_entity
        self.all_entities_by_id['fox'].resource_id = 'fox'

        # Give it an AI controller.
        self.all_ai_by_id['fox'] = ai_controllers.ManualInstructions(self, 'fox')

        # Find the Geese.
        all_goose_data = mission_data['geese']
        goose_ids = []

        for goose_data in all_goose_data:
            goose_id = "goose_%03d" % len(goose_ids)
            goose_ids.append(goose_id)

            # Get their starting positions.
            goose_position_x = goose_data['position']['x']
            goose_position_y = goose_data['position']['y']

            # Add the goose.
            goose = Entity(position={'x':goose_position_x, 'y':goose_position_y}, entity_type='goose')
            goose.collision_behavior = GooseCollisionResolver(goose)
            self.all_entities_by_id[goose_id] = goose
            self.all_entities_by_id[goose_id].resource_id = 'goose'

        # Give them AI controllers.
        self.all_ai_by_id['goose'] = ai_controllers.ChaseTheFox(self, goose_ids)

    def delete_dead_entities(self):
        """Look at all entities and remove the dead ones.
        Return a list of the deleted entites
        """
        dead_entities = [e for e in self.all_entities_by_id if self.all_entities_by_id[e].is_dead]

        # Tell the ai_controllers to delete their entities.
        for ai in self.all_ai_by_id:
            self.all_ai_by_id[ai].delete_entities(dead_entities)

        # Actually delete them
        for e in dead_entities:
            del self.all_entities_by_id[e]
        return dead_entities

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

        # For each location, see if there are multiple entities on the same spot.
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

        # For each entity, see if it switched positions with another entity.
        for entity_a_id in self.all_entities_by_id:
            for entity_b_id in self.all_entities_by_id:
                # You can't cross yourself
                if entity_a_id == entity_b_id:
                    continue
                # Check the previous positions
                a_pos_x = self.all_entities_by_id[entity_a_id].position_x
                a_pos_y = self.all_entities_by_id[entity_a_id].position_y
                a_previous_pos_x = self.all_entities_by_id[entity_a_id].position_history[-1]['x']
                a_previous_pos_y = self.all_entities_by_id[entity_a_id].position_history[-1]['y']

                b_pos_x = self.all_entities_by_id[entity_b_id].position_x
                b_pos_y = self.all_entities_by_id[entity_b_id].position_y
                b_previous_pos_x = self.all_entities_by_id[entity_b_id].position_history[-1]['x']
                b_previous_pos_y = self.all_entities_by_id[entity_b_id].position_history[-1]['y']

                # If A's old pos is B's current pos and B's old pos is A's current pos, they switched.
                if (
                        a_previous_pos_x == b_pos_x \
                        and a_previous_pos_y == b_pos_y \
                        and a_pos_x == b_previous_pos_x \
                        and a_pos_y == b_previous_pos_y \
                ):
                    # Add this to the collisions.
                    new_collision = {
                        'colliding objects':[self.all_entities_by_id[entity_b_id], self.all_entities_by_id[entity_a_id]],
                        'x':a_pos_x,
                        'y':a_pos_y
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
                # Ask the entity to resolve its collision and collect the results
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

    def reset_for_new_round(self):
        """Reset the status at the end of the round.
        """
        self.fox_moved = False
        self.other_entity_move_results = {}
        self.player_desired_direction = None

        # Remove all dead units.
        self.dead_entities = self.mission_model.delete_dead_entities()

class MissionView(object):
    """Visual representation of the mission.
    This class has some function pointers that need to be set by a subclass.
    """
    def __init__(self):
        self.mission_controller = None

        # mission start has 3 statuses: "not started", "in progress" or "complete".
        self.mission_start_status = "not started"

        # Track the player's last input.
        self.player_input = None

        # Other entity's moves.
        self.other_entity_move_results = None

        # Sense if othe runits have moved.
        self.finished_moving_entities = False

        # Track the state of the mission complete message. It should have 3 states: "not started", "in progress" or "complete".
        self.mission_complete_display_progress = "not started"

        # Function Pointers that must be overriden by a subclass.
        self.draw_mission_start = lambda s: None
        self.move_entities = lambda s: None
        self.animate_mission_complete = lambda s: None

    def update(self):
        """This function will be called periodically to update the state or wait for animation to complete.
        """
        # If the mission controller didn't start, there is nothing to update.
        if not self.mission_controller:
            return

        # Get the mission view status
        status = self.get_status()

        # If the mission start hasn't happened yet, show it.
        if self.mission_start_status in ["not started", "in progress"]:
            self.draw_mission_start()
            return

        # If the player passed input, move the entities.
        if self.player_input != None and not self.other_entity_move_results:
            # Move all of the AI entities
            self.mission_controller.move_ai_entities()
            # Record the other entity moves
            mission_controller_status = self.mission_controller.get_status()
            self.other_entity_move_results = mission_controller_status["other entities moves"]
            return

        # If we know how the entities want to move this turn but we haven't moved them yet, move them now.
        if self.other_entity_move_results and not self.finished_moving_entities:
            self.move_entities()
            return

        # If the entities have finished moving, see if the mission is complete.
        if self.finished_moving_entities \
           and status["mission complete message id"] in ["win", "lose"] \
           and self.mission_complete_display_progress in ["not started", "in progress"]:
            self.animate_mission_complete()
            return

    def get_status(self):
        """Returns a dictionary showing the status of this mission.
        """

        # Determine if the mission controller is ready.
        if not self.mission_controller:
            return {
                "mission controller initialized" : False
            }

        mission_controller_status = self.mission_controller.get_status()

        # mission start has 3 statuses: not started, in progress or complete.
        showing_mission_start = None
        finished_showing_mission_start = None

        if self.mission_start_status == "not started":
            showing_mission_start = False
            finished_showing_mission_start = False
        elif self.mission_start_status == "in progress":
            showing_mission_start = True
            finished_showing_mission_start = False
        else:
            showing_mission_start = False
            finished_showing_mission_start = True

        # If the mission has finished showing the start screen, see if the player has passed input in.
        waiting_for_player_input = (
            self.mission_start_status == "complete"
            and self.player_input == None
        )

        # If you're not waiting for the player's moves, then you know what the entities are doing.
        entity_moves = self.other_entity_move_results

        # If the mission is completed, note this.
        mission_complete_message_id = None
        controller_state = self.mission_controller.get_status()
        if controller_state["mission complete"] in ["player win", "player lose"]:
            if controller_state["mission complete"] == "player win":
                mission_complete_message_id = "win"
            else:
                mission_complete_message_id = "lose"

        showing_mission_complete_display = None
        finished_showing_mission_complete_display = None

        if self.mission_complete_display_progress == "not started":
            showing_mission_complete_display = False
            finished_showing_mission_complete_display = False
        elif self.mission_complete_display_progress == "in progress":
            showing_mission_complete_display = True
            finished_showing_mission_complete_display = False
        else:
            showing_mission_complete_display = False
            finished_showing_mission_complete_display = True

        return {
            "mission controller initialized" : True,
            "showing mission start" : showing_mission_start,
            "finished showing mission start" : finished_showing_mission_start,
            "waiting for player input" : waiting_for_player_input,
            "entity moves" : entity_moves,
            "entities have moved" : self.finished_moving_entities,
            "showing mission complete message" : showing_mission_complete_display,
            "finished showing mission complete message" : finished_showing_mission_complete_display,
            "mission complete message id": mission_complete_message_id,
        }

    def reset_for_new_round(self):
        """Reset the state for the new round.
        """

        # Tell the mission controller to reset for the new round.
        self.mission_controller.reset_for_new_round()

        # Reset!
        self.player_input = None
        self.other_entity_move_results = None
        self.finished_moving_entities = False

    def apply_player_input(self, player_input):
        """If the mission is accepting player input, it will be passed to the mission controller.
        """
        # If we're waiting for player input, accept it.
        status = self.get_status()

        if status["waiting for player input"]:
            self.player_input = player_input
            # Pass the player input to the controller.
            self.mission_controller.player_input(player_input)

