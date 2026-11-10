from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText
from kivy.metrics import dp

import db
from widgets.base_modal import BaseModal, notify
from widgets.field_row import FieldRow

class CreateTableModal(BaseModal):
    def __init__(self, on_created=None, **kwargs):
        super().__init__(title="Новая таблица", fixed_height=dp(520), **kwargs)
        self.on_created = on_created

        self.add_content(MDLabel(text="Название таблицы:", font_style="Body", role="small", size_hint_y=None, height=dp(22)))
        self.f_display = MDTextField(hint_text="Например: Расписание", size_hint_y=None, height=dp(48))
        self.add_content(self.f_display)

        self.add_content(MDLabel(text="Поля таблицы:", font_style="Body", role="small", size_hint_y=None, height=dp(22)))
        self.fields_box = MDBoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6))
        self.fields_box.bind(minimum_height=self.fields_box.setter("height"))
        self.add_content(self.fields_box)

        self.add_row()
        self.add_content(MDButton(MDButtonText(text="+ Поле"), style="outlined", size_hint=(None, None), size=(dp(130), dp(40)), on_release=lambda x: self.add_row()))
        self.add_button("Отмена", style="text", on_release=lambda x: self.dismiss())
        self.add_button("Создать", style="filled", on_release=lambda x: self.do_create())

    def add_row(self):
        self.fields_box.add_widget(FieldRow(on_delete=lambda r: self.fields_box.remove_widget(r)))

    def do_create(self):
        display = self.f_display.text.strip()
        if not display:
            return notify("Введите название", is_error=True)

        columns = []
        for child in self.fields_box.children[::-1]:
            if isinstance(child, FieldRow):
                data = child.get_data()
                if not data["name"]: continue
                try: db.safe_name(data["name"])
                except ValueError as e: return notify(str(e), is_error=True)
                columns.append(data)

        if not columns:
            return notify("Добавьте поле", is_error=True)

        try:
            db.create_table(display, columns)
        except Exception as e:
            return notify(str(e), is_error=True)

        self.dismiss()
        if self.on_created: self.on_created()