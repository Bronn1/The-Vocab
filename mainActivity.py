# -*- coding: utf-8 -*-
#
# mainActivity.py
#
# Runs  application
#
from kivymd.app import MDApp
from kivy.core.window import Window, Keyboard
from kivy.config import Config
from kivy.utils import platform

from libs.uix.startingScreenView import StartingScreenView
from libs.uix.flashcardPlayerView import FlashcardsPlayerView
from libs.uix.flashcardPacksView import FlashcardPacksView
from libs.uix.flashcardEditorView import FlashcardEditorView
from libs.presenters.flashcardPacksPresenter import FlashcardPacksPresenter
from libs.presenters.flashcardPlayerPresenter import FlashcardPlayerPresenter
from libs.presenters.flashcardEditorPresenter import FlashcardEditorPresenter
from libs.model.flashcardModel import FlashcardModel
from libs.common.appSettings import AppSettings
from libs.uix.customScreenManager import CustomScreenManager
from upgrade.upgrade_db import Upgrade_db


class MainActivity(MDApp):
    """
    Main application class. Create screen views and presenters.
    Initializes Screen Manager
    Updates DB version if needed

    :Events:
        `on_action_previous`: *event
            Fired when previous button is pressed on the action bar
         `_on_keyboard_down`: keyboard, keycode, tex
            Fired when a  key is pressed(passes an event to currently active screen)
    """

    title = "TheVocab b1.1.1"
    icon = ""
    screensViewStack = ["startScreen"]

    def __init__(self, **kvargs):
        super(MainActivity, self).__init__(**kvargs)
        # bind keyboard events to the handler
        Window.bind(on_key_up=self._on_keyboard_down)
        self._VERSION = 'b1.1.1'
        self._set_defaults_config_setting_if_not_exist()

        font_size = 16
        if platform == 'android':
            font_size = 33

        self._update_db()
        self.model = FlashcardModel(self.user_data_dir, debug=AppSettings.Debug)
        self.learned_words_counter = -1

        # creating all screen  views and presenters for them
        self.starting_screen = StartingScreenView()
        self.starting_screen.action_previous.bind(on_press=self.on_action_previous)
        self.flashcard_player_view = FlashcardsPlayerView(font_size)
        self.flashcard_player_presenter = FlashcardPlayerPresenter(self.model, self.flashcard_player_view)
        self.flashcard_packs_view = FlashcardPacksView(self.starting_screen.screen_manager)
        self.flashcard_packs_presenter = FlashcardPacksPresenter(self.model, self.flashcard_packs_view)
        self.flashcard_editor_view = FlashcardEditorView()
        self.edit_packs_presenter = FlashcardEditorPresenter(self.model, self.flashcard_editor_view)

        # adding screens to Screen manager
        self.starting_screen.screen_manager.add_widget(self.flashcard_packs_view)
        self.starting_screen.screen_manager.add_widget(self.flashcard_editor_view)
        self.starting_screen.screen_manager.add_widget(self.flashcard_player_view)

        self._make_view_setup_by_user_settings()

    def _make_view_setup_by_user_settings(self):
        """
        making up views state according to previously picked user setting
        :return:
        """
        Window.release_all_keyboards()
        if Config.get('FlashcardView', 'HideTranslate') == 'True':
            self.flashcard_player_view.on_hide_translate_sentence_checkbox(True)
        if Config.get('FlashcardView', 'MutedSound') == 'True':
            self.flashcard_player_view.on_change_sound_state()
        counter = Config.get('FlashcardActionBar', 'LearnedWords')
        # TODO additional presenter for action bar  to get rid of side effects
        if counter != "-1":
            self.learned_words_counter = counter
        else:
            self.learned_words_counter = self.model.count_learned_words()
            Config.set('FlashcardActionBar', 'LearnedWords', self.learned_words_counter)
            Config.write()
        self.starting_screen.ids.label_hint.text = "Learned words " + str(self.learned_words_counter)

    def _set_defaults_config_setting_if_not_exist(self):
        """
        setting up some required config values
        :return:
        """
        Config.setdefaults('TheVocabApp', {'Version': 'b1.1.0'})
        Config.setdefaults('FlashcardView', { 'HideTranslate': 'False' })
        Config.setdefaults('FlashcardView', { 'MutedSound': 'False' })
        Config.setdefaults('FlashcardActionBar', {'LearnedWords': -1})

    def _update_db(self):
        """
        updates DB file according to current version if needed
        :return:
        """
        if Config.get('TheVocabApp', 'Version') != self._VERSION:
            if self._VERSION == 'b1.1.1':
                Upgrade_db.replace_db_file_b1_1_1(self.user_data_dir)
                Config.set('TheVocabApp', 'Version', str(self._VERSION))
                Config.write()

    def build(self):
        return self.starting_screen

    def on_resume(self):
        Window.release_all_keyboards()
        self.starting_screen.screen_manager.current_screen.on_keyboard_down('')

    def on_action_previous(self,  *event):
        """
        event called when previous button is pressed
        switching up to previously opened screen
        :param event:
        :return:
        """
        self.starting_screen.screen_manager.switch_to_previous_screen()
        Window.release_all_keyboards()
        self.starting_screen.screen_manager.set_up_current_screen()

    def _on_keyboard_down(self, keyboard, keycode, text):
        """
        keyboard events handler, passes an event to currently active screen
        :param keyboard:
        :param keycode: code of pressed key
        :param text:
        :return:
        """
        self.starting_screen.screen_manager.current_screen.on_keyboard_down(Keyboard().keycode_to_string(keycode))

        return True
