import unittest
from mission import MissionModel, MissionController, MissionView
from entity import Entity, FoxCollisionResolver, GooseCollisionResolver
import ai_controllers
from mock import patch, Mock

class EntityMovementTest(unittest.TestCase):
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

    def test_one_goose_and_one_fox_switch_positions_makes_one_dead_goose(self):
        """A fox and goose are right next to each other. They switch positions. The goose should be dead.
        """

        # If the fox bumps into 1 goose, mark the goose as dead

        # Move 1 goose into the fox.
        self.mission_model.try_to_move_entity(
            id='goose_000',
            direction='R'
        )
        self.mission_model.try_to_move_entity(
            id='fox',
            direction='L'
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

    def test_three_dead_geese_and_fox_makes_one_living_fox(self):
        # If three geese surround the fox, but one is dead, the fox lives

        # Move 3 geese into the fox.
        self.mission_model.try_to_move_entity(
            id='goose_000',
            direction='R'
        )
        self.mission_model.try_to_move_entity(
            id='goose_001',
            direction='L'
        )
        self.goose_2.is_dead = True
        self.mission_model.try_to_move_entity(
            id='goose_002',
            direction='D'
        )
        self.mission_model.move_all_entities()

        # Confirm the geese are not dead
        self.assertEqual(self.goose_0.is_dead, False)
        self.assertEqual(self.goose_1.is_dead, False)
        self.assertEqual(self.goose_2.is_dead, True)

        # Check for collisions
        self.mission_model.find_collisions()

        # Ask Mission Controller for entities to act on the collisions
        self.mission_model.resolve_collisions()

        # The geese are unchanged
        self.assertEqual(self.goose_0.is_dead, False)
        self.assertEqual(self.goose_1.is_dead, False)
        self.assertEqual(self.goose_2.is_dead, True)

        # The fox should not be dead
        self.assertEqual(self.fox_entity.is_dead, False)

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

class GroupAITests(unittest.TestCase):
    """Tests the Goose AI to ensure it behaves correctly.
    """

    def setUp(self):
        # Make a map.
        self.mission_model = MissionModel(width=5, height=2)

        # Add a Fox.
        self.fox_entity = Entity(position={'x':2, 'y':0}, entity_type='fox')

        # Add some Geese.
        self.goose_0 = Entity(position={'x':0, 'y':0}, entity_type='goose')

        self.goose_1 = Entity(position={'x':4, 'y':1}, entity_type='goose')

        self.goose_2 = Entity(position={'x':3, 'y':0}, entity_type='goose')

        self.mission_model.all_entities_by_id['fox'] = self.fox_entity
        self.mission_model.all_entities_by_id['goose_000'] = self.goose_0
        self.mission_model.all_entities_by_id['goose_001'] = self.goose_1
        self.mission_model.all_entities_by_id['goose_002'] = self.goose_2

        # Add AI for the Fox.
        self.mission_model.all_ai_by_id['fox'] = ai_controllers.AlwaysWait(self.mission_model, 'fox')

        # Add AI for the Geese so they work together as a unit.
        self.mission_model.all_ai_by_id['goose'] = ai_controllers.ChaseTheFox(self.mission_model, ['goose_000', 'goose_001', 'goose_002'])

    def test_one_goose_moves_toward_fox(self):
        """Add one goose and one fox.
        Ask the AI to process.
        The AI should tell the goose to approach the fox.
        """
        self.mission_model.all_ai_by_id['goose'] = ai_controllers.ChaseTheFox(self.mission_model, ['goose_000'])
        self.mission_model.ask_all_ai_for_next_move()
        next_moves = self.mission_model.all_ai_by_id['goose'].get_next_moves()
        self.assertEqual(next_moves, {
            'goose_000':'R'
        })

    def test_clear_ai_instructions(self):
        """Ask the AI to determine the next move, then clear the AI.
        The AI should have no instructions and be ready to go.
        """
        # Assert it has no instructions ready
        next_moves = self.mission_model.all_ai_by_id['fox'].get_next_moves()
        self.assertEqual(next_moves, {})

        self.mission_model.ask_all_ai_for_next_move()

        # Assert that it wants the fox to wait
        next_moves = self.mission_model.all_ai_by_id['fox'].get_next_moves()
        self.assertEqual(next_moves, {
            'fox':'W'
        })

        # Clear the instructions and assert it's clear.
        self.mission_model.clear_all_ai_for_moves()
        next_moves = self.mission_model.all_ai_by_id['fox'].get_next_moves()
        self.assertEqual(next_moves, {})

    def test_three_goose_moves_toward_fox(self):
        """Add three goose and one fox.
        Ask the AI to process.
        The AI should tell all of the geese to approach the fox.
        """
        self.mission_model.ask_all_ai_for_next_move()
        next_moves = self.mission_model.all_ai_by_id['goose'].get_next_moves()
        self.assertEqual(next_moves, {
            'goose_000':'R',
            'goose_001':'DL',
            'goose_002':'L'
        })

    def test_replay_moves_ai(self):
        """The AI simply replays the moves given to it.
        Test that it moves correctly.
        """
        self.mission_model.all_ai_by_id['fox'] = ai_controllers.ReplayInstructions(self.mission_model, 'fox')
        self.mission_model.all_ai_by_id['fox'].add_instructions(["U"])
        self.mission_model.ask_all_ai_for_next_move()

        # Assert it wants to go up
        next_moves = self.mission_model.all_ai_by_id['fox'].get_next_moves()
        self.assertEqual(next_moves, {
            'fox':'U'
        })
        self.mission_model.clear_all_ai_for_moves()

        # Add another 2 instructions and assert it moves that way.
        self.mission_model.all_ai_by_id['fox'].add_instructions(["UL", "W"])
        self.mission_model.ask_all_ai_for_next_move()

        # Assert it wants to go up
        next_moves = self.mission_model.all_ai_by_id['fox'].get_next_moves()
        self.assertEqual(next_moves, {
            'fox':'UL'
        })
        self.mission_model.clear_all_ai_for_moves()

        self.mission_model.ask_all_ai_for_next_move()
        next_moves = self.mission_model.all_ai_by_id['fox'].get_next_moves()
        self.assertEqual(next_moves, {
            'fox':'W'
        })
        self.mission_model.clear_all_ai_for_moves()

    def test_manual_move_ai(self):
        """The Fox will move in the direction given.
        Test that it moves correctly.
        """
        self.mission_model.all_ai_by_id['fox'] = ai_controllers.ManualInstructions(self.mission_model, 'fox')
        self.mission_model.all_ai_by_id['fox'].add_instruction("DR")
        self.mission_model.ask_all_ai_for_next_move()

        # Assert it wants to go up
        next_moves = self.mission_model.all_ai_by_id['fox'].get_next_moves()
        self.assertEqual(next_moves, {
            'fox':'DR'
        })

class MissionStatusTest(unittest.TestCase):
    """These tests will decide if the player wins or loses.
    """
    def setUp(self):
        """Create a map.
        """
        # Create a 3x2 map.
        self.mission_model = MissionModel(width=3, height=2)

    def test_no_fox_mission_incomplete(self):
        """Without a Fox, the mission can never complete.
        """
        self.assertEqual(self.mission_model.get_mission_status(), "not finished")

    def test_no_geese_mission_incomplete(self):
        """Without a Goose, the mission can never complete.
        """

        # Add a Fox
        fox_entity = Entity(position={'x':0, 'y':1}, entity_type='fox')
        self.mission_model.all_entities_by_id['fox'] = fox_entity

        self.assertEqual(self.mission_model.get_mission_status(), "not finished")

    def test_all_geese_dead_mission_success(self):
        """If there is a Fox and all Geese are dead, the mission is successful and you win.
        """
        # Add a Fox
        fox_entity = Entity(position={'x':0, 'y':1}, entity_type='fox')
        self.mission_model.all_entities_by_id['fox'] = fox_entity

        # Add a Goose
        goose0_entity = Entity(position={'x':2, 'y':0}, entity_type='goose')
        self.mission_model.all_entities_by_id['goose_000'] = goose0_entity
        # Mark the Goose as dead
        goose0_entity.is_dead = True

        # Mission Status should indicate the player won
        self.assertEqual(self.mission_model.get_mission_status(), "player win")

    def test_fox_dead_mission_failure(self):
        """If there are Geese and the Fox is dead, the mission is a failure and you lose.
        """
        # Add a Fox
        fox_entity = Entity(position={'x':0, 'y':1}, entity_type='fox')
        self.mission_model.all_entities_by_id['fox'] = fox_entity
        # Mark the Fox as dead
        fox_entity.is_dead = True

        # Add two Geese. Mark one as dead.
        goose0_entity = Entity(position={'x':2, 'y':0}, entity_type='goose')
        self.mission_model.all_entities_by_id['goose_000'] = goose0_entity

        goose1_entity = Entity(position={'x':1, 'y':0}, entity_type='goose')
        self.mission_model.all_entities_by_id['goose_001'] = goose1_entity
        goose1_entity.is_dead = True
        # Mission Status should indicate the player lost
        self.assertEqual(self.mission_model.get_mission_status(), "player lose")

    def test_all_dead_mission_failure(self):
        """If the Geese and Fox are dead, the mission is a failure and you lose.
        """
        # Add a Fox
        fox_entity = Entity(position={'x':0, 'y':1}, entity_type='fox')
        self.mission_model.all_entities_by_id['fox'] = fox_entity
        # Mark the Fox as dead
        fox_entity.is_dead = True

        # Add a Goose
        # Mark the Goose as dead
        goose0_entity = Entity(position={'x':2, 'y':0}, entity_type='goose')
        self.mission_model.all_entities_by_id['goose_000'] = goose0_entity
        goose0_entity.is_dead = True

        goose1_entity = Entity(position={'x':1, 'y':0}, entity_type='goose')
        self.mission_model.all_entities_by_id['goose_001'] = goose1_entity
        goose1_entity.is_dead = True

        # Mission Status should indicate the player lost
        self.assertEqual(self.mission_model.get_mission_status(), "player lose")

    def test_in_progress(self):
        """The mission is still in progress if the Fox and some Geese are alive.
        """
        # Add a Fox
        fox_entity = Entity(position={'x':0, 'y':1}, entity_type='fox')
        self.mission_model.all_entities_by_id['fox'] = fox_entity

        # Add two Geese. Mark one as dead.
        goose0_entity = Entity(position={'x':2, 'y':0}, entity_type='goose')
        self.mission_model.all_entities_by_id['goose_000'] = goose0_entity

        goose1_entity = Entity(position={'x':1, 'y':0}, entity_type='goose')
        self.mission_model.all_entities_by_id['goose_001'] = goose1_entity
        goose1_entity.is_dead = True
        # Mission Status should indicate the player lost
        self.assertEqual(self.mission_model.get_mission_status(), "not finished")

class MissionControllerStateTest(unittest.TestCase):
    """Tests that the mission control responds to correct stimuli.
    """

    def setUp(self):
        # Make a map.
        self.mission_model = MissionModel(width=5, height=2)

        # Add a Fox.
        self.fox_entity = Entity(position={'x':2, 'y':0}, entity_type='fox')
        self.fox_entity.collision_behavior = FoxCollisionResolver(self.fox_entity)
        self.mission_model.all_entities_by_id['fox'] = self.fox_entity
        self.mission_model.all_ai_by_id['fox'] = ai_controllers.ManualInstructions(self.mission_model, 'fox')
        # Add some Geese.
        self.goose_0 = Entity(position={'x':0, 'y':0}, entity_type='goose')
        self.goose_0.collision_behavior = GooseCollisionResolver(self.goose_0)
        self.mission_model.all_entities_by_id['goose_000'] = self.goose_0
        self.mission_model.all_ai_by_id['goose'] = ai_controllers.ChaseTheFox(self.mission_model, ['goose_000'])

        self.mission_controller = MissionController(mission_model = self.mission_model)

    def test_not_initialized(self):
        """Without a map, the mission contoller should mention it is not ready yet.
        """
        no_map_mission_controller = MissionController()
        state = no_map_mission_controller.get_status()
        self.assertFalse(state["map initialized"])

    def test_ready_for_player_input(self):
        """See if the mission controller is ready for player input.
        """
        state = self.mission_controller.get_status()
        self.assertTrue(state["map initialized"])

    def test_see_fox_movement(self):
        """After passing player input and moving, the mission controller should show the results of the fox's move.
        """
        self.mission_controller.player_input('w')
        state = self.mission_controller.get_status()
        self.assertEqual(state["player input"], "w")
        self.assertTrue(state["fox moved"])

    def test_other_entity_moves(self):
        """After the fox has finished moving, tell the mission controller you're ready. The other entities should move.
        """
        self.mission_controller.player_input('L')
        self.mission_controller.move_ai_entities()

        state = self.mission_controller.get_status()
        self.assertEqual(
            state["other entities moves"],
            {
                'fox': {
                    'x':1,
                    'y':0,
                    'is dead': False
                },
                'goose_000': {
                    'x':1,
                    'y':0,
                    'is dead': True
                }
            }
        )

    def test_check_mission_complete(self):
        """After killing the geese, did the mission complete?
        """
        self.mission_controller.player_input('l')
        self.mission_controller.move_ai_entities()

        state = self.mission_controller.get_status()
        self.assertEqual(state["mission complete"], "player win")

    def test_reset_for_new_round(self):
        """After moving, reset the state for the new round.
        """
        self.mission_controller.player_input('w')
        state = self.mission_controller.get_status()
        self.assertEqual(state["player input"], "w")
        self.assertTrue(state["fox moved"])

        self.mission_controller.reset_for_new_round()
        state = self.mission_controller.get_status()

        self.assertTrue(state['map initialized'])
        self.assertFalse(state['mission complete'])
        self.assertFalse(state['fox moved'])
        self.assertEqual(state['other entities moves'], {})
        self.assertIsNone(state['player input'])

    def test_reset_for_new_round_removes_dead(self):
        """Reset the state for the new round and remove dead units.
        """
        # Add another Goose.
        self.goose_1 = Entity(position={'x':1, 'y':0}, entity_type='goose')
        self.goose_1.collision_behavior = GooseCollisionResolver(self.goose_1)
        self.mission_model.all_entities_by_id['goose_001'] = self.goose_1
        self.mission_model.all_ai_by_id['goose'] = ai_controllers.ChaseTheFox(self.mission_model, ['goose_000', 'goose_001'])

        # Fox stands still. The goose should move into it and die.
        self.mission_controller.player_input('w')
        self.mission_controller.move_ai_entities()
        state = self.mission_controller.get_status()

        self.mission_controller.reset_for_new_round()
        state = self.mission_controller.get_status()

        # Fox should still be alive, there should only be 1 goose around.
        self.assertFalse(self.fox_entity.is_dead)
        self.assertFalse("goose_001" in self.mission_model.all_entities_by_id)
        self.assertFalse("goose_001" in self.mission_model.all_ai_by_id['goose'].entity_ids)

class TestMissionView(MissionView):
    """Testable implementation of MissionView.
    """
    def __init__(self):
        super(TestMissionView, self).__init__()
        self.draw_mission_start = self.draw_mission_start_impl
        self.move_entities = self.move_entities_impl
        self.animate_mission_complete = self.animate_mission_complete_impl

    def draw_mission_start_impl(self):
        """Draw the mission start banner.
        """
        # If it hasn't started, start it now
        if self.mission_start_status == "not started":
            self.mission_start_status = "in progress"
            return

        # If it's in progress, declare it complete
        if self.mission_start_status == "in progress":
            self.mission_start_status = "complete"
            return

    def move_entities_impl(self):
        """Animate the entities moving across the map.
        """
        # Assume units have moved.
        self.finished_moving_entities = True

    def animate_mission_complete_impl(self):
        """Animate the mission complete message.
        """

        # If the sign hasn't been shown yet, start.
        if self.mission_complete_display_progress == "not started":
            self.mission_complete_display_progress = "in progress"
            return

        # If the sign is being shown, assume it completed.
        if self.mission_complete_display_progress == "in progress":
            self.mission_complete_display_progress = "complete"
            return

class MissionViewTests(unittest.TestCase):
    """Tests the graphical representation.
    """

    def setUp(self):
        self.mission_view = TestMissionView()
        self.mock_mission_controller = Mock()

    def get_mission_controller_map_initialized(self):
        """Returns a mission controller whose map is initialized.
        """
        self.mock_mission_controller.get_status.return_value = {
            'map initialized':True,
            "other entities moves": {},
            "mission complete": None
        }
        self.mission_view.mission_controller = self.mock_mission_controller

    def get_mission_controller_player_input(self):
        """Creates a mission controller where the player is ready to add input.
        """
        self.get_mission_controller_map_initialized()
        self.entity_moves = {
            'fox': {
                'x':1,
                'y':0,
                'is dead': False
            },
            'goose_000': {
                'x':1,
                'y':0,
                'is dead': True
            }
        }
        self.mock_mission_controller.get_status.return_value = {
            'map initialized':True,
            "other entities moves": self.entity_moves,
            "mission complete": None
        }
        self.mock_mission_controller.apply_player_input.side_effect = {}
        self.mission_view.mission_controller = self.mock_mission_controller

    def get_mission_controller_player_waited(self):
        """Creates a mission controller where the player waits.
        """
        self.get_mission_controller_player_input()
        self.mission_view.mission_controller = self.mock_mission_controller
        self.mission_view.update()
        self.mission_view.update()
        self.mission_view.apply_player_input('w')
        self.mission_view.update()

    def test_wait_for_initialization(self):
        """Newly created MapView waits for initialization.
        """
        mission_view = TestMissionView()
        status = mission_view.get_status()
        self.assertEqual(status["mission controller initialized"], False)

    def test_show_mission_start(self):
        """Mission Controller has been initialized.
        Mission View will try to show the Mission Start screen.
        """
        self.get_mission_controller_map_initialized()
        self.mission_view.mission_controller = self.mock_mission_controller

        self.mission_view.update()
        status = self.mission_view.get_status()
        self.assertTrue(status["mission controller initialized"])
        self.assertTrue(status["showing mission start"])
        self.assertFalse(status["finished showing mission start"])

    def test_wait_for_mission_start_complete(self):
        """Mission View is showing the Mission Start screen.
        Mission View waits for the screen to finish.
        """
        self.get_mission_controller_map_initialized()

        self.mission_view.mission_controller = self.mock_mission_controller

        self.mission_view.update()
        self.mission_view.update()
        status = self.mission_view.get_status()
        self.assertFalse(status["showing mission start"])
        self.assertTrue(status["finished showing mission start"])

    def test_wait_for_player_input(self):
        """Make sure the MissionView is ready to accept player input when the player select screen is ready.
        """
        self.get_mission_controller_map_initialized()

        self.mission_view.update()
        status = self.mission_view.get_status()
        self.assertFalse(status["waiting for player input"])

        self.mission_view.update()
        status = self.mission_view.get_status()
        self.assertTrue(status["waiting for player input"])

    def test_send_player_input(self):
        """MissionView can pass in Player Input to the Mission Controller.
        Confirm the Mission Controller recieves the input.
        """
        self.get_mission_controller_map_initialized()

        self.mock_mission_controller.apply_player_input.side_effect = {}
        self.mission_view.mission_controller = self.mock_mission_controller

        self.mission_view.update()
        self.mission_view.update()
        status = self.mission_view.get_status()
        self.assertTrue(status["waiting for player input"])
        self.mission_view.apply_player_input('w')

        self.mission_view.update()
        status = self.mission_view.get_status()
        self.assertFalse(status["waiting for player input"])
        self.mission_view.mission_controller.player_input.assert_called_with('w')

    def test_move_entities(self):
        """Mission Controller returns a list of entities to move.
        Mission View plans to move the entities.
        """
        self.get_mission_controller_player_waited()

        status = self.mission_view.get_status()
        self.assertFalse(status["entities have moved"])
        self.assertEqual(status["entity moves"], self.entity_moves)

    def test_wait_for_entities_to_move(self):
        """Mission View moves the entities.
        Mission View waits to move the entities before continuing.
        """
        self.get_mission_controller_player_waited()

        status = self.mission_view.get_status()
        self.mission_view.update()
        status = self.mission_view.get_status()
        self.assertTrue(status["entities have moved"])

    def test_mission_win(self):
        """MissionController is in the Mission Win state.
        MissionView will show the Mission Complete message.
        """
        self.get_mission_controller_player_waited()

        self.mock_mission_controller.get_status.return_value = {
            'map initialized':True,
            "other entities moves": self.entity_moves,
            "mission complete": "player win"
        }

        self.mission_view.update()
        state = self.mission_view.get_status()

        self.assertFalse(state["showing mission complete message"])
        self.assertFalse(state["finished showing mission complete message"])
        self.assertEqual(state["mission complete message id"], "win")

        self.mission_view.update()
        state = self.mission_view.get_status()

        self.assertTrue(state["showing mission complete message"])
        self.assertFalse(state["finished showing mission complete message"])

        self.mission_view.update()
        state = self.mission_view.get_status()

        self.assertFalse(state["showing mission complete message"])
        self.assertTrue(state["finished showing mission complete message"])

    def test_mission_lose(self):
        """MissionController is in the Mission Lose state.
        MissionView will show the Failure message.
        """
        self.get_mission_controller_player_waited()

        self.mock_mission_controller.get_status.return_value = {
            'map initialized':True,
            "other entities moves": self.entity_moves,
            "mission complete": "player lose"
        }

        self.mission_view.update()
        state = self.mission_view.get_status()

        self.assertFalse(state["showing mission complete message"])
        self.assertFalse(state["finished showing mission complete message"])
        self.assertEqual(state["mission complete message id"], "lose")

        self.mission_view.update()
        state = self.mission_view.get_status()

        self.assertTrue(state["showing mission complete message"])
        self.assertFalse(state["finished showing mission complete message"])

        self.mission_view.update()
        state = self.mission_view.get_status()

        self.assertFalse(state["showing mission complete message"])
        self.assertTrue(state["finished showing mission complete message"])

    def test_reset_status_for_new_round(self):
        """Entities have moved but the mission is not complete. Ensure after resetting, the system is ready for player input.
        """

        # Wait for the entities to move
        self.get_mission_controller_player_waited()

        status = self.mission_view.get_status()
        self.mission_view.update()
        status = self.mission_view.get_status()

        self.assertTrue(status["entities have moved"])
        self.mission_view.reset_for_new_round()

        status = self.mission_view.get_status()
        self.assertTrue(status["mission controller initialized"])
        self.assertFalse(status["showing mission start"])
        self.assertTrue(status["finished showing mission start"])
        self.assertTrue(status["waiting for player input"])
        self.assertEqual(status["entity moves"], None)
        self.assertFalse(status["entities have moved"])
        self.assertFalse(status["showing mission complete message"])
        self.assertFalse(status["finished showing mission complete message"])
        self.assertIsNone(status["mission complete message id"])

if __name__ == '__main__':
    unittest.main()
