
from iconservice import *
from .experience import *
from .question import *


class InvalidUserLevel(Exception):
    pass


class TooMuchOpenedQuestions(Exception):
    pass


class LevelSystem:
    """
        Level 1 : You cannot open more than 1 question at the same time
        Level 2 : Cannot open more than 3 questions at the same time
        Level 3 : 5 questions
        Level 4 : 10 questions
        Level 5 and above : Unlimited questions
    """
    _table_max_opened_questions = {
        0: 0,
        1: 1,
        2: 3,
        3: 5,
        4: 10
    }

    def __init__(self, interface, db: IconScoreDatabase):
        self._interface = interface
        self._db = db

    def check_can_create_question(self, user_uid: int, required_level: int) -> None:
        experience_system = ExperienceSystem(self._interface, self._db)
        user_level = experience_system.get_level(user_uid)

        # Check required level for the question
        if user_level < required_level:
            raise InvalidUserLevel(user_level, required_level)

        # Check opened question count
        if user_level in LevelSystem._table_max_opened_questions:
            opened_questions_count = len(UserOpenedQuestionDB(user_uid, self._db))
            max_questions_count = LevelSystem._table_max_opened_questions[user_level]
            # Check if the user can opened a new question
            if opened_questions_count + 1 > max_questions_count:
                raise TooMuchOpenedQuestions(user_uid, max_questions_count)
