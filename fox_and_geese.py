import kivy
kivy.require('1.9.1')

from functools import partial

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Ellipse, Rectangle

class MissionModel():
    # Information needed to track the status of a mission.
    def __init__(self):
        self.grid_width = 5
        self.grid_height = 5

class MissionController(FloatLayout):
    def on_size(self, instance, value):
        self.draw_grid(MissionModel())

    def on_release_return_to_title(self):
        # Return to the title screen.

        # Tell the parent window to switch to the title screen.
        self.parent.switch_to_title()

    def draw_grid(self, mission_model):
        grid_width = mission_model.grid_width
        grid_height = mission_model.grid_height
        line_thickness = 10

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
        if 'mission_controller' in self.ids:
            mission_controller = self.ids['mission_controller']

            # Remove the Mission Screen.
            self.remove_widget(mission_controller)

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
        mission_controller = MissionController()

        # Add it.
        self.ids['mission_controller'] = mission_controller
        self.add_widget(mission_controller)

class FoxAndGeeseApp(App):
    def build(self):
        return GameController()

if __name__ == '__main__':
    FoxAndGeeseApp().run()
