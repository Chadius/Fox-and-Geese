import unittest
from mission import MissionModel, Entity

class MissionControllerTest(unittest.TestCase):
    def setUp(self):
        # Create a 3x2 map.
        self.mission_model = MissionModel(width=3, height=2)
        # Put 2 entities on the map, near the corners.
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

    # Test objects walking into the same wall, need to use last round's location

if __name__ == '__main__':
    unittest.main()
