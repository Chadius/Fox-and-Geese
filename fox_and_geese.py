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

class TitleScreen(FloatLayout):
    def on_release_go_to_mission(self):
        # Start the mission.

        # Tell the parent window to switch to the mission controller.
        self.parent.switch_to_mission()

class GameController(FloatLayout):
    def __init__ (self, *args, **kwargs):
        super(GameController, self).__init__(*args, **kwargs)
        # Add a function to draw it when ready
        Clock.schedule_once(partial(GameController.callback_switch_to_game,self), 0.0)
    def callback_switch_to_game(self, dt):
        self.switch_to_mission()

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

    def setup_mission(self):
        """Creates the underlying MissionView.
        """
        # Make a mission model.
        self.mission_model = MissionModel(width=5, height=2)

        # Add a Fox.
        self.fox_entity = Entity(position={'x':2, 'y':0}, entity_type='fox')
        self.fox_entity.collision_behavior = FoxCollisionResolver(self.fox_entity)
        self.mission_model.all_entities_by_id['fox'] = self.fox_entity
        self.mission_model.all_ai_by_id['fox'] = ai_controllers.ManualInstructions(self.mission_model, 'fox')
        self.mission_model.all_entities_by_id['fox'].resource_id = 'fox'

        # Add some Geese.
        self.goose_0 = Entity(position={'x':0, 'y':0}, entity_type='goose')
        self.goose_0.collision_behavior = GooseCollisionResolver(self.goose_0)
        self.mission_model.all_entities_by_id['goose_000'] = self.goose_0
        self.mission_model.all_entities_by_id['goose_000'].resource_id = 'goose'
        self.mission_model.all_ai_by_id['goose'] = ai_controllers.ChaseTheFox(self.mission_model, ('goose_000'))

        # Make a new mission controller
        self.mission_controller = MissionController(mission_model = self.mission_model)

        # A contained Mission View to delegate calls.
        self.mission_view = MissionView()
        self.mission_view.mission_controller = self.mission_controller

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
        # Pass in the input using mission_view.apply_player_input()
        self.mission_view.apply_player_input(player_input)

        # Tell the mission_view to update
        Clock.schedule_once(
            partial(
                KivyMissionView.update_mission_view,
                self
            ),
            0.5
        )

    def move_entities_impl(self):
        """Animate the entities moving across the map.
        """

        # If we have started moving already, return (and print a message)

        # Get the mission_view status.
        # Read which units moved, and where.
        # Start moving them!
        # Make a callback when the units finished moving.
        print "TODO: Move entities"
        pass

    def move_entities_finished_callback(self):
        """Call back function when the entities have finished moving.
        """

        # If the entities aren't moving already, return (and print a message)

        # If the mission is complete, set up a callback to animate the mission complete.
        # If the mission isn't complete, call mission_view.reset_for_new_round() and wait for more player input.
        pass

    def animate_mission_complete_impl(self):
        """Animate the mission complete message.
        """
        # TODO: Make sure the mission complete banner is ready.

        # Set up the text for the mission complete message.

        # Move the mission complete message to its proper location.

        # Set up a callback to finish the animation.
        pass

    def animate_mission_complete_finished_callback(self):
        """Callback when the Mission Complete banner finishes.
        """
        # If the banner is complete, return (and print an error message)
        # Remove the mission complete banner
        pass

class FoxAndGeeseApp(App):
    def build(self):
        return GameController()

if __name__ == '__main__':
    FoxAndGeeseApp().run()
