# -*- coding: utf-8 -*-
#
# flashcardPlayerPresenter.py
#
#
#

from abc import ABC, abstractmethod
import random
from itertools import cycle
import datetime
from libs.model.flashcard import FlashcardOperations
from kivy.core import Logger
import requests
import time
import os
os.environ['KIVY_AUDIO'] = 'ffpyplayer'
# from libs.model.flashcardPacksModel import FlashcardModel

from kivy.core.audio import SoundLoader
from kivy.utils import platform
from kivy.logger import Logger
#from libs.common.audioPlayerAndroid import AudioPlayerAndroid
from libs.common.appSettings import AppSettings

class IFlashcardPlayerPresenter(ABC):
    """Simple flashcard player interface"""

    def __init__(self):
        self.flashcard_pack_list = []

    @abstractmethod
    def on_load_flashcards(self, flashcard_pack_name):
        """
        abstract method, should implement the logic  when user try
         to load pack with flashcards.
        :return:
        """
        pass

    @abstractmethod
    def load_success(self, flashcards_list):
        """
        abstract method, should implement the logic  of processing flashcards
        received from model
        :param flashcards_list:
        :return:
        """
        pass


class FlashcardPlayerPresenter(IFlashcardPlayerPresenter):
    """
    This class needs some refactoring.
    Makes flashcard's order to show to user( flashcard's player in other words). Checks correctness of an answer.
    Updates memorization level of flashcard. Can also play a sound with pronunciation of word or sentence.
    Flashcards divided in 3 stages 'first', 'success', 'new':
    `first`: flashcards that should appear first. Contains  cards which have either last attempt to solve
             more that 'Memorization_soft_update_time' hours ago or last attempt was failed(wrong answer)
    `success`: flashcards which have last attempt to solve successful. These stage comes after first one
    `new`: Last stage contains only new flashcards( DO not include flashcards that added by user, added by user
           belong to previous stages, prob better to add separate stage in refactor)
    Every stage have their own limit of flashcards in a row. After limit has been reached switches to next stage
    """

    def __init__(self, model, flashcards_view):
        super().__init__()
        self.flashcard_model = model
        self.flashcards_view = flashcards_view
        self.set_flashcards_view_callbacks()
        self.current_flashcard = None
        self.flashcard_pack_name = ""
        self.too_many_attempts = False
        self.flashcard_pack_size = 0
        self.flashcard_need_to_show_first = []

        self.non_failed_counter = 0
        self.new_counter = 0
        self.success_counter = 0

        self.flashcard_success_list = []
        self.flashcard_new_list = []
        self.flashcard_failed_list = []
        self.flashcard_stage = ['first', 'success', 'new']

        self.mplayer = None
        self.sound_played = True

    def on_load_flashcards(self, flashcard_pack_name):
        self.flashcard_pack_name = flashcard_pack_name
        self.flashcards_view.clear_all_views()
        self.flashcards_view.reset_attempts_button_visible(False)
        self.reset()
        where = ' where memorization < '  + str(AppSettings.Maximum_memorization_state) + ' and is_learned = 0'
        flashcard_dicts = self.flashcard_model.get_flashcards_from_table(flashcard_pack_name, where)
        print(len(flashcard_dicts))
        if flashcard_dicts:
            flashcard_list = FlashcardOperations.convert_to_flashcard_list(flashcard_dicts)
            self.load_success(flashcard_list)

    def set_flashcards_view_callbacks(self):
        self.flashcards_view.register_enter_pressed_callback(self.process_user_input)
        self.flashcards_view.register_reset_attempts_callback(self._reset_recent_attempts)
        self.flashcards_view.register_skip_word_button_pressed_callback(self._skip_current_word)
        self.flashcards_view.register_success_animation_callback(self._success_animation_ended_callback)
        self.flashcards_view.register_load_flashcards_callback(self.on_load_flashcards)

    def load_success(self, flashcard_packs_list):
        flashcard_packs_list  = self._cut_flashcards_by_limits(flashcard_packs_list)
        self.set_flashcard_pack_info(flashcard_packs_list)
        if self.flashcard_pack_size != 0:
            self.non_failed_counter = 0
            self.new_counter = 0
            self.success_counter = 0
            self.flashcard_failed_list = []
            self.flashcard_success_list = []
            self.flashcard_need_to_show_first = []
            self.flashcard_new_list = []
            self.flashcards_view.set_skip_word_button(False)
            self._mix_list()
            self._update_recent_attempts()
            self._make_flashcards_lists_by_stage()
            #self.flashcard_iter = cycle(self.flashcard_pack_list)
            self.stage_iter = cycle(self.flashcard_stage)
            self.stage = next(self.stage_iter)
            #Window.softinput_mode = 'e'
            #self.current_flashcard = next(self.flashcard_iter)
            self.current_flashcard =  self._iterate_to_next_flashcard()
            if not self._is_recent_attempts_not_exceed_limit() and not self.current_flashcard :
                self._show_too_many_recent_attempts_state()
            else:
                Logger.info("FLASHCARD SCREEN: ")
                Logger.info("Opened: ")
                #Logger.info(FlashcardOperations.flashcard_string(self.current_flashcard))
                self._pass_to_view_flashcard()

    def _cut_flashcards_by_limits(self, flashcard_packs_list):
        min_limit, max_limit  = self.flashcard_model.get_min_max_limit_for_table(self.flashcard_pack_name)
        if max_limit == -1:
            max_limit = 10000000
        updated_flashcard_list = []
        for (i,flashcard) in enumerate(flashcard_packs_list):
            # if flashcard not exceeding upper and lower limits and
            # if was added by user
            if i >= min_limit and i <= max_limit or flashcard.is_user_added == 1:
                updated_flashcard_list.append(flashcard)

        return updated_flashcard_list

    def _remove_learned_flashcards(self, flashcard_packs_list):
        fixed_flashcard_list = []
        for flash in flashcard_packs_list:
            if flash.memorization < AppSettings.Maximum_memorization_state and flash.is_learned == 0:
                fixed_flashcard_list.append(flash)

        return fixed_flashcard_list

    def _make_flashcards_lists_by_stage(self):
        now = datetime.datetime.now()
        # if (time_duration.total_seconds() > AppSettings.Memorization_hard_update_time
        for flashcard in self.flashcard_pack_list:
            attempt_time = flashcard.last_failed_attempt if flashcard.last_attempt == "failed" else flashcard.last_successful_attempt
            time_duration = now - attempt_time
            if flashcard.last_attempt == 'new' and  flashcard.is_user_added != 1:
                self.flashcard_new_list.append(flashcard)
            elif time_duration.total_seconds() > AppSettings.Memorization_soft_update_time or \
                    flashcard.last_attempt == 'failed':
                self.flashcard_need_to_show_first.append(flashcard)
            else:
                self.flashcard_success_list.append(flashcard)

    def _iterate_to_next_flashcard(self):
        if len(self.flashcard_failed_list) != 0:
            # self.non_failed_counter += 1
            if self.non_failed_counter >= 3:
                self.non_failed_counter = 0
                return self.flashcard_failed_list.pop(0)
            else:
                self.non_failed_counter += 1
        else:
            self.non_failed_counter = 0

        if self.stage == "first":
            if len(self.flashcard_need_to_show_first) != 0:
                return self.flashcard_need_to_show_first.pop(0)
            else:
                self.stage = next(self.stage_iter)
        if self.stage == "success":
            if len(self.flashcard_success_list) != 0 and self.success_counter <= AppSettings.Success_flashcard_showed_limit:
                self.success_counter += 1
                if len(self.flashcard_success_list) < AppSettings.Success_flashcard_showed_limit:
                    self.stage = next(self.stage_iter)
                return self.flashcard_success_list.pop(0)
            else:
                self.success_counter = 0
                self.stage = next(self.stage_iter)
        if self.stage == "new":
            if len(self.flashcard_new_list) != 0 and self.new_counter <= AppSettings.New_flashcard_showed_limit:
                self.new_counter += 1
                return self.flashcard_new_list.pop(0)
            else:
                self.new_counter = 0
                self.stage = next(self.stage_iter)

        return None

    def set_flashcard_pack_info(self, flashcard_packs_list):
        self.flashcard_pack_list = flashcard_packs_list
        self.flashcard_pack_size = len(self.flashcard_pack_list)

    def process_user_input(self, user_input_str):
        """
        checks if recent attempts isn't exceed the limit and  the correctness of the answer
        if the answer is correct call _process_success_input method
        otherwise call _process_failed_input
        :return:
        """
        user_input_str = user_input_str.lower()
        if self.current_flashcard:
            correct_words_list = self.current_flashcard.word.split(";")
            Logger.info("Before: ")
            Logger.info(FlashcardOperations.flashcard_string(self.current_flashcard))
            Logger.info("After: ")
            if user_input_str in [x.lower() for x in correct_words_list]:
                self._process_success_input()

                next_flashcard = self._iterate_to_next_flashcard()
                if next_flashcard:
                    self.current_flashcard = next_flashcard
                Logger.info(FlashcardOperations.flashcard_string(self.current_flashcard))
            else:
                self.flashcards_view.animate_wrong_answer()
                self._process_failed_input(user_input_str)
                Logger.info(FlashcardOperations.flashcard_string(self.current_flashcard))

    def _process_success_input(self):
        self.flashcards_view.animate_success_answer()
        if not self.flashcards_view.sound_state_button():
            self.get_and_play_mp3_file()
        if not self.current_flashcard.was_failed:
            self._update_flashcard_on_success()
            self.add_updated_flashcard()
        else:
            self.current_flashcard.was_failed = False
            self.flashcard_failed_list.append(self.current_flashcard)
            self.current_flashcard.is_added_to_queue = True
            # self.__change_flashcard_position()
        self._pass_memorization_to_view()

    def get_and_play_mp3_file(self):

        api_url = AppSettings.Text_to_speech_url_api

        sentence = self.current_flashcard.sentence
        if self.current_flashcard.sentence == '':
            sentence = self.current_flashcard.word
        language = "en-us"
        if self.flashcard_pack_name == 'Spanish_words_10k':
            language = "es-es"
        querystring = {"r": "-3","c": "ogg", "f": "32khz_16bit_mono", "src": sentence,
                       "hl": language, "key": "7ce74bcde866441f9852d17822a4bcd3"}

        headers = {
        }

        response = requests.request("GET", api_url, headers=headers, params=querystring)
        self.sound_played = False
        if response.status_code == 200:
            with open('sound.ogg', 'wb') as f:
                f.write(response.content)
            self.mplayer = SoundLoader.load('sound.ogg')
            if self.mplayer:
                self.mplayer.play()


    def _success_animation_ended_callback(self):
        if self.mplayer: #and platform == 'android':
            # For now busy waiting should be ok, cuz u anyway want to block everything till sound is played
            # also kivy sound loader seems to be buggy
            time.sleep(abs(self.mplayer.length - 0.9))
            self.mplayer.unload()
        if self._is_recent_attempts_not_exceed_limit() and self.current_flashcard:
            self._pass_to_view_flashcard()
        else:
            self._show_too_many_recent_attempts_state()

    def _process_failed_input(self, user_input_str):
        self._help_tip_view_state(user_input_str)
        self._update_flashcard_on_fail()
        self._pass_memorization_to_view()

    def _pass_to_view_flashcard(self):
        self.is_learned_flashcard()
        self.flashcards_view.show_flashcard(self.current_flashcard.processed_sentence, self.current_flashcard.sentence_translate,
                                            self.current_flashcard.translate)
        self.flashcards_view.show_memorization(self.current_flashcard.memorization)

    def is_learned_flashcard(self):
        pass
        #counter = 0
        #while self.current_flashcard.memorization >= AppSettings.Maximum_memorization_state or \
        #      self.current_flashcard.is_learned == 1:
        #    self.current_flashcard = next(self.flashcard_iter)
        #    counter += 1
        #    if(counter > self.flashcard_pack_size):
        #        break


    def _pass_memorization_to_view(self):
        self.flashcards_view.show_memorization(self.current_flashcard.memorization)

    def _mix_list(self):
        """
        """
        # let's mix list,  that flashcards is picked randomly for sort every time
        random.shuffle(self.flashcard_pack_list)
        #self.flashcard_pack_list.sort(key=cmp_to_key(custom_sort_cmp))

    def _help_tip_view_state(self, user_answer):
        """
        Проверяет в какие местах пользователь опечатался, если опечаток больше 4
        вовзращает None
        :param user_answer:
        :return:
        """
        self.help_tip_view_state(True)
        # self.flashcard_player_view.show_word_input(r'[color=1a651a][i]' + user_answer + r'[/color][/i]')
        # self.flashcard_player_view.show_word_input('[b]Hello[color=ff0000]world[/color][/b]')
        # Clock.schedule_once(lambda dt: self.pass_correct_answer_to_view(), 1)
        self.pass_correct_answer_to_view()
        # Clock.schedule_interval(lambda dt: self.clear_help_tip_view_state(), 3)

    def help_tip_view_state(self, flag):
        self.flashcards_view.set_help_state_flag(flag)

    def clear_help_tip_view_state(self):
        pass
        #if self.flashcard_player_view.is_help_tip_state:
        #    self.flashcard_player_view.show_word_input("")
        #    self.help_tip_view_state(False)

    def pass_correct_answer_to_view(self):
        self.flashcards_view.show_word_input(self.current_flashcard.word)

    def add_updated_flashcard(self):
        if self.current_flashcard.is_learned == 1 or \
                self.current_flashcard.memorization >= AppSettings.Maximum_memorization_state or  \
                self.current_flashcard.recent_attempts >= AppSettings.Recent_attempts_threshold:
            return
        else:
            self.flashcard_success_list.append(self.current_flashcard)


    def _update_flashcard_on_success(self):
        self.current_flashcard.recent_attempts += 1
        self.current_flashcard.is_added_to_queue = False
        now = datetime.datetime.now()
        if self.current_flashcard.last_attempt == "new" and self.current_flashcard.is_user_added == 0:
            #self.current_flashcard.is_learned = 1
            self.current_flashcard.memorization = AppSettings.Maximum_memorization_state
        else:
            attempt_time = self.current_flashcard.last_failed_attempt if self.current_flashcard.last_attempt == "failed" \
                else self.current_flashcard.last_successful_attempt
            # update memorization state by time duration since last try
            time_duration = now - attempt_time
            if (time_duration.total_seconds() > AppSettings.Memorization_hard_update_time and
                self.current_flashcard.memorization < AppSettings.Maximum_memorization_state -1):
                self.current_flashcard.memorization += 2

            elif (time_duration.total_seconds() > AppSettings.Memorization_soft_update_time and
                  self.current_flashcard.memorization < AppSettings.Maximum_memorization_state):
                self.current_flashcard.memorization += 1

        self.current_flashcard.last_attempt = 'success'
        self.current_flashcard.last_successful_attempt = now
        self.flashcard_model.update_flashcard_last_attempt(self.flashcard_pack_name, self.current_flashcard)

    def _update_flashcard_on_fail(self):
        """
        updated flashcard attributes on users wrong input
        :return:
        """
        self.current_flashcard.recent_attempts += 1
        now = datetime.datetime.now()
        attempt_time = self.current_flashcard.last_failed_attempt if self.current_flashcard.last_attempt == "failed" \
            else self.current_flashcard.last_successful_attempt
        # update memorization state by time duration since last try
        time_duration = now - attempt_time
        if time_duration.total_seconds() > AppSettings.Memorization_hard_update_time and \
                self.current_flashcard.memorization > 2:
            self.current_flashcard.memorization -= 2

        elif (time_duration.total_seconds() > AppSettings.Memorization_soft_update_time or
              self.current_flashcard.last_attempt == "success") and \
              self.current_flashcard.memorization > 1:
            self.current_flashcard.memorization -= 1

        self.current_flashcard.last_attempt = 'failed'
        self.current_flashcard.last_failed_attempt = now
        self.current_flashcard.was_failed = True
        self.flashcard_model.update_flashcard_last_attempt(self.flashcard_pack_name, self.current_flashcard)

    def _is_recent_attempts_not_exceed_limit(self):
        is_recent_attempts_not_exceed = False
        for flashcard in self.flashcard_success_list:
            if not flashcard.recent_attempts >= AppSettings.Recent_attempts_threshold:
                is_recent_attempts_not_exceed = True
        for flashcard in self.flashcard_new_list:
            if not flashcard.recent_attempts >= AppSettings.Recent_attempts_threshold:
                is_recent_attempts_not_exceed = True
        for flashcard in self.flashcard_failed_list:
            if not flashcard.recent_attempts >= AppSettings.Recent_attempts_threshold:
                is_recent_attempts_not_exceed = True
        for flashcard in self.flashcard_need_to_show_first:
            if not flashcard.recent_attempts >= AppSettings.Recent_attempts_threshold:
                is_recent_attempts_not_exceed = True

        return is_recent_attempts_not_exceed

    def _update_recent_attempts(self):
        # TODO maybe bug!!! recent_attempts is needed to update in db
        for flashcard in self.flashcard_pack_list:
            now = datetime.datetime.now()
            if flashcard.last_attempt == "success":
                time_duration = now - flashcard.last_successful_attempt
                if time_duration.total_seconds() > AppSettings.Memorization_soft_update_time:
                    flashcard.recent_attempts = 0
            else:
                time_duration = now - flashcard.last_failed_attempt
                if time_duration.total_seconds() > AppSettings.Memorization_soft_update_time:
                    flashcard.recent_attempts = 0

    def _show_too_many_recent_attempts_state(self):
        msg = "Too many recent attempts on all yours flashcard, comeback later or refresh it by clicking on button below"
        self.flashcards_view.show_warn(msg)
        self.flashcards_view.reset_attempts_button_visible(True)

    def _reset_recent_attempts(self):
        for flashcard in self.flashcard_pack_list:
            flashcard.recent_attempts = 0
            self.flashcard_model.update_flashcard_last_attempt(self.flashcard_pack_name, flashcard)

        self.on_load_flashcards(self.flashcard_pack_name)

    def reset(self):
        """
        устанавливает в начальное состояние при загрузке очередного пака с флешкартами
        :return:
        """
        self.current_flashcard = None

    def _skip_current_word(self):
        if self.current_flashcard:
            self.current_flashcard.is_learned = 1
            self.flashcard_model.update_learned_field(self.flashcard_pack_name, self.current_flashcard)
            next_flashcard = self._iterate_to_next_flashcard()
            if next_flashcard:
                self.current_flashcard = next_flashcard
            self._pass_to_view_flashcard()
            self.flashcards_view.set_skip_word_button(False)

    def sound_finished(self):
        self.sound_played = True
