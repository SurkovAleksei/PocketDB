import json
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivy.metrics import dp
from widgets.validators import validate_field
import datetime
import re

import db
from widgets.base_modal import BaseModal, notify

class AddRowModal(BaseModal):
    def __init__(self, table_name, table, on_created=None, **kwargs):
        super().__init__(title=f"Добавить в «{table['display_name']}»", fixed_height=dp(500), **kwargs)
        self.table_name = table_name
        self.on_created = on_created
        self.columns = json.loads(table["columns"])

        self.fields = {}
        for col in self.columns:
            self.add_content(MDLabel(text=f"{col['name']} ({col['type']})", font_style="Body", role="small", size_hint_y=None, height=dp(22)))
            f = MDTextField(hint_text=col["name"], size_hint_y=None, height=dp(48))
            self.fields[col["name"]] = f
            self.add_content(f)

        self.add_button("Отмена", style="text", on_release=lambda x: self.dismiss())
        self.add_button("Сохранить", style="filled", on_release=lambda x: self.do_save())

    def do_save(self):
        data = {}
        for col in self.columns:
            name, ctype = col["name"], col["type"]
            ok, val, err = validate_field(ctype, self.fields[name].text)
            if not ok:
                notify(f"{name}: {err}", is_error=True)
                return
            data[name] = val

        try:
            db.add_row(self.table_name, data)
        except Exception as e:
            notify(str(e), is_error=True)
            return

        self.dismiss()
        if self.on_created: self.on_created()