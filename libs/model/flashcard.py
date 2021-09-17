
class Flashcard():
    """
    Class implements flashcard structure
    """
    def __init__(self, id = None, word = "" , translate = "", memorization = 0, sentence = "", sentence_translate = "",
                 processed_sentence = "", last_successful_attempt = None, last_failed_attempt = None,
                 last_attempt = "", recent_attempt = 0, is_user_added = "", is_learned = "", is_added_to_user = ""):
        self.id = id
        self.word = word
        self.translate = translate
        self.memorization = memorization
        self.sentence = sentence
        self.sentence_translate = sentence_translate
        self.processed_sentence = processed_sentence
        self.last_successful_attempt = last_successful_attempt
        self.last_failed_attempt = last_failed_attempt
        self.last_attempt = last_attempt
        self.recent_attempts = recent_attempt
        # if user gave the wrong word, flashcard will be added in flashcards queue  to show up again till correct word.
        self.is_added_to_queue = False
        # another bool var, if last time user failed word, flashcard would be open till correct word, so we need to
        # determine if it was was fail at first place and dont update last success attempt
        self.was_failed = False
        # checks
        self.is_user_added = is_user_added
        self.is_learned = is_learned
        self.is_added_to_user = is_added_to_user


class FlashcardOperations():
    """
    Defines some operations with flashcards (like swap)
    """
    @staticmethod
    def swap( first, second):
        if isinstance( first, Flashcard) and isinstance(second, Flashcard):
            first.id, second.id = second.id, first.id
            first.word , second.word = second.word, first.word
            first.translate, second.translate = second.translate, first.translate
            first.memorization, second.memorization = second.memorization, first.memorization
            first.sentence, second.sentence = second.sentence, first.sentence
            first.sentence_translate, second.sentence_translate = second.sentence_translate, first.sentence_translate
            first.processed_sentence, second.processed_sentence = second.processed_sentence, first.processed_sentence
            first.last_successful_attempt, second.last_successful_attempt = second.last_successful_attempt, first.last_successful_attempt
            first.last_failed_attempt, second.last_failed_attempt = second.last_failed_attempt, first.last_failed_attempt
            first.last_attempt, second.last_attempt = second.last_attempt, first.last_attempt
            first.recent_attempts, second.recent_attempts = second.recent_attempts, first.recent_attempts
            first.is_added_to_queue, second.is_added_to_queue = second.is_added_to_queue, first.is_added_to_queue
            first.was_failed, second.was_failed = second.was_failed, first.was_failed
            first.is_user_added , second.is_user_added  = second.is_user_added , first.is_user_added
            first.is_learned, second.is_learned = second.is_learned, first.is_learned
            first.is_added_to_user, second.is_added_to_user = second.is_added_to_user, first.is_added_to_user

    @staticmethod
    def flashcard_string(flashcard):
        """ debug info"""
        #print (flashcard.word, " -> ", flashcard.memorization, " <-memoriz; ", flashcard.last_attempt, flashcard.last_successful_attempt, flashcard.last_failed_attempt)
        return flashcard.word, flashcard.translate, flashcard.sentence, flashcard.processed_sentence, \
               " memor-> ", flashcard.memorization, "; last attempt-> ", flashcard.last_attempt, flashcard.recent_attempts, \
               "; failed->", flashcard.last_failed_attempt, "; success->", flashcard.last_successful_attempt, "; was_failed->" , \
               flashcard.was_failed, "; is added to queue->", flashcard.is_added_to_queue, "; "

    @staticmethod
    def convert_to_flashcard_list(list_of_dicts):
        """
        converts list of dicts with flashcard info to list with Flashcard
        :param list_of_dicts:
        :return: list of flashcards
        """
        flashcard_list = []
        for row in list_of_dicts:
            # TODO keys existence
            flashcard = Flashcard(row['id'], row['word'],row['translate'], row['memorization'], row['sentence'],
                           row['sentence_translate'], row['processed_sentence'], row['last_successful_attempt'],
                           row['last_failed_attempt'], row['last_attempt'], row['recent_attempts'],
                           row['is_user_added'], row['is_learned'], row['is_added_to_user'] )
            flashcard_list.append(flashcard)

        return flashcard_list
