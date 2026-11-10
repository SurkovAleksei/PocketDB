from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.utils import get_color_from_hex
from kivy.core.window import Window

import db
from screens.tables import TablesScreen
from screens.rows import RowsScreen

BG_COLOR = get_color_from_hex("#D9D9D9")

class AnyTableApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"

        db.init_db()
        self.sm = MDScreenManager()

        tables = TablesScreen(name="tables")
        t_layout = MDBoxLayout(orientation="vertical")
        t_layout.md_bg_color = BG_COLOR
        tables.add_widget(t_layout)
        tables.ids.container = t_layout

        rows = RowsScreen(name="rows")
        r_layout = MDBoxLayout(orientation="vertical")
        r_layout.md_bg_color = BG_COLOR
        rows.add_widget(r_layout)
        rows.ids.container = r_layout

        self.sm.add_widget(tables)
        self.sm.add_widget(rows)

        Window.bind(on_keyboard=self._on_keyboard)
        return self.sm

    def _on_keyboard(self, window, key, *args):
        if key == 27 and self.sm.current == "rows":
            self.sm.current = "tables"
            return True
        return False

if __name__ == "__main__":
    AnyTableApp().run()