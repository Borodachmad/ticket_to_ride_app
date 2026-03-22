from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty

from score_calc import process_image

# Перевод цветов игроков на русский
COLOR_NAMES = {
    "red": "Красный",
    "yellow": "Жёлтый",
    "blue": "Синий",
    "green": "Зелёный",
    "black": "Чёрный",
}


class ResultsScreen(Screen):
    selected_file = StringProperty("")

    def on_pre_enter(self):
        self.clear_widgets()

        root = BoxLayout(orientation="vertical", padding=20, spacing=10)

        # Заголовок
        root.add_widget(
            Label(
                text="Результаты анализа",
                size_hint=(1, 0.1),
                font_size="22sp",
                bold=True,
            )
        )

        # Файл
        filename = self.selected_file.split("/")[-1] if "/" in self.selected_file else self.selected_file
        root.add_widget(
            Label(text=f"Фото: {filename}", size_hint=(1, 0.05), font_size="14sp")
        )

        # Обрабатываем изображение
        result = process_image(self.selected_file)

        if not result["success"]:
            root.add_widget(
                Label(
                    text=f"Ошибка: {result['error']}",
                    size_hint=(1, 0.7),
                    font_size="18sp",
                    color=(1, 0.3, 0.3, 1),
                )
            )
        else:
            # Скроллируемая область с результатами
            scroll = ScrollView(size_hint=(1, 0.7))
            content = BoxLayout(
                orientation="vertical",
                spacing=10,
                size_hint_y=None,
                padding=[0, 10, 0, 10],
            )
            content.bind(minimum_height=content.setter("height"))

            players = result.get("players", {})

            if not players:
                content.add_widget(
                    Label(
                        text="Вагончики не обнаружены.\nПопробуйте другое фото.",
                        size_hint_y=None,
                        height=80,
                        font_size="18sp",
                    )
                )
            else:
                # Сортируем по очкам (лидер сверху)
                sorted_players = sorted(
                    players.items(), key=lambda x: x[1]["score"], reverse=True
                )

                for color, data in sorted_players:
                    name = COLOR_NAMES.get(color, color)
                    score = data["score"]
                    routes_count = data["routes_count"]
                    segments = data["segments"]

                    # Блок игрока
                    player_box = BoxLayout(
                        orientation="vertical",
                        size_hint_y=None,
                        height=90,
                        padding=[10, 5, 10, 5],
                    )

                    player_box.add_widget(
                        Label(
                            text=f"[b]{name}[/b]  —  {score} очков",
                            markup=True,
                            font_size="20sp",
                            size_hint_y=None,
                            height=35,
                            halign="left",
                            text_size=(None, None),
                        )
                    )

                    # Детали маршрутов
                    routes_detail = []
                    for r in data["routes"]:
                        routes_detail.append(f"{r['wagons']} ваг. (+{r['score']})")
                    routes_str = ", ".join(routes_detail) if routes_detail else "—"

                    player_box.add_widget(
                        Label(
                            text=f"Маршрутов: {routes_count}  |  Вагонов: {segments}",
                            font_size="14sp",
                            size_hint_y=None,
                            height=25,
                            halign="left",
                        )
                    )
                    player_box.add_widget(
                        Label(
                            text=f"Маршруты: {routes_str}",
                            font_size="13sp",
                            size_hint_y=None,
                            height=25,
                            halign="left",
                        )
                    )

                    content.add_widget(player_box)

                # Итого
                total = sum(p["score"] for p in players.values())
                content.add_widget(
                    Label(
                        text=f"\nВсего обнаружено вагонов: {result['total_segments']}",
                        size_hint_y=None,
                        height=40,
                        font_size="15sp",
                    )
                )

            scroll.add_widget(content)
            root.add_widget(scroll)

        # Кнопки навигации
        btn_box = BoxLayout(
            orientation="horizontal", size_hint=(1, 0.1), spacing=10
        )
        btn_back = Button(text="← Назад")
        btn_back.bind(on_press=self.go_back)
        btn_menu = Button(text="В меню")
        btn_menu.bind(on_press=self.go_menu)
        btn_box.add_widget(btn_back)
        btn_box.add_widget(btn_menu)
        root.add_widget(btn_box)

        self.add_widget(root)

    def go_back(self, *args):
        self.manager.current = "photo"

    def go_menu(self, *args):
        self.manager.current = "menu"
