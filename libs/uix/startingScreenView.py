# -*- coding: utf-8 -*-
#
# startscreenView.py
#
# Starting app screen
#

from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.button import Button
from libs.uix.screenViewInterface import ScreenViewInterface
from kivy.uix.screenmanager import  FadeTransition, WipeTransition

#CustomScreenManager.screlibs/uix/.py
class ImageButton(ButtonBehavior, Image):
    pass


class StartingScreenView(BoxLayout):
    __metaclass__ = ScreenViewInterface

    events_callback = ObjectProperty(None)

    """цвет виджета пока единственный и основной"""
    # TODO add common constans for colors
    color_blue = ListProperty([0.1607843137254902, 0.34901960784313724, 0.6784313725490196])

    """ грузим макет интерфейса"""
    Builder.load_file("libs/uix/kv/startingScreenView.kv")

    def __init__(self, **kvargs):
        super().__init__(**kvargs)
        self.orientation = "vertical"
        self.screen_name = "startScreen"
        self.screen_manager = self.ids.screen_manager
        self.action_previous = self.ids.action_previous
        self.screen_manager.transition = WipeTransition(duration=.25)
        self.ids.starting_screen.on_show_screen = self.on_show_screen
        self.ids.starting_screen.on_keyboard_down = self.on_keyboard_down


    def menu_buttons_view(self):
        name_path_buttons_menu = {
            "create lib": "data/images/test-img.png",
            "play flashcards": "data/images/test-img.png"}

        for name_button in name_path_buttons_menu.keys():
            item_box = BoxLayout(orientation="vertical", size_hint=[.9, .9])
            item_label = Button(text=name_button, id=name_button, on_press=self.events_callback)
            item_button = \
                ImageButton(source=name_path_buttons_menu[name_button], id=name_button,
                            on_press=self.events_callback)
            item_box.add_widget(item_button)
            item_box.add_widget(item_label)
            self.ids.menu_buttons.add_widget(item_box)

    def on_switch_screen_buttons(self, screen_name):
        self.screen_manager.switch_to_screen(screen_name)
        self.screen_manager.set_up_current_screen()

    def get_screen_name(self):
        return self.ids.starting_screen.name

    def on_keyboard_down(self, key_name = ''):
        pass

    def on_show_screen(self, event_string = ''):
        pass
