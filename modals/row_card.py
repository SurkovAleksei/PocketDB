from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.metrics import dp

import db
from widgets.base_modal import BaseModal, notify
from modals.edit_row import EditRowModal

class RowCardModal(BaseModal):
    def __init__(self, table_name, row, on_changed=None, **kwargs):
        super().__init__(title=f"Запись #{row['id']}", fixed_height=dp(400), **kwargs)
        self.table_name = table_name
        self.row = row
        self.on_changed = on_changed

        for k, v in row.items():
            if k == "created_at": continue
            line = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(28), spacing=dp(8))
            line.add_widget(MDLabel(text=f"{k}:", font_style="Body", role="small", size_hint_x=0.4))
            line.add_widget(MDLabel(text=db.format_value(v), font_style="Body", role="medium", size_hint_x=0.6))
            self.add_content(line)

        self.add_button("Удалить", style="outlined", on_release=lambda x: ConfirmDeleteModal(on_confirm=self.do_delete).open())
        self.add_button("Изменить", style="filled", on_release=lambda x: self.edit())
        self.add_button("Закрыть", style="text", on_release=lambda x: self.dismiss())

    def do_delete(self):
        try: db.delete_row(self.table_name, self.row["id"])
        except Exception as e: return notify(str(e), is_error=True)
        self.dismiss()
        if self.on_changed: self.on_changed()

    def edit(self):
        table = db.get_table(self.table_name)
        if not table: return notify("Таблица не найдена", is_error=True)
        self.dismiss()
        EditRowModal(table_name=self.table_name, table=table, row=self.row, on_saved=self.on_changed).open()

class ConfirmDeleteModal(BaseModal):
    def __init__(self, on_confirm=None, **kwargs):
        super().__init__(title="Удалить запись?", fixed_height=dp(240), **kwargs)
        self.add_content(MDLabel(text="Это действие нельзя отменить.", halign="center", size_hint_y=None, height=dp(60)))

        def do_confirm(*args):
            self.dismiss()
            if on_confirm: on_confirm()

        self.add_button("Отмена", style="text", on_release=lambda x: self.dismiss())
        self.add_button("Удалить", style="filled", on_release=do_confirm)