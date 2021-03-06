import kivy
kivy.require('1.9.1')

from functools import partial

from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label

from mission import MissionModel, MissionController, MissionView
from entity import Entity, FoxCollisionResolver, GooseCollisionResolver
import ai_controllers

mission_yaml_file = """
campaign:
  mission ids:
    - mission 1
missions:
  mission 1:
    map height: 4
    map width: 5
    fox:
      position:
        x: 2
        y: 0
    geese:
      -
        position:
          x: 1
          y: 0
      -
        position:
          x: 3
          y: 0
      -
        position:
          x: 2
          y: 1
"""

class TitleScreen(FloatLayout):
    def on_release_go_to_mission(self):
        # Start the mission.

        # Tell the parent window to switch to the mission controller.
        self.parent.switch_to_mission()

class GameController(FloatLayout):
    def __init__ (self, *args, **kwargs):
        super(GameController, self).__init__(*args, **kwargs)
        # Add a function to draw it when ready
        Clock.schedule_once(partial(GameController.callback_switch_to_title,self), 0.0)

    def callback_switch_to_title(self, dt):
        self.switch_to_title()

    def switch_to_title(self):
        # User wants to switch to the title screen.

        # Remove the mission controller if it's active.
        if 'mission_view' in self.ids:
            mission_view = self.ids['mission_view']

            # Remove the Mission Screen.
            self.remove_widget(mission_view)

        # Prepare a new title screen.
        title_screen_controller = TitleScreen()

        # Add it.
        self.ids['title_screen'] = title_screen_controller
        self.add_widget(title_screen_controller)

    def switch_to_mission(self):
        # User wants to switch to the mission screen.

        # Remove the mission controller if it's active.
        if 'title_screen' in self.ids:
            # Find the title screen.
            title_screen = self.ids['title_screen']

            # Remove the Title Screen.
            self.remove_widget(title_screen)

        # Prepare a new mission controller.
        mission_view = KivyMissionView()

        # Add it.
        self.ids['mission_view'] = mission_view
        self.add_widget(mission_view)

