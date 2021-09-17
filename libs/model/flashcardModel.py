# -*- coding: utf-8 -*-
#
# flashcardModel.py
#
# Model class to work with DB
#

from abc import ABC, abstractmethod
import sqlite3
from datetime import datetime
import os
from kivy.logger import Logger

from libs.common.appSettings import AppSettings


class IFlashcardModel(ABC):
    """
    Model interface, describes needed methods for Presenters
    """

    def __init__(self):
        self.presenter = None

    @abstractmethod
    def get_data_table_names(self):
        pass

    @abstractmethod
    def get_flashcards_from_table(self, table_name, where):
        pass

    @abstractmethod
    def update_flashcard_last_attempt(self, pack_name, flashcard):
        pass

    @abstractmethod
    def add_flashcard_in_table(self, pack_name, flashcard_hash):
        pass

    @abstractmethod
    def edit_flashcard_in_table(self, pack_name, flashcard_hash):
        pass

    @abstractmethod
    def create_flashcard_pack(self, name):
        pass

    @abstractmethod
    def get_min_max_limit_for_table(self, name):
        pass

    @abstractmethod
    def update_learned_field(self, table_name, flashcard):
        pass

    @abstractmethod
    def set_min_max_limit_for_table(self, pack_name, min_limit, max_limit):
        pass

# for sqlite fetch stuff
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]

    return d


