class AIController():
    """Abstract/Base controller for AI."""
    def __init__ (self, mission_model, entity_id):
        """ Constructor. pass in the id of the entity to control."""
        self.mission_model = mission_model

        self._init_entities(entity_id)

        self.next_moves_by_entity_id = {}

    def _init_entities(self,entity_id):
        """Internal method to set the internal entity ids. Can be overwritten."""
        self.entity_id = entity_id

    def determine_next_moves(self):
        """Process the AI to figure out and store the next moves for the entities in controlled.
        """
        pass

    def get_next_moves(self):
        """Return the already stored moves.
        """
        return self.next_moves_by_entity_id

    def clear_all_ai_moves(self):
        """Clear all of the moves.
        """
        self.next_moves_by_entity_id = {}

    def delete_entities(self, entity_ids_to_delete):
        """Remove the given entities from consideration.
        Subclasses should overwrite this.
        """
        pass

class AlwaysWait(AIController):
    """AI will always wait.
    """
    def determine_next_moves(self):
        self.next_moves_by_entity_id[self.entity_id] = 'W'

class ChaseTheFox(AIController):
    """AI will try to move one step closer to the fox.
    """

    def _init_entities(self, entity_id):
        """Internal method to set the internal entity ids. Can be overwritten."""

        # If entity_ids is a single item, put it in a list
        if isinstance(entity_id, basestring):
            entity_id = [entity_id]

        self.entity_ids = entity_id

    def determine_next_moves(self):
        # Clear out previous round's instructions
        self.next_moves_by_entity_id = {}

        # Because you can move in eight directions, move towards the fox.
        fox_entity = self.mission_model.all_entities_by_id['fox']

        # Get the fox's position
        fox_position_x = fox_entity.position_x
        fox_position_y = fox_entity.position_y

        # For each entity
        for entity_id in self.entity_ids:
            entity = self.mission_model.all_entities_by_id[entity_id]

            # Get the entity's position
            entity_position_x = entity.position_x
            entity_position_y = entity.position_y

            entity_direction_x = ""
            entity_direction_y = ""

            # Move towards the fox
            if fox_position_x < entity_position_x:
                entity_direction_x = 'L'
            elif fox_position_x > entity_position_x:
                entity_direction_x = 'R'

            if fox_position_y < entity_position_y:
                entity_direction_y = 'D'
            elif fox_position_y > entity_position_y:
                entity_direction_y = 'U'

            final_direction = entity_direction_y + entity_direction_x

            if final_direction == "":
                final_direction = 'W'

            # Store this result for later.
            self.next_moves_by_entity_id[entity_id] = final_direction

    def delete_entities(self, entity_ids_to_delete):
        """Remove the given entities from consideration.
        Subclasses should overwrite this.
        """
        for id in entity_ids_to_delete:
            self.entity_ids.remove(id)

class ManualInstructions(AIController):
    """AI waits for an instruction.
    """
    def __init__(self, *args, **kwargs):
        AIController.__init__(self, *args, **kwargs)

        self.next_instruction = None

    def add_instruction(self, instruction):
        """Changes the next input to be consumed.
        """
        self.next_instruction = instruction

    def determine_next_moves(self):
        """Consume the next_instruction.
        """
        next_instruction = 'W'

        if self.next_instruction:
            next_instruction = self.next_instruction
            self.next_instruction = None

        # Store the id for this unit.
        self.next_moves_by_entity_id[self.entity_id] = next_instruction

class ReplayInstructions(AIController):
    """AI maintains a queue of instructions and processes one per turn.
    """
    def __init__(self, *args, **kwargs):
        AIController.__init__(self, *args, **kwargs)

        self.next_instructions = []

    def add_instructions(self, instructions):
        """Changes the next input to be consumed.
        """
        self.next_instructions += instructions

    def determine_next_moves(self):
        """Consume the next_instruction.
        """
        next_instruction = 'W'

        if len(self.next_instructions) > 0:
            next_instruction = self.next_instructions.pop(0)

        # Store the id for this unit.
        self.next_moves_by_entity_id[self.entity_id] = next_instruction
