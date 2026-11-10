from kivy.uix.modalview import ModalView
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.label import MDLabel
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.utils import get_color_from_hex

WHITE = get_color_from_hex("#FFFFFF")
ERROR = get_color_from_hex("#D32F2F")
INFO = get_color_from_hex("#1976D2")

class BaseModal(ModalView):
    def __init__(self, title="", fixed_height=None, **kwargs):
        super().__init__(
            size_hint=(0.95, None),
            height=fixed_height or dp(500),
            auto_dismiss=False,
            background_color=(0, 0, 0, 0.7),
            **kwargs
        )
        
        # Используем MDCard вместо MDBoxLayout для белого фона
        self.root_box = MDCard(
            orientation="vertical", 
            spacing=dp(12), 
            padding=dp(16),
            radius=[dp(12)],
            md_bg_color=WHITE,
            elevation=4
        )

        if title:
            self.root_box.add_widget(MDLabel(
                text=title, font_style="Headline", role="small", size_hint_y=None, height=dp(40)
            ))

        self.scroll = ScrollView()
        self.content_box = MDBoxLayout(
            orientation="vertical", spacing=dp(12), size_hint_y=None, padding=[0, 0, 0, dp(8)]
        )
        self.content_box.bind(minimum_height=self.content_box.setter("height"))
        self.scroll.add_widget(self.content_box)
        self.root_box.add_widget(self.scroll)

        self.buttons_box = MDBoxLayout(
            orientation="horizontal", size_hint_y=None, height=dp(48), spacing=dp(8)
        )
        self.root_box.add_widget(self.buttons_box)
        self.add_widget(self.root_box)

    def add_content(self, widget):
        self.content_box.add_widget(widget)

    def add_button(self, text, style="text", on_release=None):
        btn = MDButton(MDButtonText(text=text), style=style, on_release=on_release)
        self.buttons_box.add_widget(btn)
        return btn

_notify_modal = None

def notify(text, is_error=False):
    global _notify_modal
    if _notify_modal:
        _notify_modal.dismiss()
    
    color = ERROR if is_error else INFO
    title = "Ошибка" if is_error else "Сообщение"
    
    m = BaseModal(fixed_height=dp(200))
    m.add_content(MDLabel(
        text=title, theme_text_color="Custom", text_color=color,
        font_style="Headline", role="small", size_hint_y=None, height=dp(30)
    ))
    m.add_content(MDLabel(
        text=str(text), halign="center", size_hint_y=None, height=dp(60)
    ))
    m.add_button("OK", style="filled", on_release=lambda x: m.dismiss())
    _notify_modal = m
    m.open()