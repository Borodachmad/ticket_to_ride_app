from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout


class PhotoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation="vertical", padding=20, spacing=20)

        btn_process = Button(text="Обработать тестовое фото")
        btn_process.bind(on_press=self.go_results)

        layout.add_widget(btn_process)
        self.add_widget(layout)

    def go_results(self, *args):
        self.manager.current = "results"
