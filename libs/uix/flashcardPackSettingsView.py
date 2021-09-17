from kivy.uix.popup import Popup
from kivy.lang import Builder
from libs.uix.rangeSliderView import RangeSlider

class FlashcardPackSettingsPopup(Popup):
    Builder.load_file('libs/uix/kv/flashcardPackSettingsView.kv')
    def __init__(self, obj,  **kwargs):
        super(FlashcardPackSettingsPopup, self).__init__(**kwargs)
        self.parent_screen = obj
        self.flashcard_pack_name = ""
        self.is_edit_existing_flashcard_pressed = False
        self.range_0 = 0
        self.range_1 = 0

    def open(self, pack_name, range_list):
        self.title = pack_name
        self.ids.slider.range = (0, range_list[2])
        self.ids.slider.value = (range_list[0], range_list[1])
        super().open()

    def accept_flashcard_pack_settings(self, pack_name, range_value_0, range_value_1):
        self.parent_screen.set_flashcard_pack_setting(pack_name, range_value_0, range_value_1)
        super().dismiss()