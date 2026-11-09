from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDListItem, MDListItemHeadlineText
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty
from kivy.metrics import dp
from kivy.utils import get_color_from_hex

import db
from modals.add_row import AddRowModal
from modals.filter import FilterModal
from modals.row_card import RowCardModal
from widgets.base_modal import notify

BG = get_color_from_hex("#D9D9D9")
LIST_BG = get_color_from_hex("#CFCFCF")
FILTER_COLOR = get_color_from_hex("#1976D2")

class RowsScreen(MDScreen):
    table_name = StringProperty("")
    display_name = StringProperty("")
    active_filters = StringProperty("")

    def on_enter(self):
        self.refresh()

    def refresh(self, filters=None, order_by=None):
        self.md_bg_color = BG
        container = self.ids.container
        container.clear_widgets()
        container.md_bg_color = BG

        table = db.get_table(self.table_name)
        self.display_name = table["display_name"] if table else self.table_name

        if filters:
            parts = [f"{k} {op} {v}" for k, op, v in filters]
            self.active_filters = "И: " + ", ".join(parts)
        else:
            self.active_filters = ""

        top_height = dp(70) if self.active_filters else dp(50)
        top_bar = MDBoxLayout(orientation="vertical", size_hint=(1, None), height=top_height, spacing=dp(2), padding=[dp(12), dp(4), dp(12), 0])
        top_bar.md_bg_color = BG

        title_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40), spacing=dp(8))
        title_row.add_widget(MDLabel(text=self.display_name, font_style="Headline", role="small", valign="middle", size_hint_y=None, height=dp(40)))
        title_row.add_widget(MDButton(MDButtonText(text="Фильтр"), style="text", size_hint=(None, None), size=(dp(90), dp(36)), pos_hint={"center_y": 0.5}, on_release=lambda x: self.show_filter()))
        top_bar.add_widget(title_row)

        if self.active_filters:
            top_bar.add_widget(MDLabel(text=self.active_filters, font_style="Body", role="small", theme_text_color="Custom", text_color=FILTER_COLOR, size_hint_y=None, height=dp(22), valign="middle"))

        container.add_widget(top_bar)

        try:
            rows = db.get_rows(self.table_name, filters=filters, order_by=order_by)
        except Exception as e:
            notify(str(e), is_error=True)
            rows = []

        list_zone = MDBoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(4), padding=[dp(8), dp(8), dp(8), dp(8)])
        list_zone.bind(minimum_height=list_zone.setter("height"))
        list_zone.md_bg_color = BG

        if not rows:
            item = MDListItem(md_bg_color=LIST_BG, size_hint_y=None, height=dp(56))
            item.add_widget(MDListItemHeadlineText(text="Нет записей"))
            list_zone.add_widget(item)
        else:
            for r in rows:
                parts = [f"#{r['id']}"]
                for k, v in r.items():
                    if k not in ("id", "created_at"):
                        parts.append(f"{k}: {db.format_value(v)}")
                text = " | ".join(parts)
                item = MDListItem(md_bg_color=LIST_BG, size_hint_y=None, height=dp(56), on_release=lambda x, row=r: self.open_row(row))
                item.add_widget(MDListItemHeadlineText(text=text))
                list_zone.add_widget(item)

        scroll = ScrollView()
        scroll.add_widget(list_zone)
        container.add_widget(scroll)

        bottom_zone = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(72), spacing=dp(8), padding=[dp(12), dp(8), dp(12), dp(12)])
        bottom_zone.md_bg_color = BG
        bottom_zone.add_widget(MDButton(MDButtonText(text="Назад"), style="outlined", on_release=lambda x: self.go_back()))
        bottom_zone.add_widget(MDButton(MDButtonText(text="Добавить"), style="filled", on_release=lambda x: self.show_add()))
        container.add_widget(bottom_zone)

    def go_back(self):
        self.manager.current = "tables"

    def open_row(self, row):
        RowCardModal(table_name=self.table_name, row=row, on_changed=self.refresh).open()

    def show_filter(self):
        FilterModal(table_name=self.table_name, on_apply=self.refresh).open()

    def show_add(self):
        table = db.get_table(self.table_name)
        if table: AddRowModal(table_name=self.table_name, table=table, on_created=self.refresh).open()