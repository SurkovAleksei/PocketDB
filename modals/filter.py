from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivy.metrics import dp

from widgets.base_modal import BaseModal

OPERATORS = ["=", ">", "<", ">=", "<=", "LIKE"]

class FilterModal(BaseModal):
    def __init__(self, table_name, on_apply=None, **kwargs):
        super().__init__(title="Фильтр", fixed_height=dp(400), **kwargs)
        self.on_apply = on_apply

        self.add_content(MDLabel(text="Поле:", font_style="Body", role="small", size_hint_y=None, height=dp(22)))
        self.f_col = MDTextField(size_hint_y=None, height=dp(48))
        self.add_content(self.f_col)

        self.add_content(MDLabel(text="Оператор (LIKE для текста):", font_style="Body", role="small", size_hint_y=None, height=dp(22)))
        self.f_op = MDTextField(text="LIKE", size_hint_y=None, height=dp(48))
        self.add_content(self.f_op)

        self.add_content(MDLabel(text="Значение:", font_style="Body", role="small", size_hint_y=None, height=dp(22)))
        self.f_val = MDTextField(size_hint_y=None, height=dp(48))
        self.add_content(self.f_val)

        self.add_button("Сброс", style="text", on_release=self.do_reset)
        self.add_button("Применить", style="filled", on_release=self.do_apply)

    def do_apply(self, *args):
        col = self.f_col.text.strip()
        op = self.f_op.text.strip().upper()
        val = self.f_val.text.strip()
        
        self.dismiss()
        if self.on_apply:
            if col and op and val:
                self.on_apply(filters=[(col, op, val)])
            else:
                self.on_apply()

    def do_reset(self, *args):
        self.dismiss()
        if self.on_apply:
            self.on_apply()