class FlashcardModel(IFlashcardModel):
    """
    Contains methods to work with  SQL-lite DB
    DB has very simple structure, every table represents pack with flashcards.
    Tables structure:
			id INTEGER PRIMARY KEY ASC,
			word varchar(255) NOT NULL ,
			translate varchar(255) NOT NULL,
			memorization int DEFAULT 0,
			sentence text DEFAULT '',
			entence_translate text DEFAULT '',
			processed_sentence text DEFAULT '',
			last_successful_attempt timestamp,
			last_failed_attempt timestamp,
			last_attempt text CHECK(last_attempt in ("failed", "success", "new")),
			recent_attempts int,
			is_user_added int,
			is_learned int,
			is_added_to_user text CHECK(is_added_to_user in ("yes", "created", "no", "reset"))
			CHECK (memorization>=0 and memorization<=10)
    Also DB has additional table 'pack_setting_limit' with limits for flashcards
    """

    def __init__(self, db_path, debug=True):
        super().__init__()
        self.debug = debug
        Logger.error(db_path)
        self.db_path = db_path
        self.data_table_names = []
        self.flashcards = []

        self._data_db_name = 'flashcards.db'
        self.setting_limit_table = 'pack_setting_limit'
        self.db_con = self._connect_to_db()
        self.db_con.set_trace_callback(Logger.info)
        self.INIT_MEMORIZATION = AppSettings.Init_memorization_state

    def _connect_to_db(self):
        """
        Connects to SQL-lite DB, if debug is on changes path to test-DB in current directory
        :return: DB connection object
        """
        # os.path.join('data','db') #os.path.dirname(os.path.abspath(__file__)) self.db_path
        path = self.db_path
        if self.debug:
            path = os.path.dirname(os.path.abspath(__file__))
        try:
            print(path)
            con = sqlite3.connect(os.path.join(path, self._data_db_name), detect_types=sqlite3.PARSE_DECLTYPES)
            con.row_factory = dict_factory
            return con

        except sqlite3.Error as e:
            Logger.error("Error connecting to SQL-lite database: " + e.__str__())

    def get_data_table_names(self):
        """
        Load all data tables except one 'limit settings' table
        :return: List of table names
        """
        data_table_names = []
        if self.db_con:
            try:
                cursor = self.db_con.cursor()
                # executing all tables from DB
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                table_name = cursor.fetchone()
                while table_name is not None:
                    if table_name['name'] != self.setting_limit_table:
                        data_table_names.append(table_name['name'])
                    table_name = cursor.fetchone()
                cursor.close()

            except sqlite3.Error as e:
                Logger.error("Can't load tables from SQL-lite database: " + e.__str__())

            return data_table_names

    def get_flashcards_from_table(self, table_name, where=''):
        """
        Executes all rows(flashcards) from table
        :param where:
        :param table_name:
        :return: list of flashcards
        """
        flashcards = []
        if self.db_con:
            try:
                query = "SELECT * FROM {}".format(table_name)
                query += where
                cursor = self.db_con.cursor()
                cursor.execute(query)
                row = cursor.fetchone()
                while row is not None:
                    flashcards.append(row)
                    row = cursor.fetchone()

                cursor.close()

            except sqlite3.Error as e:
                Logger.error("Can't load rows from SQL-lite table: " + table_name + ", error: " + e.__str__())

        return flashcards

    def update_flashcard_last_attempt(self, table_name, flashcard):
        """
        Updates rows in table that connected with last attempt:
        (memorization, last_successful_attempt, last_failed_attempt, last_attempt, recent_attempts)
        :param table_name:
        :param flashcard:
        :return:
        """
        if self.db_con:
            try:
                # TODO add is_learned
                sql_update_query = "Update " + table_name + " set memorization = ?, last_successful_attempt = ?," \
                                   " last_failed_attempt = ?, last_attempt = ?, recent_attempts = ? where id = ?"
                columns_values = (flashcard.memorization, flashcard.last_successful_attempt,
                                   flashcard.last_failed_attempt, flashcard.last_attempt, flashcard.recent_attempts,
                                   flashcard.id)
                cursor = self.db_con.cursor()
                cursor.execute(sql_update_query, columns_values)
                self.db_con.commit()
                cursor.close()

            except sqlite3.Error as e:
                Logger.error("Can't update row in table: " + table_name + ", error: " + e.__str__())

    def update_learned_field(self, table_name, flashcard):
        if self.db_con:
            try:
                sql_update_query = "Update " + table_name + " set is_learned = ?  where id = ?"
                columns_values = (flashcard.is_learned, flashcard.id)
                cursor = self.db_con.cursor()
                cursor.execute(sql_update_query, columns_values)
                self.db_con.commit()
                cursor.close()

            except sqlite3.Error as e:
                Logger.error("Can't update row in table: " + table_name + ", error: " + e.__str__())

    def add_flashcard_in_table(self, table_name, fields_dict):
        """
        Adds new flashcard in table
        Assumes every required field exists
        :param table_name:
        :param fields_dict:
        :return:
        """
        if self.db_con:
            try:
                cursor = self.db_con.cursor()
                fields_dict['word'] = fields_dict['word'].lower()
                # if id wasn't set then the flashcard is new
                if fields_dict['id'] is None:
                    sql_update_query = "INSERT INTO " + table_name + "( id, word, translate, memorization, sentence, " \
                                       "sentence_translate, processed_sentence, last_successful_attempt, " \
                                       "last_failed_attempt, last_attempt, recent_attempts, is_user_added, " \
                                       "is_learned, is_added_to_user ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
                    columns_values = (None, fields_dict['word'], fields_dict['translate'], self.INIT_MEMORIZATION,
                                      fields_dict['sentence'], fields_dict['sentence_translate'],
                                      fields_dict['processed_sentence'], datetime.now(), datetime.now(),
                                      "new", 0, 1, 0, "created")
                    cursor.execute(sql_update_query, columns_values)
                    self.db_con.commit()
                    cursor.close()

            except sqlite3.Error as e:
                Logger.error("Can't insert row in table: " + table_name + ", error: " + e.__str__())

    def edit_flashcard_in_table(self, table_name, fields_dict):
        """
        Edit(updates) basic flashcard information  in table
        :param table_name:
        :param fields_dict:
        :return:
        """
        if self.db_con:
            try:
                fields_dict['word'] = fields_dict['word'].lower()
                sql_update_query = "Update " + table_name + " set word = ?, translate = ?," \
                                                           " sentence = ?, sentence_translate = ?," \
                                                           " processed_sentence = ? where id = ?"
                columns_values = (fields_dict['word'], fields_dict['translate'],
                                  fields_dict['sentence'], fields_dict['sentence_translate'],
                                  fields_dict['processed_sentence'], fields_dict['id'])
                cursor = self.db_con.cursor()
                cursor.execute(sql_update_query, columns_values)
                self.db_con.commit()
                cursor.close()
                Logger.debug('title: This is a debug message.')

            except sqlite3.Error as e:
                Logger.error("Can't  basic update row in table: " + table_name + ", error: " + e.__str__())

    def count_learned_words(self):
        """
        Counts all rows in All tables with criterion is_learned = 1 or memorization > learned threshold
        :return:
        """
        counter = 0
        if self.db_con:
            try:
                flashcard_packs = []
                cursor = self.db_con.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                table_name = cursor.fetchone()
                while table_name is not None:
                    if table_name['name'] != self.setting_limit_table:
                        flashcard_packs.append(table_name['name'])
                    table_name = cursor.fetchone()

                for table_name in flashcard_packs:
                    query = "SELECT COUNT(*) FROM " + table_name + " where memorization >= " + str(AppSettings.Maximum_memorization_state)  + \
                            " or is_learned = 1"
                    cursor = self.db_con.cursor()
                    cursor.execute(query)
                    row = cursor.fetchone()
                    if row is not None:
                        counter += row['COUNT(*)']

                cursor.close()

            except sqlite3.Error as e:
                Logger.error("Can't load tables from SQL-lite database: " + e.__str__())

        return counter

    def get_min_max_limit_for_table(self, table_name):
        """
        Gets minimum and maximum fields to show for table name
        :param table_name:
        :return: minimum and maximum
        """
        min_limit = 0
        max_limit = -1
        if self.db_con:
            try:
                cursor = self.db_con.cursor()
                cursor.execute("SELECT * FROM  pack_setting_limit")
                row = cursor.fetchall()
                if row is not None:
                    for i in row:
                        # if isinstance(i, tuple):
                        #    print("kave\n\n\n\n")
                        #    if i[0] == table_name:
                        #        min_limit = i[1]
                        #        max_limit = i[2]
                        #elif i['table_name'] == table_name:
                        if i['pack_name'] == table_name:
                            min_limit = i['min']
                            max_limit = i['max']

                cursor.close()

            except sqlite3.Error as e:
                Logger.error("Can't load limit settings from SQL-lite database: " + e.__str__())

        return (min_limit, max_limit)

    def set_min_max_limit_for_table(self, pack_name, min_limit, max_limit):
        """
        Sets minimum and maximum fields to show for table name
        :param pack_name:
        :param min_limit:
        :param max_limit:
        :return:
        """
        try:
            cursor = self.db_con.cursor()
            sql_update_query = "REPLACE INTO pack_setting_limit ( pack_name, min, max) VALUES(?,?,?)"
            columns_values = (pack_name, min_limit, max_limit)
            cursor.execute(sql_update_query, columns_values)
            self.db_con.commit()
            cursor.close()

        except sqlite3.Error as e:
            Logger.error("Can't replace limit settings in SQL-lite database: " + e.__str__())

    def count_rows_in_table(self, table_name):
        """
        Counts rows in given table
        :param table_name:
        :return: rows count
        """
        count = 0
        query = "SELECT COUNT(*) FROM {}".format(table_name)
        try:
            cursor = self.db_con.cursor()
            cursor.execute(query)
            row = cursor.fetchone()
            if row is not None:
                count = row['COUNT(*)']
            cursor.close()

        except sqlite3.Error as e:
            Logger.error("Can't  count rows in table: " + table_name + ", error: " + e.__str__())

        return count


    def create_flashcard_pack(self, name):
        """
		try: # English colloquial phrases
			cursor = self.db_con.cursor()
			cursor.execute(""CREATE TABLE English_words_4k (
			                id INTEGER PRIMARY KEY ASC,
				            word varchar(255) NOT NULL ,
				            translate varchar(255) NOT NULL,
				            memorization int DEFAULT 0,
				            sentence text DEFAULT '',
				            sentence_translate text DEFAULT '',
				            processed_sentence text DEFAULT '',
				            last_successful_attempt timestamp,
				            last_failed_attempt timestamp,
				            last_attempt text CHECK(last_attempt in ("failed", "success", "new")),
				            recent_attempts int,
				            is_user_added int,
				            is_learned int,
				            is_added_to_user text CHECK(is_added_to_user in ("yes", "created", "no", "reset"))
				            CHECK (memorization>=0 and memorization<=10) );"")
pType TEXT CHECK( pType IN ('M','R','H') )
		except sqlite3.Error as e:
			# add log file
			print(e)

		except Exception as e:
			print(e)
		"""
        # cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        # insert into spanish values(NULL,"surrender;give up", "сдача;сдаваться;отказ", 2, "ffffffff, surrender df,./","тест сдачи тест" , "ffffffff, сдача df,./", CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, "failed", 0, 1, 0, "created" );
        # insert into spanish values(NULL, "demand", "требовать", 9, "we demand explanation!", "мы требуем объяснений", "we требовать explanation!",CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, "failed", 0, 1, 0, "created");
        # insert into spanish values(NULL,"test2", "тест2", 0, "test2 dfksf , dsfdsfd test2","тест сдачи тест" ,"тест2 dfksf , dsfdsfd тест2",CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, "new", 0, 1, 0, "created" );
        # insert into spanish values(NULL, "test3", "тест3", 0, "test3 dfksf , dsfdsfd test2","тест сдачи тест" , "тест3 dfksf , dsfdsfd test2" ,CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, "success", 0, 1, 0, "created" );
        pass


# CREATE TABLE pack_setting_limit (
#				            pack_name varchar(255) PRIMARY KEY ASC,
#				            min int DEFAULT 0,
#                            max int DEFAULT -1);