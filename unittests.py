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
            direction='U'
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
        self.assertEqual(fox_entity.position_y, 1)

        goose_entity = self.mission_model.all_entities_by_id['goose_000']
        self.assertEqual(goose_entity.position_x, 1)
        self.assertEqual(goose_entity.position_y, 1)

        goose2_entity = self.mission_model.all_entities_by_id['goose_001']
        self.assertEqual(goose2_entity.position_x, 1)
        self.assertEqual(goose2_entity.position_y, 0)

    # Test unit does not move off screen

if __name__ == '__main__':
    unittest.main()
