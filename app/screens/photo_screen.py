from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.properties import StringProperty


class PhotoScreen(Screen):
    selected_file = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation="vertical", padding=20, spacing=20)

        # Кнопка выбора фото
        btn_select = Button(text="Выбрать фото", size_hint=(1, 0.2))
        btn_select.bind(on_press=self.open_file_chooser)
        layout.add_widget(btn_select)

        # Показываем путь выбранного файла
        self.lbl_file = Label(text="Файл не выбран")
        layout.add_widget(self.lbl_file)

        # Кнопка обработки
        self.btn_process = Button(
            text="Обработать фото",
            size_hint=(1, 0.2),
            disabled=True
        )
        self.btn_process.bind(on_press=self.go_results)
        layout.add_widget(self.btn_process)

        self.add_widget(layout)

    def open_file_chooser(self, *args):
        chooser = FileChooserIconView()

        popup = Popup(
            title="Выберите фото",
            content=chooser,
            size_hint=(0.9, 0.9)
        )

        # когда пользователь выбирает файл
        chooser.bind(on_submit=lambda inst, selection, touch:
            self.on_file_selected(selection, popup)
        )

        popup.open()

    def on_file_selected(self, selection, popup):
        if selection:
            self.selected_file = selection[0]
            self.lbl_file.text = f"Выбрано: {self.selected_file}"

            # делаем кнопку активной
            self.btn_process.disabled = False

        popup.dismiss()

    def go_results(self, *args):
        # сохраняем путь в менеджере
        self.manager.get_screen("results").selected_file = self.selected_file
        self.manager.current = "results"
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.properties import StringProperty


class PhotoScreen(Screen):
    selected_file = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation="vertical", padding=20, spacing=20)

        # Кнопка выбора фото
        btn_select = Button(text="Выбрать фото", size_hint=(1, 0.2))
        btn_select.bind(on_press=self.open_file_chooser)
        layout.add_widget(btn_select)

        # Показываем путь выбранного файла
        self.lbl_file = Label(text="Файл не выбран")
        layout.add_widget(self.lbl_file)

        # Кнопка обработки
        self.btn_process = Button(
            text="Обработать фото",
            size_hint=(1, 0.2),
            disabled=True
        )
        self.btn_process.bind(on_press=self.go_results)
        layout.add_widget(self.btn_process)

        self.add_widget(layout)

    def open_file_chooser(self, *args):
        chooser = FileChooserIconView()

        popup = Popup(
            title="Выберите фото",
            content=chooser,
            size_hint=(0.9, 0.9)
        )

        # когда пользователь выбирает файл
        chooser.bind(on_submit=lambda inst, selection, touch:
            self.on_file_selected(selection, popup)
        )

        popup.open()

    def on_file_selected(self, selection, popup):
        if selection:
            self.selected_file = selection[0]
            self.lbl_file.text = f"Выбрано: {self.selected_file}"

            # делаем кнопку активной
            self.btn_process.disabled = False

        popup.dismiss()

    def go_results(self, *args):
        # сохраняем путь в менеджере
        self.manager.get_screen("results").selected_file = self.selected_file
        self.manager.current = "results"
