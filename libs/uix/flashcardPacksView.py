# -*- coding: utf-8 -*-
#
# startscreen.py
#
# отображение экрана с флешкартами
#

from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from libs.uix.formattedButton import  PackActionBar
from libs.uix.flashcardPackSettingsView import FlashcardPackSettingsPopup
from libs.uix.screenViewInterface import ScreenViewInterface

class FlashcardPacksView(Screen):
    __metaclass__ = ScreenViewInterface

    """ экран отображает доступные либы/паки с флешкартами"""
    title = "Flashcards packs"
    Builder.load_file('libs/uix/kv/flashcardPacksView.kv')
    #grid_layout = ObjectProperty(None)


    def __init__(self, sreeen_manager, **kvargs):
        super().__init__(**kvargs)
        # для работы с action bar
        self.screen_manager = sreeen_manager
        self.availPacks = []
        self.get_flashcard_pack_setting = None
        self.set_flashcard_pack_setting = None
        self.load_flashcards_packs = None


    def register_get_flashcard_pack_setting(self, callback):
        self.get_flashcard_pack_setting = callback

    def register_set_flashcard_pack_setting(self, callback):
        self.set_flashcard_pack_setting = callback

    def register_load_flashcard_packs_callback(self, callback):
        self.load_flashcards_packs = callback

    def create_flashcard_packs_view(self, packs_list):
        self.availPacks = packs_list
        # очищаем установленные до этого виджеты, чтобы избежать дублирования
        self.ids.pack_names_grid.clear_widgets()
        for pack_name in self.availPacks:
            item_box = BoxLayout(orientation="vertical"  )
            #item_label = FormattedButton(text=pack_name, size_hint=(.6, None), pos_hint={'x':.2})
            item_label = PackActionBar(pack_name=pack_name, main_callback=self.open_flashcards_screen,
                                       setting_callback=self.open_flashcard_pack_setting,
                                       size_hint=(.8, None), pos_hint={'x':.1})
            #item_label.add_child()
            item_box.add_widget(item_label)
            #item_box.add_widget(item_label_shit)
            self.ids.pack_names_grid.add_widget(item_box)
            #print(self.ids.pack_names_grid.children())
            #item_label.bind(self.open_flashcards_screen)

    def open_flashcards_screen(self, event):
        if hasattr(event, 'text') and event.text in self.availPacks:
            self.screen_manager.switch_to_screen('screen_flashcards_view')
            self.screen_manager.set_up_current_screen(event.text)

    def open_flashcard_pack_setting(self, event):
        settingsPopup = FlashcardPackSettingsPopup(self)
        range_list = self.get_flashcard_pack_setting(event.pack_name)
        settingsPopup.open(event.pack_name, range_list)

    def accept_flashcard_pack_settings(self, pack_name, range_value_0, range_value_1):
        self.set_flashcard_pack_setting(pack_name, range_value_0, range_value_1)

    def get_screen_name(self):
        return self.name

    def on_keyboard_down(self, key_name = ''):
        pass

    def on_show_screen(self, event_string = ''):
        self.load_flashcards_packs()