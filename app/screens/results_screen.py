from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button


class ResultsScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()

        layout = BoxLayout(orientation="vertical", padding=20, spacing=20)

        # Пока фиксированный текст — позже добавим реальные очки
        layout.add_widget(Label(text="Результаты обработки будут здесь"))

        btn_back = Button(text="Назад в меню")
        btn_back.bind(on_press=self.go_menu)

        layout.add_widget(btn_back)
        self.add_widget(layout)

    def go_menu(self, *args):
        self.manager.current = "menu"
