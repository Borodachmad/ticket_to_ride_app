from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty

from score_calc import process_image


class ResultsScreen(Screen):
    selected_file = StringProperty("")

    def on_pre_enter(self):
        self.clear_widgets()

        layout = BoxLayout(orientation="vertical", padding=20, spacing=20)

        layout.add_widget(Label(text=f"Файл: {self.selected_file}"))

        # Обрабатываем изображение
        result = process_image(self.selected_file)

        if not result["success"]:
            layout.add_widget(Label(text=f"Ошибка: {result['error']}"))
        else:
            layout.add_widget(
                Label(
                    text=(
                        "Обработано!\n"
                        f"Ширина: {result['width']}\n"
                        f"Высота: {result['height']}\n"
                    )
                )
            )

        self.add_widget(layout)
