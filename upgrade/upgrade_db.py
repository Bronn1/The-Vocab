import shutil
import os


class Upgrade_db():

    def __init__(self):
        pass

    @staticmethod
    def replace_db_file_b1_1_1(user_data_dir):
        '''
        this method replace old version of db
        used only bete test!
        :return:
        '''
        src_dir = 'upgrade'
        #dest_dir = os.path.join('user_data_dir')
        src_file = os.path.join(src_dir, 'flashcards.db')
        shutil.copy(src_file, user_data_dir)



    def upgdrade_db(self):
        pass