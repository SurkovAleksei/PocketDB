from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.textfield import MDTextField
from kivy.uix.spinner import Spinner
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.utils import get_color_from_hex

FIELD_TYPES = ["Текст", "Число", "Дата", "Время", "Да/Нет"]
BG_COLOR = get_color_from_hex("#E8E8F2")
TEXT_COLOR = get_color_from_hex("#2A2A55")

class ColoredSpinner(Spinner):
    def __init__(self, **kwargs):
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_down", "")
        kwargs.setdefault("background_color", (0, 0, 0, 0))
        kwargs.setdefault("color", TEXT_COLOR)
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(rgba=BG_COLOR)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(8)])
        self.bind(pos=self._update_bg, size=self._update_bg)

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

class FieldRow(MDBoxLayout):
    def __init__(self, on_delete=None, **kwargs):
        super().__init__(orientation="horizontal", size_hint_y=None, height=dp(56), spacing=dp(8), **kwargs)
        self.selected_type = FIELD_TYPES[0]

        self.type_spinner = ColoredSpinner(
            text=FIELD_TYPES[0], values=FIELD_TYPES, size_hint=(None, None),
            size=(dp(110), dp(48)), pos_hint={"center_y": 0.5}
        )
        self.type_spinner.bind(text=lambda i, v: setattr(self, "selected_type", v))
        self.add_widget(self.type_spinner)

        self.name_field = MDTextField(
            hint_text="Имя поля", size_hint=(1, None), height=dp(48), pos_hint={"center_y": 0.5}
        )
        self.add_widget(self.name_field)

        self.del_btn = MDIconButton(
            icon="close", size_hint=(None, None), size=(dp(48), dp(48)),
            pos_hint={"center_y": 0.5}, on_release=lambda x: on_delete(self) if on_delete else None
        )
        self.add_widget(self.del_btn)

    def get_data(self):
        return {"name": self.name_field.text.strip(), "type": self.selected_type}