class KivyMissionView(FloatLayout):
    """Kivy object to show visual elements and pass input.
    """
    def __init__(self, *args, **kwargs):
        super(KivyMissionView, self).__init__(*args, **kwargs)

        # Make the mission view.
        self.setup_mission()

        # Use this class's functions to implement actions.
        self.mission_view.draw_mission_start = self.draw_mission_start_impl
        self.mission_view.move_entities = self.move_entities_impl
        self.mission_view.animate_mission_complete = self.animate_mission_complete_impl

        # Set up sprites and images.
        self.image_info_by_id = {}
        self.image_info_by_id['fox'] = {
            'resource': 'f_icon.png'
        }
        self.image_info_by_id['goose'] = {
            'resource': 'g_icon.png'
        }
        self.sprite_info_by_id = {}
        self.started_moving_sprites = False

    def setup_mission(self):
        """Creates the underlying MissionView.
        """
        # Make a mission model.
        self.mission_model = MissionModel()
        self.mission_model.load_mission("mission 1", mission_yaml_file)

        # Make a new mission controller
        self.mission_controller = MissionController(mission_model = self.mission_model)

        # A contained Mission View to delegate calls.
        self.mission_view = MissionView()
        self.mission_view.mission_controller = self.mission_controller

    def oldSetup(self):
        """DELETE ME
        """
        self.mission_model = MissionModel(width=5, height=2)

        # Add a Fox.
        self.fox_entity = Entity(position={'x':2, 'y':0}, entity_type='fox')
        self.fox_entity.collision_behavior = FoxCollisionResolver(self.fox_entity)
        self.mission_model.all_entities_by_id['fox'] = self.fox_entity
        self.mission_model.all_ai_by_id['fox'] = ai_controllers.ManualInstructions(self.mission_model, 'fox')
        self.mission_model.all_entities_by_id['fox'].resource_id = 'fox'

        # Add some Geese.
        self.goose_0 = Entity(position={'x':1, 'y':0}, entity_type='goose')
        self.goose_0.collision_behavior = GooseCollisionResolver(self.goose_0)
        self.mission_model.all_entities_by_id['goose_000'] = self.goose_0
        self.mission_model.all_entities_by_id['goose_000'].resource_id = 'goose'

        self.goose_001 = Entity(position={'x':3, 'y':0}, entity_type='goose')
        self.goose_001.collision_behavior = GooseCollisionResolver(self.goose_0)
        self.mission_model.all_entities_by_id['goose_001'] = self.goose_001
        self.mission_model.all_entities_by_id['goose_001'].resource_id = 'goose'

        self.goose_002 = Entity(position={'x':2, 'y':1}, entity_type='goose')
        self.goose_002.collision_behavior = GooseCollisionResolver(self.goose_0)
        self.mission_model.all_entities_by_id['goose_002'] = self.goose_002
        self.mission_model.all_entities_by_id['goose_002'].resource_id = 'goose'

        self.mission_model.all_ai_by_id['goose'] = ai_controllers.ChaseTheFox(self.mission_model, ['goose_000', 'goose_001', 'goose_002'])

    def on_size(self, instance, value):
        """Redraw the screen when resized.
        """
        self.redraw()

    def redraw(self):
        """Clear and redraw the canvas.
        """
        # Clear the canvas.
        with self.canvas:
            Color(self.background_color[0], self.background_color[1], self.background_color[2], mode='hsv')
            Rectangle(
                pos=(0,0),
                size=(self.window_width, self.bar_height)
            )

        self.draw_grid(self.mission_model)

        # Draw each entity onto the grid.
        for entity_id in self.mission_model.all_entities_by_id:
            self.draw_entity(entity_id)

        # Update the mission view.
        self.update_mission_view()

    def update_mission_view(self, dt=0.0):
        """Updates the mission view so we know what to do next.
        """

        # Tell the mission view to update. The mission_view may call functions in this class.
        self.mission_view.update()

        # Get the status from the mission view.
        mission_view_status = self.mission_view.get_status()

    def draw_entity(self, entity_id):
        """ Draw the entity's icon on top of the grid.
        """
        if self.mission_model.all_entities_by_id[entity_id]:
            entity = self.mission_model.all_entities_by_id[entity_id]
            # Figure out its final coordinates.
            image_position = self.get_screen_coordinates_from_grid(
                self.mission_model,
                entity.position_x,
                entity.position_y
            )
            # Figure out the size the image should be.
            image_size = self.get_grid_cell_size(self.mission_model)
            # If the image doesn't exist, create it
            if not (entity_id in self.sprite_info_by_id and self.sprite_info_by_id[entity_id]):
                new_image = Image(
	            source = self.image_info_by_id[entity.resource_id]['resource'],
	            pos = image_position,
                    size_hint_x = None,
                    size_hint_y = None,
                    size = image_size,
                    allow_stretch = True
                )
                self.add_widget(new_image)
                self.sprite_info_by_id[entity_id] = new_image
            else:
                # Otherwise, move the image to its destination
                self.sprite_info_by_id[entity_id].pos = image_position
                self.sprite_info_by_id[entity_id].size = image_size

    def on_release_return_to_title(self):
        """Time to return to the title screen.
        """

        # Tell the parent window to switch to the title screen.
        self.parent.switch_to_title()

    def get_grid_line_thickness(self, grid_width, grid_height):
        # Returns the thickness the lines should be at.
        number_of_cells = grid_height * grid_width
        if number_of_cells > 100:
            return 2
        elif number_of_cells > 80:
            return 3
        elif number_of_cells > 60:
            return 5
        elif number_of_cells > 30:
            return 7
        return 10

    def draw_grid(self, mission_model):
        grid_width = mission_model.grid_width
        grid_height = mission_model.grid_height
        line_thickness = self.get_grid_line_thickness(grid_width, grid_height)

        # Draw the grid.
        with self.canvas:
            Color(0.0, 0.0, 0.2, mode='hsv')

            # Draw vertical lines of the grid.
            for i in xrange(grid_width+1):
                x = (self.window_width * i / (grid_width * 1.0)) - (line_thickness/2)
                y = 0
                Rectangle(
                    pos=(x, y),
                    size=(line_thickness, self.height)
                )

            # Draw horizontal lines of the grid.
            for i in xrange(grid_height+1):
                x = 0
                y = (self.bar_height * i / (grid_height * 1.0)) - (line_thickness/2)
                Rectangle(
                    pos=(x, y),
                    size=(self.window_width, line_thickness)
                )

    def get_grid_cell_size(self, mission_model):
        # Returns the size of each cell on the grid.
        width = self.window_width  / (mission_model.grid_width * 1.0)
        height = self.bar_height  / (mission_model.grid_height * 1.0)
        return (width, height)

    def get_screen_coordinates_from_grid(self,mission_model,grid_x,grid_y):
        # Converts the coordinates (grid_x, grid_y) to screen coordinates and returns them as a tuple.
        screen_x = (grid_x * self.window_width)  / (mission_model.grid_width * 1.0)
        screen_y = (grid_y * self.bar_height)  / (mission_model.grid_height * 1.0)
        return (screen_x, screen_y)

    def draw_mission_start_impl(self):
        """Draw the mission start banner.
        """
        mission_view_status = self.mission_view.get_status()

        # If it has started, exit (and print a message)
        if mission_view_status["showing mission start"] or mission_view_status["finished showing mission start"]:
            print "Mission Start banner already appeared. Why are we calling this function?"
            return

        # Make a mission_start_widget.
        self.mission_start_widget = self.make_mission_start_widget()
        self.mission_start_widget.pos=(-300,0)
        self.ids['mission_start'] = self.mission_start_widget
        self.add_widget(self.mission_start_widget)
        mission_start_widget = self.mission_start_widget

        # Center the Mission Start widget on the page.
        # Setup Animation object
        scroll_animation = Animation(x=0, y=0)
        # Use it on widget
        scroll_animation.start(mission_start_widget)

        # Set the mission view to in progress.
        self.mission_view.mission_start_status = "in progress"

        # Make a callback to announce that it's done.
        Clock.schedule_once(
            partial(
                KivyMissionView.draw_mission_start_callback,
                self
            ),
            2.0
        )

    def make_mission_start_widget(self):
        """Creates a Widget to show the mission start.
        """
        return Label(text='Hello world')

    def draw_mission_start_callback(self, dt):
        """Call back function when the mission start banner has finished.
        """

        # Declare the mission view's mission start status complete.
        self.mission_view.mission_start_status = "complete"

        # Remove the mission start banner.
        self.remove_widget(self.mission_start_widget)

        # Tell the layout to update.
        Clock.schedule_once(
            partial(
                KivyMissionView.update_mission_view,
                self
            ),
            0.5
        )

    def accept_player_input(self, player_input):
        """Callback to accept player input. player_input is a string indicating which direction the player wants to move in.
        """

        # If the mission view is not accepting player input, return
        status = self.mission_view.get_status()
        if not status["waiting for player input"]:
            return

        # Pass in the input using mission_view.apply_player_input()
        self.mission_view.apply_player_input(player_input)

        # Tell the mission_view to update

        # Update once to apply input and figure out how the units moved.
        Clock.schedule_once(
            partial(
                KivyMissionView.update_mission_view,
                self
            ),
            0.2
        )

        # Now actually move the units.
        Clock.schedule_once(
            partial(
                KivyMissionView.update_mission_view,
                self
            ),
            0.2
        )

    def move_entities_impl(self):
        """Animate the entities moving across the map.
        """

        # If we have started moving already, return
        if self.started_moving_sprites:
            return

        # Get the mission_view status.
        status = self.mission_view.get_status()

        # Read which units moved, and where.
        max_animation_time = 2.0
        for entity_id in status["entity moves"]:
            entity_animation = None

            # Start moving them.
            the_sprite = self.sprite_info_by_id[entity_id]

            final_position = self.get_screen_coordinates_from_grid(
                self.mission_model,
                status["entity moves"][entity_id]['x'],
                status["entity moves"][entity_id]['y'],
            )

            # Scroll the unit moving over
            scroll_animation = Animation(
                x=final_position[0],
                y=final_position[1]
            )
            # Use it on widget
            if entity_animation == None:
                entity_animation = scroll_animation
            else:
                entity_animation += scroll_animation

            # If any units died, fade them out.
            if status["entity moves"][entity_id]['is dead']:
                fade_animation = Animation(size=(0,0), t='in_quad')
                if entity_animation == None:
                    entity_animation = fade_animation
                else:
                    entity_animation += fade_animation

            entity_animation.start(the_sprite)

        # Make a callback when the units finished moving.
        self.started_moving_sprites = True

        Clock.schedule_once(
            partial(
                KivyMissionView.move_entities_finished_callback,
                self
            ),
            max_animation_time
        )

    def move_entities_finished_callback(self, dt=0.0):
        """Call back function when the entities have finished moving.
        """

        # If the entities aren't moving already, return (and print a message)
        if not self.started_moving_sprites:
            print "Sprites haven't finished moving. Why was this called?"
            return

        # Tell the mission view we finished moving.
        self.mission_view.finished_moving_entities = True

        # Set up a callback to update the status.
        Clock.schedule_once(
            partial(
                KivyMissionView.update_mission_view,
                self
            ),
            0.1
        )

        # Set up another callback to see if the round should be reset.
        Clock.schedule_once(
            partial(
                KivyMissionView.reset_for_new_round,
                self
            ),
            0.2
        )

    def reset_for_new_round(self, dt=0.0):
        """Reset the mission view for a new round if the mission is not yet complete.
        """

        # If the mission is complete, return
        mission_view_status = self.mission_view.get_status()
        if mission_view_status["mission complete message id"]:
            return

        # If the mission isn't complete, call mission_view.reset_for_new_round() and wait for more player input.
        status = self.mission_view.get_status()

        self.mission_view.reset_for_new_round()
        self.started_moving_sprites = False

        # Delete any sprites that correspond to non existent units.
        sprites_to_delete = [id for id in self.sprite_info_by_id if not id in self.mission_model.all_entities_by_id]

        for sprite_id in sprites_to_delete:
            sprite_to_delete = self.sprite_info_by_id[sprite_id]
            self.remove_widget(sprite_to_delete)
            del self.sprite_info_by_id[sprite_id]

    def animate_mission_complete_impl(self):
        """Animate the mission complete message.
        """
        # Make sure the mission complete banner is ready.
        status = self.mission_view.get_status()
        if status["showing mission complete message"] or not status["mission complete message id"]:
            print "Why did we call the animate mission copmlete impl?"
            return

        # Set up the text for the mission complete message.
        mission_complete_text = "you lose..."

        if status["mission complete message id"] == "win":
            mission_complete_text = "YOU WIN!"

        self.mission_complete_widget = self.make_mission_complete_widget(mission_complete_text)
        self.mission_complete_widget.pos=(-300,0)
        self.ids['mission_complete'] = self.mission_complete_widget
        self.add_widget(self.mission_complete_widget)
        mission_complete_widget = self.mission_complete_widget

        # Move the mission complete message to its proper location.
        scroll_animation = Animation(x=0, y=0)
        scroll_animation.start(mission_complete_widget)

        # Tell the mission view the banner is now in progress.
        self.mission_view.mission_complete_display_progress = "in progress"

        # Set up a callback to finish the animation.
        Clock.schedule_once(
            partial(
                KivyMissionView.animate_mission_complete_finished_callback,
                self
            ),
            2.0
        )

    def make_mission_complete_widget(self, message):
        """Creates a Widget to show the mission start.
        """
        return Label(text=message)

    def animate_mission_complete_finished_callback(self, dt=0.0):
        """Callback when the Mission Complete banner finishes.
        """
        # If the banner is complete, return (and print an error message)
        status = self.mission_view.get_status()
        if not status["showing mission complete message"] or status["finished showing mission complete message"]:
            print "We played the mission complete finished callback. Why?"
            return

        self.mission_view.mission_complete_display_progress = "complete"
        self.remove_widget(self.mission_complete_widget)

        # Update the mission view.
        Clock.schedule_once(
            partial(
                KivyMissionView.update_mission_view,
                self
            ),
            0.1
        )

class FoxAndGeeseApp(App):
    def build(self):
        return GameController()

if __name__ == '__main__':
    FoxAndGeeseApp().run()
