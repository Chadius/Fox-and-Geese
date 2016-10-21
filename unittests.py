import unittest
from mission import MissionModel
from entity import Entity, FoxCollisionResolver, GooseCollisionResolver
from mock import patch

class MissionControllerTest(unittest.TestCase):
    def setUp(self):
        # Create a 3x2 map.
        self.mission_model = MissionModel(width=3, height=2)
        # Put entities on the map, near the corners.
        fox_entity = Entity(position={'x':0, 'y':1})
        goose_entity = Entity(position={'x':2, 'y':0})
        goose2_entity = Entity(position={'x':1, 'y':0})
        self.mission_model.all_entities_by_id['fox'] = fox_entity
        self.mission_model.all_entities_by_id['goose_000'] = goose_entity
        self.mission_model.all_entities_by_id['goose_001'] = goose2_entity

    def test_move_to_open_spot(self):
        # Test unit can move into an open spot
        self.mission_model.try_to_move_entity(
            id='fox',
            direction='D'
        )

        self.mission_model.try_to_move_entity(
            id='goose_000',
            direction='UL'
        )

        # This unit is going to wait this turn.
        self.mission_model.try_to_move_entity(
            id='goose_001',
            direction='W'
        )

        # Units should not have moved yet
        fox_entity = self.mission_model.all_entities_by_id['fox']
        self.assertEqual(fox_entity.position_x, 0)
        self.assertEqual(fox_entity.position_y, 1)

        goose_entity = self.mission_model.all_entities_by_id['goose_000']
        self.assertEqual(goose_entity.position_x, 2)
        self.assertEqual(goose_entity.position_y, 0)

        goose2_entity = self.mission_model.all_entities_by_id['goose_001']
        self.assertEqual(goose2_entity.position_x, 1)
        self.assertEqual(goose2_entity.position_y, 0)

        # Move all units
        self.mission_model.move_all_entities()

        # Test units are at expected positions
        fox_entity = self.mission_model.all_entities_by_id['fox']
        self.assertEqual(fox_entity.position_x, 0)
        self.assertEqual(fox_entity.position_y, 0)

        goose_entity = self.mission_model.all_entities_by_id['goose_000']
        self.assertEqual(goose_entity.position_x, 1)
        self.assertEqual(goose_entity.position_y, 1)

        goose2_entity = self.mission_model.all_entities_by_id['goose_001']
        self.assertEqual(goose2_entity.position_x, 1)
        self.assertEqual(goose2_entity.position_y, 0)

    def test_unit_stays_on_map(self):
        # Test unit does not move off screen
        self.mission_model.try_to_move_entity(
            id='fox',
            direction='DL'
        )

        self.mission_model.move_all_entities()

        fox_entity = self.mission_model.all_entities_by_id['fox']
        self.assertEqual(fox_entity.position_x, 0)
        self.assertEqual(fox_entity.position_y, 0)

    def test_collision_check1(self):
        # Move all entities on top of each other, then check for collisions to make sure it's the expected answer.

        # Move the fox and one of the geese on top of each other.
        self.mission_model.try_to_move_entity(
            id='fox',
            direction='DR'
        )

        self.mission_model.try_to_move_entity(
            id='goose_000',
            direction='L'
        )

        self.mission_model.move_all_entities()

        # All units should be on top of each other now
        fox_entity = self.mission_model.all_entities_by_id['fox']
        self.assertEqual(fox_entity.position_x, 1)
        self.assertEqual(fox_entity.position_y, 0)

        goose_entity = self.mission_model.all_entities_by_id['goose_000']
        self.assertEqual(goose_entity.position_x, 1)
        self.assertEqual(goose_entity.position_y, 0)

        goose2_entity = self.mission_model.all_entities_by_id['goose_001']
        self.assertEqual(goose2_entity.position_x, 1)
        self.assertEqual(goose2_entity.position_y, 0)

        # There should be no collision data
        self.assertEqual(self.mission_model.collisions, [])

        # Check for collisions
        self.mission_model.find_collisions()

        # Ensure expected data is in collisions
        self.assertEqual(len(self.mission_model.collisions), 1)
        self.assertEqual(self.mission_model.collisions[0]['x'], 1)
        self.assertEqual(self.mission_model.collisions[0]['y'], 0)
        self.assertEqual(len(self.mission_model.collisions[0]['colliding objects']), 3)
        self.assertIn(fox_entity, self.mission_model.collisions[0]['colliding objects'])
        self.assertIn(goose_entity, self.mission_model.collisions[0]['colliding objects'])
        self.assertIn(goose2_entity, self.mission_model.collisions[0]['colliding objects'])

    def test_collision_check2(self):
        # Move entities on top of each other, then check for collisions to make sure it's the expected answer.

        # Move the fox and one of the geese on top of each other.
        self.mission_model.try_to_move_entity(
            id='fox',
            direction='R'
        )

        self.mission_model.try_to_move_entity(
            id='goose_000',
            direction='UL'
        )

        self.mission_model.move_all_entities()

        # Fox and one goose should be on top of each other now
        fox_entity = self.mission_model.all_entities_by_id['fox']
        self.assertEqual(fox_entity.position_x, 1)
        self.assertEqual(fox_entity.position_y, 1)

        goose_entity = self.mission_model.all_entities_by_id['goose_000']
        self.assertEqual(goose_entity.position_x, 1)
        self.assertEqual(goose_entity.position_y, 1)

        # The other goose is left alone
        goose2_entity = self.mission_model.all_entities_by_id['goose_001']
        self.assertEqual(goose2_entity.position_x, 1)
        self.assertEqual(goose2_entity.position_y, 0)

        # There should be no collision data
        self.assertEqual(self.mission_model.collisions, [])

        # Check for collisions
        self.mission_model.find_collisions()

        # Ensure expected data is in collisions
        self.assertEqual(len(self.mission_model.collisions), 1)
        self.assertEqual(self.mission_model.collisions[0]['x'], 1)
        self.assertEqual(self.mission_model.collisions[0]['y'], 1)
        self.assertEqual(len(self.mission_model.collisions[0]['colliding objects']), 2)
        self.assertIn(fox_entity, self.mission_model.collisions[0]['colliding objects'])
        self.assertIn(goose_entity, self.mission_model.collisions[0]['colliding objects'])
        self.assertNotIn(goose2_entity, self.mission_model.collisions[0]['colliding objects'])

    def test_clear_collisions(self):
        # After checking for collisions, make sure you can clear the collision check.

        # Move the fox and one of the geese on top of each other.
        self.mission_model.try_to_move_entity(
            id='fox',
            direction='DR'
        )

        self.mission_model.try_to_move_entity(
            id='goose_000',
            direction='L'
        )

        self.mission_model.move_all_entities()

        # There should be no collision data
        self.assertEqual(self.mission_model.collisions, [])

        # Check for collisions
        self.mission_model.find_collisions()

        # There should be collisions
        self.assertNotEqual(self.mission_model.collisions, [])

        # Clear the collisions
        self.mission_model.clear_collisions()

        # There should be no collision data
        self.assertEqual(self.mission_model.collisions, [])


