from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout
from kivy.clock import Clock
from kivy.animation import Animation

class PackActionBar(RelativeLayout):
    Builder.load_file('libs/uix/kv/formattedButton.kv')
    def __init__(self, pack_name, main_callback, setting_callback, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pack_name = pack_name
        self.main_button_callback = main_callback
        self.ids.float_button.ids.setting_button.bind(on_press=setting_callback)
        self.ids.float_button.ids.setting_button.pack_name = pack_name
        self.ids.main_button.bind(on_press=main_callback)

    def breath(self, dtx):
        button_breath_animation = Animation(btn_size=(44,44),t='in_quad', duration=.5) +\
               Animation(btn_size=(48,48),t='in_quad', duration=.5)
        button_breath_animation.start(self.ids.float_button)

class FormattedButton(Button):
    Builder.load_file('libs/uix/kv/formattedButton.kv')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)