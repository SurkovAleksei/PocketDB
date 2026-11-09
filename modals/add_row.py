import json
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivy.metrics import dp
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

    def _validate(self, ctype, raw):
        ctype, raw = str(ctype).strip().lower(), raw.strip()
        if not raw: return True, "", None

        if ctype == "число":
            try:
                val = float(raw.replace(",", "."))
                return True, (int(val) if val.is_integer() else val), None
            except ValueError:
                return False, None, "не число"

        if ctype == "да/нет":
            low = raw.lower()
            if low in ("1", "да", "yes", "true", "+"): return True, 1, None
            if low in ("0", "нет", "no", "false", "-"): return True, 0, None
            return False, None, "введите да/нет"

        if ctype == "дата":
            for fmt in ("%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d"):
                try: return True, datetime.datetime.strptime(raw, fmt).strftime("%Y-%m-%d"), None
                except ValueError: pass
            return False, None, "формат ДД.ММ.ГГГГ"

        if ctype == "время":
            raw = raw.replace(".", ":")
            if ":" not in raw and len(raw) == 4: raw = raw[:2] + ":" + raw[2:]
            if re.match(r'^\d{1,2}:\d{2}$', raw):
                h, m = raw.split(":")
                return True, f"{int(h):02d}:{m}", None
            return False, None, "формат ЧЧ:ММ"

        return True, raw, None

    def do_save(self):
        data = {}
        for col in self.columns:
            name, ctype = col["name"], col["type"]
            ok, val, err = self._validate(ctype, self.fields[name].text)
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