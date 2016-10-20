class Entity:
    def __init__(self, position={'x':None, 'y':None}, entity_type=None):
        self.position_x = position['x']
        self.position_y = position['y']

        self.pending_position_x = None
        self.pending_position_y = None

        self.is_dead = False

        self.resource_id = None
        self.entity_type = entity_type

        # This component controlls the behavior when the Entity collides with something else.
        self.collision_behavior = CollisionResolver(self)

    def resolve_collisions(self, collision_info):
        return self.collision_behavior.get_collision_resolution(
            colliding_entities = collision_info['colliding objects'],
            collision_x = collision_info['x'],
            collision_y = collision_info['y']
        )

class CollisionResolver():
    # Abstract class for collision resolution. Figures out what it should do when it collides with other objects.
    def __init__(self, entity):
        self.entity = entity

    def get_collision_resolution(self, colliding_entities, collision_x, collision_y):
        # All CollisionResolvers must implement this function.
        # This calculates what will happen to self.entity after colliding with the other Entities.

        # colliding_entities - a list of Entities that have collided.
        # collision_x - the x coordinate of the collision.
        # collision_y - the y coordinate of the collision.
        raise NotImplementedError

class FoxCollisionResolver(CollisionResolver):
    def get_collision_resolution(self, colliding_entities, collision_x, collision_y):
        # All CollisionResolvers must implement this function.
        # This calculates what will happen to self.entity after colliding with the other Entities.

        # colliding_entities - a list of Entities that have collided.
        # collision_x - the x coordinate of the collision.
        # collision_y - the y coordinate of the collision.
        resolutions = []
        goose_count = 0
        # For each entity
        for colliding_entity in colliding_entities:
            # skip if it's yourself
            if colliding_entity == self.entity:
                continue

            # Count the geese
            if colliding_entity.entity_type == 'goose':
                goose_count += 1

        # If there are 3 geese, You are dead
        if goose_count >= 3:
            resolutions.append({'action':'kill self'})

        return resolutions

class GooseCollisionResolver(CollisionResolver):
    def get_collision_resolution(self, colliding_entities, collision_x, collision_y):
        # All CollisionResolvers must implement this function.
        # This calculates what will happen to self.entity after colliding with the other Entities.

        # colliding_entities - a list of Entities that have collided.
        # collision_x - the x coordinate of the collision.
        # collision_y - the y coordinate of the collision.

        resolutions = []
        collided_with_fox = False
        goose_count = 0
        # For each entity
        for colliding_entity in colliding_entities:
            # skip if it's yourself
            if colliding_entity == self.entity:
                goose_count += 1
                continue

            # count the number of geese
            if colliding_entity.entity_type == 'goose':
                goose_count += 1

            # see if you bumped into a fox
            if colliding_entity.entity_type == 'fox':
                collided_with_fox = True

        # If there is a fox and less than 3 geese, this goose should die.
        if collided_with_fox and goose_count < 3:
                resolutions.append({'action':'kill self'})
        return resolutions

