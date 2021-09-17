# -*- coding: utf-8 -*-
#
# libs/uix/flashcardEditorView.py
#
# view for editing/adding flashcards(including two popups view for picking flashcards
# and flashcard editor)

from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from libs.uix.formattedButton import FormattedButton
from libs.uix.screenViewInterface import ScreenViewInterface

class PopupLabelCell(Label):
    pass


class PickExistingFlashcardPopup(Popup):

    def __init__(self, parent_popup, **kwargs):
        super(PickExistingFlashcardPopup, self).__init__(**kwargs)
        self.parent_popup = parent_popup
        self.flashcards_list = []

    def open(self, flashcards_list):
        self.flashcards_list = flashcards_list
        self.existing_flashcards_view()
        super().open()

    def existing_flashcards_view(self):
        """
        showing all list of all available flashcards to edit
        :return:
        """
        self.ids.flashcards_view.clear_widgets()
        for flashcard_word in self.flashcards_list:
            # we'll allow to edit only user created flashcards
            if flashcard_word.is_user_added == 1:
                button_view = FormattedButton(text=flashcard_word.word)
                button_view.bind(on_press=self.parent_popup.on_edit_picked_flashcard_pressed)
                self.ids.flashcards_view.add_widget(button_view)
            # layout.add_widget(button_view)
        # self.ids.flashcard_player_view.add_widget(layout)
        # s = "Button: %s"i
        # for i in range(30):
        #    hey = s % (i)
        #    self.ids.flashcard_player_view.add_widget(Button(text=hey))


class FlashcardEditorPopup(Popup):

    def __init__(self, obj, **kwargs):
        super(FlashcardEditorPopup, self).__init__(**kwargs)
        self.parent_screen = obj
        self.flashcard_pack_name = ""
        self.starting_view_state()
        self.flashcard_editor_fields_view()
        self.existing_flashcard_popup = PickExistingFlashcardPopup(self)
        self.flashcard_id = None
        self.is_edit_existing_flashcard_pressed = False

    def open(self, flashcard_pack_name):
        self.clear_views()
        self.flashcard_pack_name = flashcard_pack_name
        self.starting_view_state()
        super().open()
        # self.ids.save_button.bind(on_press=lambda x: self.parent_screen.add_flashcard_pressed_callback())

    def starting_view_state(self):
        """
        Method sets  buttons state when view  has been opened(initial state of view)
        :return:
        """
        self.ids.save_button.visible = False
        self.ids.cancel_button.visible = False
        self.ids.error_label.visible = False
        self.ids.edit_button.visible = True
        self.ids.add_button.visible = True
        self.ids.container.visible = False

    def flashcard_editor_view_state(self, *args):
        """
        Method sets  buttons state when edit/add flashcard has been clicked
        :param args:
        :return:
        """
        self.ids.save_button.visible = True
        self.ids.cancel_button.visible = True
        self.ids.error_label.visible = True
        self.ids.edit_button.visible = False
        self.ids.edit_button.height = '0dp'
        self.ids.add_button.height = '0dp'
        self.ids.add_button.visible = False
        self.ids.container.visible = True
        self.parent_screen.word_text_input.focus = True

    def flashcard_editor_fields_view(self):
        self.container.clear_widgets()
        self.container.cols = 1

        self.container.add_widget(PopupLabelCell(text="Word to remember(synonyms allowed, format: "
                                                      "\"word1;synonym word1..\")", size_hint=(0.3, 0.2)))
        self.container.add_widget(self.parent_screen.word_text_input)
        self.container.add_widget(PopupLabelCell(text="Translate",  size_hint=(0.2, 0.2)))
        self.container.add_widget(self.parent_screen.translate_text_input)
        self.container.add_widget(PopupLabelCell(text="Sentence with your word (optionally)",  size_hint=(0.3, 0.2)))
        self.container.add_widget(self.parent_screen.sentence_text_input)
        self.container.add_widget(PopupLabelCell(text="Sentence translate (optionally)", size_hint=(0.3, 0.2)))
        self.container.add_widget(self.parent_screen.translate_sentence_text_input)

    def existing_flashcards_in_pack(self):
        self.parent_screen.edit_flashcards_pressed_callback(self.flashcard_pack_name)

    def open_existing_flashcard_popup(self, flashcards_list):
        self.existing_flashcard_popup.open(flashcards_list)

    def on_edit_picked_flashcard_pressed(self, button_view):
        self.parent_screen.edit_existing_flashcard_pressed_callback(button_view.text)
        self.is_edit_existing_flashcard_pressed = True
        self.existing_flashcard_popup.dismiss()

    def show_error_msg(self, msg):
        self.ids.error_label.text = msg

    def show_picked_flashcard(self, flashcard):
        self.parent_screen.word_text_input.text = flashcard.word
        self.parent_screen.translate_text_input.text = flashcard.translate
        self.parent_screen.sentence_text_input.text = flashcard.sentence
        self.parent_screen.translate_sentence_text_input.text = flashcard.sentence_translate
        self.flashcard_id = flashcard.id
        self.flashcard_editor_view_state()

    def dismiss(self):
        if self.is_edit_existing_flashcard_pressed:
            self.parent_screen.word_text_input.text = ""
            self.show_error_msg("")
            self.parent_screen.translate_text_input.text = ""
            self.parent_screen.sentence_text_input.text = ""
            self.parent_screen.translate_sentence_text_input.text = ""
            self.flashcard_id = None
        self.is_edit_existing_flashcard_pressed = False
        self.parent_screen.word_text_input.focus = False
        super().dismiss()

    def clear_views(self):
        self.parent_screen.word_text_input.text = ""
        self.show_error_msg("")
        self.parent_screen.translate_text_input.text = ""
        self.parent_screen.sentence_text_input.text = ""
        self.parent_screen.translate_sentence_text_input.text = ""
        self.is_edit_existing_flashcard_pressed = False
        self.flashcard_id = None
        self.parent_screen.word_text_input.focus = True


