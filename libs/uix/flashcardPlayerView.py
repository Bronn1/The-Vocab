# -*- coding: utf-8 -*-
#
# startscreen.py
#
# отображение экрана с флешкартами
#

from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from kivy.animation import Animation
from kivy.config import Config
from libs.uix.screenViewInterface import ScreenViewInterface
from libs.common.appSettings import AppSettings


class FlashcardsPlayerView(Screen):
    __metaclass__ = ScreenViewInterface

    #events_callback = ObjectProperty(None)
    title = "Learn flashcards"
    Builder.load_file("libs/uix/kv/flashcardPlayerView.kv")
    events_callback = ObjectProperty(None)
    hide_translate_checkbox = ObjectProperty(None)

    def __init__(self,  font_size, **kvargs):
        super().__init__(**kvargs)
        self.font_size = font_size
        self.enter_pressed_callback = None
        self.reset_attempts_callback = None
        self.ids.word_input.unfocus_on_touch = False
        self.is_help_tip_state = False
        self.skip_word_button__callback  = None
        self.success_animation_callback = None
        self.on_load_flashcards = None
        self.ids.memorization_progress_bar.max = AppSettings.Maximum_memorization_state


    def on_events(self, event):
        pass

    def register_enter_pressed_callback(self, callback):
        self.enter_pressed_callback = callback

    def register_reset_attempts_callback(self, callback):
        self.reset_attempts_callback = callback

    def register_skip_word_button_pressed_callback(self, callback):
        self.skip_word_button_pressed_callback = callback

    def register_success_animation_callback(self, callback):
        self.success_animation_callback = callback

    def register_load_flashcards_callback(self, callback):
        self.on_load_flashcards = callback

    def on_show_screen(self, event_string = ''):
        self.on_load_flashcards(event_string)
        self.ids.word_input.focus = True

    def show_flashcard(self, sentence, sentence_translate, translate):
        """
        Отображает предложение(фразу) в label: sentence_label
        :return:
        """
        self.ids.word_input.hint_text = ''
        self.ids.word_input.text = ""
        self.on_keyboard_down("4")
        self.ids.sentence_label.text = sentence
        self.ids.translate_label.text = sentence_translate
        if not self.ids.translate_label.text == '':
            self.ids.word_full_translate_button.tooltip_text = translate
            #self.word_full_translate.description_text = translate
        else:
            #self.word_full_translate.description_text = ' '
            self.ids.word_full_translate_button.tooltip_text = ' '

    def show_word_input(self, str):
        self.ids.word_input.text = ''
        self.ids.word_input.hint_text = str

    def show_memorization(self, memorization):
        self.ids.memorization_progress_bar.value = memorization
        if memorization <= 2:
            self.ids.memorization_progress_bar.color = (0.949, 0.471, 0.294, 1.0)
        elif memorization <= 4:
            self.ids.memorization_progress_bar.color = (0.302, 0.02, 0.91, 1.0)
        else:
            self.ids.memorization_progress_bar.color = (0, 0.729, 0, 1.0)

    def animate_wrong_answer(self, *args):
        animation = Animation(background_color = (1, 0.388, 0.306,1))
        animation.bind(on_complete=self.reset_input_word)
        animation.start(self.ids.word_input)

    def animate_success_answer(self, *args):
        animation = Animation(background_color = (0.196, 0.804, 0.196, 0.5), duration=2., t='out_elastic')
        self.ids.word_input.disabled = True
        self.ids.skip_word_button.disabled = True
        animation.bind(on_complete=self.reset_input_word_success)
        animation.start(self.ids.word_input)

    def reset_input_word_success(self, *args):
        widget = args[1]
        widget.background_color = (0.592, 0.745, 0.98, 1.)
        self.ids.word_input.disabled = False
        self.ids.skip_word_button.disabled = False
        self.success_animation_callback()

    def reset_input_word(self, *args):
        widget = args[1]
        widget.background_color = (0.592, 0.745, 0.98, 1.)
        self.ids.word_input.disabled = False
        #widget.blink_size = 0

    def show_warn(self, warn):
        """
        Отображает предложение(фразу) в label: sentence_label
        :return:
        """
        #self._on_keyboard_down("4", 'f', 'sdf')
        self.ids.sentence_label.text = warn

    def show_translation(self, translation):
        """
        Отображает предложение(фразу) в label: sentence_label
        :return:
        """
        self.ids.translate_label.text = translation

    def set_help_state_flag(self, flag):
        self.is_help_tip_state = flag

    def enter_pressed(self):
        """
        Вызывается, если user нажал enter и если колбэк устанаовлен, передает
        управление пресентеру
        :return:
        """
        if self.enter_pressed_callback: # and self.start_screen.screen_manager.current == self.screen_name: #and \
            #    self.is_help_tip_state == False:
            self.enter_pressed_callback(self.ids.word_input.text)
            #self.ids.word_input.text = ""
            self.ids.word_input.focus = True

    def reset_recent_attempts_button_pressed(self):
        self.reset_attempts_callback()

    def clear_all_views(self):
        """
        clears widgets ,sets initial state for views
        :return:
        """
        self.ids.sentence_label.text = ""
        self.ids.translate_label.text = ""
        self.ids.word_input.text = ""
        self.ids.word_input.disabled = False
        #self.word_full_translate.description_text = ' '
        self.ids.word_full_translate_button.tooltip_text = ''
        self.ids.word_input.background_color = (0.592, 0.745, 0.98, 1.)

    def reset_attempts_button_visible(self, flag):
        self.ids.reset_recent_attempts.visible = flag

    def on_hide_translate_sentence_checkbox(self, flag):
        #self.ids.hide_translate_checkbox.active = flag
        if(flag):
            self.ids.hide_translate_checkbox.active = False
            self.ids.hide_translate_checkbox.icon = 'data/images/arrow_down.png'
            self.ids.translate_label.visible = False
            # TODO clean up shitcode with magic numbers
            self.ids.useless_label.pos_hint = {'center_x': 0.4, 'top':0.78}
            self.ids.word_input.pos_hint = {'center_x': 0.54, 'top':0.74}
            #self.ids.word_full_translate.pos_hint = {'center_x': 0.14, 'top': 0.78}
        else:
            self.ids.hide_translate_checkbox.active = True
            self.ids.translate_label.visible = True
            self.ids.hide_translate_checkbox.icon = 'data/images/arrow_up.png'
            self.ids.useless_label.pos_hint = {'center_x': 0.4, 'top': 0.58}
            self.ids.word_input.pos_hint = {'center_x': 0.54, 'top': 0.54}
            #self.ids.word_full_translate.pos_hint =  {'center_x': 0.14, 'top':0.58}
        Config.set('FlashcardView', 'HideTranslate', str(flag))
        Config.write()

    def set_skip_word_button(self, flag):
        self.ids.skip_word_button.active = flag

    def on_skip_word(self):
        self.skip_word_button_pressed_callback()

    def on_change_sound_state(self):
        if self.ids.sound_state_button.is_sound_muted:
            self.ids.sound_state_button.icon = "data/images/sou.png"
            self.ids.sound_state_button.is_sound_muted = False
        else:
            self.ids.sound_state_button.icon = "data/images/nosound.png"
            self.ids.sound_state_button.is_sound_muted = True
        Config.set('FlashcardView', 'MutedSound', str(self.ids.sound_state_button.is_sound_muted))
        Config.write()

    def sound_state_button(self):
        return self.ids.sound_state_button.is_sound_muted

    def get_screen_name(self):
        return self.name

    def on_keyboard_down(self, key_name = ''):
        """
        handles keyboard events
        :param key_name: string representation of pressed key
        :return:
        """
        self.ids.word_input.focus = True
