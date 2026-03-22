from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label


class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation="vertical", padding=40, spacing=20)

        # Заголовок
        layout.add_widget(
            Label(
                text="Ticket to Ride\nПодсчёт очков",
                font_size="28sp",
                halign="center",
                size_hint=(1, 0.4),
            )
        )

        btn_photo = Button(
            text="Загрузить фото игрового поля",
            size_hint=(1, 0.2),
            font_size="18sp",
        )
        btn_photo.bind(on_press=self.go_photo)
        layout.add_widget(btn_photo)

        # Описание
        layout.add_widget(
            Label(
                text="Сфотографируйте поле после партии.\n"
                     "Приложение найдёт вагончики каждого\n"
                     "игрока и посчитает очки.",
                font_size="14sp",
                halign="center",
                size_hint=(1, 0.3),
            )
        )

        self.add_widget(layout)

    def go_photo(self, *args):
        self.manager.current = "photo"