class FlashcardEditorView(Screen):
    """ """
    __metaclass__ = ScreenViewInterface

    title = "Flashcards packs"
    Builder.load_file('libs/uix/kv/flashcardEditorView.kv')

    def __init__(self, **kvargs):
        super().__init__(**kvargs)
        # to deal with action bar
        self.availablePacks = []
        self.edit_flashcards_pressed_callback = None
        self.add_flashcard_pressed_callback = None
        self.edit_existing_flashcard_pressed_callback = None
        # KIVY magic, u cant get text from 'textinput' from popup window !
        # so  lets create textinputs in parent window
        self.word_text_input = TextInput(text=str(""), multiline=True, font_size=23, size_hint=(1, 0.2),  focus=False)
        self.translate_text_input = TextInput(text=str(""), multiline=True, font_size=23, size_hint=(1, 0.2), focus=False)
        self.sentence_text_input = TextInput(text=str(""), multiline=True, font_size=23, size_hint=(1, 0.2), focus=False)
        self.translate_sentence_text_input = TextInput(text=str(""), multiline=True, font_size=23, size_hint=(1, 0.2), focus=False)
        self.popup = FlashcardEditorPopup(self)


    def register_edit_flashcards_pressed_callback(self, callback):
        self.edit_flashcards_pressed_callback = callback

    def register_add_flashcard_pressed_callback(self, callback):
        self.add_flashcard_pressed_callback = callback

    def register_edit_existing_flashcard(self, callback):
        self.edit_existing_flashcard_pressed_callback = callback

    def register_load_flashcard_packs_callback(self, callback):
        self.load_flashcards_packs = callback

    def notice_about_error(self, error_text):
        pass

    def create_flashcard_packs_view(self, packs_list):
        self.availablePacks = packs_list
        # clear all widgets to avoid duplicates
        self.ids.pack_names_grid.clear_widgets()
        for pack_name in self.availablePacks:
            item_box = BoxLayout(orientation="vertical")
            item_label = FormattedButton(text=pack_name, size_hint=(.8, None), pos_hint={'x': .1})
            item_box.add_widget(item_label)
            self.ids.pack_names_grid.add_widget(item_box)
            item_label.bind(on_press=self.on_flashcard_pack_pressed)

    def popup_callback(self, flashcard_pack):
        """ Open Popup """
        self.popup.open(flashcard_pack)

    def on_flashcard_pack_pressed(self, event):
        if hasattr(event, 'text') and event.text in self.availablePacks:
            self.popup_callback(event.text)

    def get_screen_name(self):
        return self.name

    def on_show_screen(self, event_string = ''):
        self.load_flashcards_packs()
        self.word_text_input.focus = True

    def on_keyboard_down(self, key_name = ''):
        """
        handles keyboard events on flashcard editor screen
        :param key_name: string representation of pressed key
        :return:
        """
        if key_name == 'enter':
            if self.word_text_input.focus:
                self.word_text_input.focus = False
                self.word_text_input.text = self.word_text_input.text[:-1]
                self.translate_text_input.focus = True
            elif self.translate_text_input.focus:
                self.translate_text_input.focus = False
                self.translate_text_input.text = self.translate_text_input.text[:-1]
                self.sentence_text_input.focus = True
            elif self.sentence_text_input.focus:
                self.sentence_text_input.focus = False
                self.sentence_text_input.text = self.sentence_text_input.text[:-1]
                self.translate_sentence_text_input.focus = True
            elif self.translate_sentence_text_input.focus:
                self.translate_sentence_text_input.focus = False
                self.translate_sentence_text_input.text = self.translate_sentence_text_input.text[:-1]
                self.word_text_input.focus = True
                self.add_flashcard_pressed_callback(self.popup.flashcard_pack_name)