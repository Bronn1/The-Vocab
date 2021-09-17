from libs.uix.screenViewInterface import ScreenViewInterface
from kivy.uix.screenmanager import ScreenManager

class CustomScreenManager(ScreenManager):
    '''
    Handles all logic of managing  screens of applications
    inherits Kivy class ScreenManager
    '''

    def __init__(self, **kvargs):
        super().__init__(**kvargs)
        self._screens_stack = []
        #self._screen_manager

    def switch_to_screen(self, screen_name):
        '''
        switch currently showing screen to screen with name 'screen_name'
        adds switched screen to _screen_stack attribute
        :param screen_name: name of screen
        :return:
        '''
        if self.has_screen(screen_name):
            self._add_to_screen_stack(self.current)
            self.current = screen_name

    def set_up_current_screen(self, event_str = ''):
        '''
        calls on_show_screen() method to set up all needed data for new screen
        also manages the action bar since its also part of screens
        :param event_str: event that needs to be possibly passed to new screen
        :return:
        '''
        if self.current_screen:
            self.current_screen.on_show_screen(event_str)
            if self._is_screen_stack_empty():
                self.parent.action_previous.visible = False
            else:
                self.parent.action_previous.visible = True

    def switch_to_previous_screen(self):
        '''
        switch currently showing screen to previously  showed screen
        :return:
        '''
        if self._screens_stack:
            self.current = self._pop_from_screen_stack()

    def _is_screen_stack_empty(self):
        if self._screens_stack:
            return False
        else:
            return True


    def _add_to_screen_stack(self, screen_name):
        self._screens_stack.append(screen_name)

    def _pop_from_screen_stack(self):
        return self._screens_stack.pop()

