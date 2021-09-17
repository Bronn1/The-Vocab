# -*- coding: utf-8 -*-
#
# flascardPacksPresenter.py
#
# Презентер для flashcard Packs.
#

from abc import ABC, abstractmethod


class IFlashcardPacksPresenter(ABC):

    def __init__(self):
        """
        constructor
        """
        self.flashcard_packs_list = []

    @abstractmethod
    def on_load_flashcard_packs(self):
        """
        abstract method
        :return:
        """
        pass

    @abstractmethod
    def load_success(self, flashcardPacksList):
        """
        callback method , it starts working when model
        have loaded flashcard packs. Pass to view names
        of flashcard packs
        :param flashcardPacksList:
        :return:
        """
        pass

    # @abstractmethod
    # def flashcard_packs(self):
    #    pass


class FlashcardPacksPresenter(IFlashcardPacksPresenter):
    def __init__(self, model, flashcard_packs_view):
        super().__init__()
        self.flashcard_packs_model = model
        self.flashcard_packs_view = flashcard_packs_view
        self.flashcard_packs_view.register_get_flashcard_pack_setting(self.get_flashcard_pack_setting)
        self.flashcard_packs_view.register_set_flashcard_pack_setting(self.set_flashcard_pack_setting)
        self.flashcard_packs_view.register_load_flashcard_packs_callback(self.on_load_flashcard_packs)

    def on_load_flashcard_packs(self):
        flashcard_packs_list = self.flashcard_packs_model.get_data_table_names()
        if flashcard_packs_list:
            self.load_success(flashcard_packs_list)
        # TODO add possible view error state

    def load_success(self, flashcard_packs_list):
        self.flashcard_packs_list = flashcard_packs_list
        self.flashcard_packs_view.create_flashcard_packs_view(self.flashcard_packs())

    def flashcard_packs(self):
        return self.flashcard_packs_list

    def set_flashcard_pack_setting(self, pack_name, min, max):
        self.flashcard_packs_model.set_min_max_limit_for_table(pack_name, min, max)

    def get_flashcard_pack_setting(self, pack_name):
        (min_limit, max_limit) = self.flashcard_packs_model.get_min_max_limit_for_table(pack_name)
        range_max = self.flashcard_packs_model.count_rows_in_table(pack_name)
        if max_limit == -1:
            max_limit = range_max

        return [min_limit, max_limit, range_max]