from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDListItem, MDListItemHeadlineText, MDListItemSupportingText
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.utils import get_color_from_hex

import db
from modals.create_table import CreateTableModal
from widgets.base_modal import BaseModal, notify

BG = get_color_from_hex("#D9D9D9")
LIST_BG = get_color_from_hex("#CFCFCF")
LONG_PRESS_TIME = 0.7

class TablesScreen(MDScreen):
    def on_enter(self):
        self.refresh()

    def refresh(self):
        self.md_bg_color = BG
        container = self.ids.container
        container.clear_widgets()
        container.md_bg_color = BG

        tables = db.get_tables()
        top_zone = MDBoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(4), padding=[dp(8), dp(8), dp(8), dp(8)])
        top_zone.bind(minimum_height=top_zone.setter("height"))
        top_zone.md_bg_color = BG

        if not tables:
            top_zone.add_widget(MDLabel(text="Таблиц пока нет", halign="center", font_style="Headline", role="medium", size_hint_y=None, height=dp(60)))
        else:
            for t in tables:
                item = MDListItem(md_bg_color=LIST_BG, size_hint_y=None, height=dp(64))
                item.add_widget(MDListItemHeadlineText(text=t["display_name"]))
                item.add_widget(MDListItemSupportingText(text=t["name"]))
                item.table_name = t["name"]
                item.display_name = t["display_name"]
                item._long_fired = False
                
                # Привязываем долгий тап
                item.bind(on_touch_down=self._on_touch_down)
                item.bind(on_touch_up=self._on_touch_up)
                
                # ДОБАВЛЯЕМ ОБЫЧНЫЙ КЛИК (открытие таблицы)
                item.bind(on_release=lambda x, name=t["name"]: self.open_table(name))
                
                top_zone.add_widget(item)

        scroll = ScrollView()
        scroll.add_widget(top_zone)
        container.add_widget(scroll)

        bottom_zone = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(72), spacing=dp(8), padding=[dp(12), dp(8), dp(12), dp(12)])
        bottom_zone.md_bg_color = BG
        bottom_zone.add_widget(MDButton(MDButtonText(text="Добавить таблицу"), style="filled", on_release=lambda x: self.show_create()))
        bottom_zone.add_widget(MDButton(MDButtonText(text="Заглушка"), style="outlined", on_release=lambda x: notify("В разработке")))
        container.add_widget(bottom_zone)

    def _on_touch_down(self, item, touch):
        if not item.collide_point(*touch.pos): return
        if "_long_event" in touch.ud: touch.ud["_long_event"].cancel()
        item._long_fired = False
        touch.ud["_long_event"] = Clock.schedule_once(lambda dt: self._on_long_press(item), LONG_PRESS_TIME)

    def _on_touch_up(self, item, touch):
        if "_long_event" in touch.ud:
            touch.ud["_long_event"].cancel()
            touch.ud.pop("_long_event", None)
        if getattr(item, "_long_fired", False):
            item._long_fired = False
            return True

    def _on_long_press(self, item):
        item._long_fired = True
        ConfirmDeleteTableModal(item.table_name, item.display_name, on_confirm=self.refresh).open()

    def open_table(self, name):
        screen = self.manager.get_screen("rows")
        screen.table_name = name
        self.manager.current = "rows"

    def show_create(self):
        CreateTableModal(on_created=self.refresh).open()

class ConfirmDeleteTableModal(BaseModal):
    def __init__(self, table_name, display_name, on_confirm=None, **kwargs):
        super().__init__(title=f"Удалить «{display_name}»?", fixed_height=dp(240), **kwargs)
        self.table_name = table_name
        self.on_confirm = on_confirm
        self.add_content(MDLabel(text="Все записи будут удалены безвозвратно.", halign="center", size_hint_y=None, height=dp(60)))

        def do_confirm(*args):
            try: db.delete_table(self.table_name)
            except Exception as e: notify(str(e), is_error=True)
            self.dismiss()
            if self.on_confirm: self.on_confirm()

        self.add_button("Отмена", style="text", on_release=lambda x: self.dismiss())
        self.add_button("Удалить", style="filled", on_release=do_confirm)