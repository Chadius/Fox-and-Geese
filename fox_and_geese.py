import kivy
kivy.require('1.9.1')

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout

class MissionController(FloatLayout):
    pass

class TitleScreen(FloatLayout):
    pass

class GameController(FloatLayout):
    pass

class FoxAndGeeseApp(App):
    def build(self):
        return GameController()

if __name__ == '__main__':
    FoxAndGeeseApp().run()