class FoxGooseCollisionBehavior(unittest.TestCase):
    def setUp(self):
        # Create a 3x2 map.
        self.mission_model = MissionModel(width=3, height=2)

        # Create a fox entity, and put it at the center.
        self.fox_entity = Entity(position={'x':1, 'y':0}, entity_type='fox')
        self.fox_entity.collision_behavior = FoxCollisionResolver(self.fox_entity)

        # Create 3 geese. They are all within 1 space of the Fox.
        self.goose_0 = Entity(position={'x':0, 'y':0}, entity_type='goose')
        self.goose_0.collision_behavior = GooseCollisionResolver(self.goose_0)

        self.goose_1 = Entity(position={'x':2, 'y':0}, entity_type='goose')
        self.goose_1.collision_behavior = GooseCollisionResolver(self.goose_1)

        self.goose_2 = Entity(position={'x':1, 'y':1}, entity_type='goose')
        self.goose_2.collision_behavior = GooseCollisionResolver(self.goose_2)

        self.mission_model.all_entities_by_id['fox'] = self.fox_entity
        self.mission_model.all_entities_by_id['goose_000'] = self.goose_0
        self.mission_model.all_entities_by_id['goose_001'] = self.goose_1
        self.mission_model.all_entities_by_id['goose_002'] = self.goose_2

    def test_one_goose_and_fox_makes_one_dead_goose(self):
        # If the fox bumps into 1 goose, mark the goose as dead

        # Move 1 goose into the fox.
        self.mission_model.try_to_move_entity(
            id='goose_000',
            direction='R'
        )
        self.mission_model.move_all_entities()

        # Confirm the goose is not dead
        self.assertEqual(self.goose_0.is_dead, False)

        # Check for collisions
        self.mission_model.find_collisions()

        # Ask Mission Controller for entities to act on the collisions
        self.mission_model.resolve_collisions()

        # The goose should be dead
        self.assertEqual(self.goose_0.is_dead, True)

        # The fox should NOT be dead
        self.assertEqual(self.fox_entity.is_dead, False)

        # Other geese should NOT be dead
        self.assertEqual(self.goose_1.is_dead, False)
        self.assertEqual(self.goose_2.is_dead, False)

    def test_two_geese_and_fox_makes_two_dead_geese(self):
        # If the fox bumps into 2 geese, mark the geese as dead

        # Move 2 geese into the fox.
        self.mission_model.try_to_move_entity(
            id='goose_000',
            direction='R'
        )
        self.mission_model.try_to_move_entity(
            id='goose_001',
            direction='L'
        )
        self.mission_model.move_all_entities()

        # Confirm the geese are not dead
        self.assertEqual(self.goose_0.is_dead, False)
        self.assertEqual(self.goose_1.is_dead, False)

        # Check for collisions
        self.mission_model.find_collisions()

        # Ask Mission Controller for entities to act on the collisions
        self.mission_model.resolve_collisions()

        # The geese should be dead
        self.assertEqual(self.goose_0.is_dead, True)
        self.assertEqual(self.goose_1.is_dead, True)

        # The fox should NOT be dead
        self.assertEqual(self.fox_entity.is_dead, False)

        # Other geese should NOT be dead
        self.assertEqual(self.goose_2.is_dead, False)

    def test_three_geese_and_fox_makes_one_dead_fox(self):
        # If three geese surround the fox, the fox should be dead.

        # Move 3 geese into the fox.
        self.mission_model.try_to_move_entity(
            id='goose_000',
            direction='R'
        )
        self.mission_model.try_to_move_entity(
            id='goose_001',
            direction='L'
        )
        self.mission_model.try_to_move_entity(
            id='goose_002',
            direction='D'
        )
        self.mission_model.move_all_entities()

        # Confirm the geese are not dead
        self.assertEqual(self.goose_0.is_dead, False)
        self.assertEqual(self.goose_1.is_dead, False)
        self.assertEqual(self.goose_2.is_dead, False)

        # Check for collisions
        self.mission_model.find_collisions()

        # Ask Mission Controller for entities to act on the collisions
        self.mission_model.resolve_collisions()

        # The geese should NOT be dead
        self.assertEqual(self.goose_0.is_dead, False)
        self.assertEqual(self.goose_1.is_dead, False)
        self.assertEqual(self.goose_2.is_dead, False)

        # The fox should be dead
        self.assertEqual(self.fox_entity.is_dead, True)

    @patch.object(MissionModel, '_get_random_entity')
    def test_two_geese_makes_one_move_ahead(self, _get_random_entity):
        # If two geese bump into each other, one of them moves ahead while the other one retreats.

        # _get_random_entity chooses an index at random. For the unit test we'll stub that out so it always chooses a fixed index.
        expected_results_by_random_index = {
            0: {
                'goose_0': {
                    'comment': 'advanced',
                    'x': 0,
                    'y': 1
                },
                'goose_2': {
                    'comment': 'retreated',
                    'x': 1,
                    'y': 1
                },
                'expected string' : 'goose_0 should be at (0,1) and goose_2 should be at (1,1). Actual positions:'
            },
            1: {
                'goose_0': {
                    'comment': 'retreated',
                    'x': 0,
                    'y': 0
                },
                'goose_2': {
                    'comment': 'advanced',
                    'x': 0,
                    'y': 1
                },
                'expected string' : 'goose_0 should be at (0,0) and goose_2 should be at (0,1). Actual positions:'
            }
        }

        for random_index in expected_results_by_random_index:
            # Reset the board.
            self.setUp()

            # Mock the _get_random_entity function so it always chooses a set index.
            _get_random_entity.side_effect = lambda entities: entities[random_index]

            # Two geese move into the same space.
            self.mission_model.try_to_move_entity(
                id='goose_000',
                direction='U'
            )
            self.mission_model.try_to_move_entity(
                id='goose_002',
                direction='L'
            )

            self.mission_model.move_all_entities()

            # Confirm the geese are at the same position
            self.assertEqual(self.goose_0.position_x, 0)
            self.assertEqual(self.goose_0.position_y, 1)

            self.assertEqual(self.goose_2.position_x, 0)
            self.assertEqual(self.goose_2.position_y, 1)

            # Check for collisions
            self.mission_model.find_collisions()

            # Ask Mission Controller for entities to act on the collisions
            self.mission_model.resolve_collisions()

            # One of the geese should have advanced to the new position and the other should have retreated
            goose_assertion_string = expected_results_by_random_index[random_index]['expected string'] + "goose_0: (%d,%d) goose_2: (%d,%d)" % (
                self.goose_0.position_x,
                self.goose_0.position_y,
                self.goose_2.position_x,
                self.goose_2.position_y,
            )

            self.assertEqual(self.goose_0.position_x, expected_results_by_random_index[random_index]['goose_0']['x'], goose_assertion_string)
            self.assertEqual(self.goose_0.position_y, expected_results_by_random_index[random_index]['goose_0']['y'], goose_assertion_string)

            self.assertEqual(self.goose_2.position_x, expected_results_by_random_index[random_index]['goose_2']['x'], goose_assertion_string)
            self.assertEqual(self.goose_2.position_y, expected_results_by_random_index[random_index]['goose_2']['y'], goose_assertion_string)

    @patch.object(MissionModel, '_get_random_entity')
    def test_two_geese_one_waiting_makes_one_retreat(self, _get_random_entity):
        # One goose stands still while the other walks into it. The walking one should retreat.

        # Mock the _get_random_entity function so it always chooses the last Entity. The first Entity should be the one that advances.
        _get_random_entity.side_effect = lambda entities: entities[-1]

        # Two geese move into the same space.
        self.mission_model.try_to_move_entity(
            id='goose_000',
            direction='W'
        )
        self.mission_model.try_to_move_entity(
            id='goose_002',
            direction='DL'
        )

        self.mission_model.move_all_entities()

        # Confirm the geese are at the same position
        self.assertEqual(self.goose_0.position_x, 0)
        self.assertEqual(self.goose_0.position_y, 0)

        self.assertEqual(self.goose_2.position_x, 0)
        self.assertEqual(self.goose_2.position_y, 0)

        # Check for collisions
        self.mission_model.find_collisions()

        # Ask Mission Controller for entities to act on the collisions
        self.mission_model.resolve_collisions()

        # Goose 0 should not have moved
        self.assertEqual(self.goose_0.position_x, 0)
        self.assertEqual(self.goose_0.position_y, 0)

        # Goose 2 should have returned to its original position
        self.assertEqual(self.goose_2.position_x, 1)
        self.assertEqual(self.goose_2.position_y, 1)

if __name__ == '__main__':
    unittest.main()
