from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from app.screens.menu_screen import MenuScreen
from app.screens.photo_screen import PhotoScreen
from app.screens.results_screen import ResultsScreen


class TTRApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name="menu"))
        sm.add_widget(PhotoScreen(name="photo"))
        sm.add_widget(ResultsScreen(name="results"))
        return sm


if __name__ == "__main__":
    TTRApp().run()
