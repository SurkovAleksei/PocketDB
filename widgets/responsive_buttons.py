from kivymd.uix.gridlayout import MDGridLayout
from kivy.metrics import dp
from kivy.core.window import Window

class ResponsiveButtons(MDGridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.spacing = dp(8)
        self.padding = [dp(12), dp(8), dp(12), dp(12)]
        self.size_hint_y = None
        self.bind(width=self._on_width_change)
        self._update_layout()

    def _on_width_change(self, instance, value):
        self._update_layout()

    def _update_layout(self):
        w = Window.width
        if w > dp(400):
            self.cols = 3
            self.height = dp(72)
        elif w > dp(280):
            self.cols = 2
            self.height = dp(130)
        else:
            self.cols = 1
            self.height = dp(180)