from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout


class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation="vertical", padding=20, spacing=20)

        btn_photo = Button(text="Загрузить фото маршрутов")
        btn_photo.bind(on_press=self.go_photo)

        layout.add_widget(btn_photo)
        self.add_widget(layout)

    def go_photo(self, *args):
        self.manager.current = "photo"
