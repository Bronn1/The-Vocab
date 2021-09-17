
class AppSettings:
    Debug = True

    # time limits to update state of memorization of a flashcard with a word
    Memorization_soft_update_time = 60 * 60 * 7  # 9 hours
    Memorization_hard_update_time = 60 * 60 * 24 * 2
    # limit after it flashcard consider as already learned and doesnt show anymore
    Maximum_memorization_state = 8
    Init_memorization_state = 0
    # attempts on one flashcard in very short period of time
    Recent_attempts_threshold = 1006
    # how many different types of flashcards we'r gonna see in one try
    Failed_flashcard_showed_limit = 5
    Success_flashcard_showed_limit = 8
    New_flashcard_showed_limit = 12
    Text_to_speech_url_api = "http://api.voicerss.org/"