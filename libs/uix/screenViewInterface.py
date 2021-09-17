# -*- coding: utf-8 -*-
#
# screenViewInterface.py
#
# Interface for all screen's views
#

from abc import ABC, abstractmethod


class ScreenViewInterface(ABC):
    """
    Interface contains methods that every screen view has to implement
    """

    @abstractmethod
    def get_screen_name(self):
        pass

    @abstractmethod
    def on_keyboard_down(self, key_name = ''):
        pass

    @abstractmethod
    def on_show_screen(self, event_string = ''):
        pass
