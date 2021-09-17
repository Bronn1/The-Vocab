# -*- coding: utf-8 -*-
#
# flashcardEditorPresenter.py
#
# Flashcard packs editor logic
#

from abc import ABC, abstractmethod
import datetime
import re
from libs.presenters.flashcardPacksPresenter import IFlashcardPacksPresenter
from libs.model.flashcard import FlashcardOperations
from kivy.core import Logger
import json

class IFlashcardEditorPresenter(ABC):

    @abstractmethod
    def on_add_flashcard_in_pack(self, pack_name):
        """

        :return:
        """
        pass


class FlashcardEditorPresenter(IFlashcardPacksPresenter, IFlashcardEditorPresenter):

    def __init__(self, model, editor_view):
        super().__init__()
        self.flashcard_packs_model = model
        self.editor_view = editor_view
        self.editor_view.register_edit_flashcards_pressed_callback(self.on_load_flashcards_from_pack)
        self.editor_view.register_add_flashcard_pressed_callback(self.on_add_flashcard_in_pack)
        self.editor_view.register_edit_existing_flashcard(self.on_edit_existing_flashcard)
        self.editor_view.register_load_flashcard_packs_callback(self.on_load_flashcard_packs)
        self.user_input = {}
        self.flashcards_list = []

    def get_user_input(self):
        """
        Get user input from  view
        :return: hash
        """
        return { 'id': self.editor_view.popup.flashcard_id,
                       'word': self.editor_view.word_text_input.text,
                      'translate': self.editor_view.translate_text_input.text,
                      'sentence': self.editor_view.sentence_text_input.text,
                      'processed_sentence': "",
                      'sentence_translate': self.editor_view.translate_sentence_text_input.text}

    def on_load_flashcard_packs(self):
        flashcard_packs_list = self.flashcard_packs_model.get_data_table_names()
        if flashcard_packs_list:
            self.load_success(flashcard_packs_list)
        # TODO add possible view error state

    def on_add_flashcard_in_pack(self, pack_name):
        self.user_input = self.get_user_input()
        Logger.info(json.dumps(self.user_input))
        self.remove_leading_spaces()
        self.remove_last_semicolon()
        if self._check_word_and_translate_not_empty():
            if self._check_sentence_contains_word():
                self._create_processed_sentence()
                if self.user_input['id'] is None:
                    self.flashcard_packs_model.add_flashcard_in_table(pack_name, self.user_input)
                else:
                    self.flashcard_packs_model.edit_flashcard_in_table(pack_name, self.user_input)
                self.clear_view()
            else:
                self.pass_error_msg_to_view("Sentence must contain specified word: " + self.user_input['word'])
        else:
            self.pass_error_msg_to_view("Word and Translate fields are required")

    def remove_leading_spaces(self):
        for key in self.user_input.keys():
            if key is not "id":
                self.user_input[key] = self.user_input[key].strip()

    def remove_last_semicolon(self):
        for key in self.user_input.keys():
            if key is not "id" and self.user_input[key].endswith(';'):
                self.user_input[key] = self.user_input[key][:-1]

    def _check_word_and_translate_not_empty(self):
        """
        user input verification, if fields word(Word to remember) or translate are empty return False
        :return: True if input was correct, False otherwise
        """
        if self.user_input['translate'] == "" or self.user_input['word'] == "":
            return False
        return True

    def _check_sentence_contains_word(self):
        if self.user_input['sentence'] != "":
            correct_words_list = self.user_input['word'].split(";")
            for word in correct_words_list:
                match_found = re.search(r'\b' + word + r'\b', self.user_input['sentence'])
                if match_found:
                    return True
            return False
        return True

    def _create_processed_sentence(self):
        if self.user_input['sentence'] != "":
            words_list = self.user_input['word'].split(";")
            for word in words_list:
                if(re.search(r'\b' + word + r'\b', self.user_input['sentence'])):
                    self.user_input['processed_sentence'] = re.sub(r'\b' + word + r'\b', r'[color=1a651a][i]' +
                                                            self.user_input['translate'] + r'[/color][/i]', self.user_input['sentence'])
        else:
            self.user_input['processed_sentence'] = self.user_input['translate']
        self.pass_error_msg_to_view(self.user_input['processed_sentence'])

    def pass_error_msg_to_view(self, msg):
        self.editor_view.popup.show_error_msg(msg)

    def clear_view(self):
        self.editor_view.popup.clear_views()

    def load_success(self, flashcard_packs_list):
        self.flashcard_packs_list = flashcard_packs_list
        self.editor_view.create_flashcard_packs_view(self.flashcard_packs_list)

    def load_flashcards_success(self, flashcards):
        self.flashcards_list = flashcards
        self.editor_view.popup.open_existing_flashcard_popup(flashcards)

    def on_load_flashcards_from_pack(self, pack_name):
        flashcard_dicts = self.flashcard_packs_model.get_flashcards_from_table(pack_name)
        if flashcard_dicts:
            flashcard_list = FlashcardOperations.convert_to_flashcard_list(flashcard_dicts)
            self.load_flashcards_success(flashcard_list)

    def on_edit_existing_flashcard(self, flashcard_word):
        [ self.pass_flashcard_in_view(i) for i in self.flashcards_list if i.word == flashcard_word ]

    def pass_flashcard_in_view(self, flashcard):
        self.editor_view.popup.show_picked_flashcard(flashcard)
