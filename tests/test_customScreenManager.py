import unittest
from unittest.mock import MagicMock
from unittest.mock import *
from libs.uix.customScreenManager import *
from kivy.uix.screenmanager import Screen

class TestScreenManager(unittest.TestCase):

    def setUp(self):
        self.screen_manager = CustomScreenManager()
        self.screen_manager.parent = MagicMock()
        # mock adding real widget to exclude all internal Kivy graphical stuff from tests
        self.screen_manager.real_add_widget = MagicMock()
        # create some mock screens to manage them
        self.test_screens = []
        for i in range(4):
            screen = MagicMock(spec=Screen)
            screen.manager = None
            screen.on_show_screen = MagicMock()
            screen.name = 'test_screen_name %d' % i
            self.test_screens.append(screen)

    #@patch('Screen')
    def test_current_after_add_widget(self):
        screen_name = "testing_screen_name"
        screen = MagicMock(spec=Screen)
        screen.on_show_screen =  MagicMock()
        screen.manager = None
        screen.name = screen_name
        self.screen_manager.add_widget(screen)
        self.assertEqual(self.screen_manager.current, screen_name, "Incorrect screen name after add widget")

    def test_current_after_switch_to_screen(self):
        self.screen_manager.add_widget(self.test_screens[0])
        self.screen_manager.add_widget(self.test_screens[1])
        expected_screen_name = self.test_screens[1].name
        self.screen_manager.switch_to_screen(expected_screen_name)

        self.assertEqual(self.screen_manager.current, expected_screen_name, "Incorrect screen name after switch to screen")

    def test_screen_stack_after_switch_to_screen(self):
        self.screen_manager.add_widget(self.test_screens[0])
        self.screen_manager.add_widget(self.test_screens[1])
        self.screen_manager.add_widget(self.test_screens[2])
        self.screen_manager.add_widget(self.test_screens[3])
        self.screen_manager.switch_to_screen(self.test_screens[1].name)
        self.screen_manager.switch_to_screen(self.test_screens[2].name)

        expected_stack = [self.test_screens[0].name, self.test_screens[1].name]

        self.assertListEqual(self.screen_manager._screens_stack, expected_stack)

    def test_screen_stack_after_switch_to_previous(self):
        self.screen_manager.add_widget(self.test_screens[0])
        self.screen_manager.add_widget(self.test_screens[1])
        self.screen_manager.add_widget(self.test_screens[2])
        self.screen_manager.add_widget(self.test_screens[3])
        self.screen_manager.switch_to_screen(self.test_screens[1].name)
        self.screen_manager.switch_to_screen(self.test_screens[2].name)
        self.screen_manager.switch_to_screen(self.test_screens[3].name)
        self.screen_manager.switch_to_previous_screen()
        self.screen_manager.switch_to_previous_screen()


        expected_stack = [self.test_screens[0].name]

        self.assertListEqual(self.screen_manager._screens_stack, expected_stack)

    def test_current_after_switch_to_previous(self):
        self.screen_manager.add_widget(self.test_screens[0])
        self.screen_manager.add_widget(self.test_screens[1])
        self.screen_manager.add_widget(self.test_screens[2])
        self.screen_manager.add_widget(self.test_screens[3])
        self.screen_manager.switch_to_screen(self.test_screens[1].name)
        self.screen_manager.switch_to_screen(self.test_screens[2].name)
        self.screen_manager.switch_to_screen(self.test_screens[3].name)
        self.screen_manager.switch_to_previous_screen()

        expected_screen_name = self.test_screens[2].name

        self.assertEqual(self.screen_manager.current, expected_screen_name, "Incorrect screen name after switch to previous")

    def test_on_show_screen_called_once(self):
        self.screen_manager.add_widget(self.test_screens[0])
        self.screen_manager.add_widget(self.test_screens[1])
        self.screen_manager.switch_to_screen(self.test_screens[1].name)
        self.screen_manager.set_up_current_screen("test")

        self.test_screens[1].on_show_screen.assert_called_once_with("test")

#    try:
    #       myFunc()
        #    except ExceptionType:
#        self.fail("myFunc() raised ExceptionType unexpectedly!")