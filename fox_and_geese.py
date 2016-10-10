import kivy
kivy.require('1.9.1')

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout

class MissionController(FloatLayout):
    def on_release_return_to_title(self):
        # Return to the title screen.

        # Tell the parent window to switch to the title screen.
        self.parent.switch_to_title()

class TitleScreen(FloatLayout):
    def on_release_go_to_mission(self):
        # Start the mission.

        # Tell the parent window to switch to the mission controller.
        self.parent.switch_to_mission()

class GameController(FloatLayout):
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
