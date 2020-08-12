# -*- coding: utf-8 -*-


from iconservice import *
from .consts import *
from ..scorelib.id_factory import *
from ..scorelib.utils import *
from ..scorelib.linked_list import *


class InvalidQuestionState(Exception):
    pass


class InvalidQuestionData(Exception):
    pass


class InvalidUserUid(Exception):
    pass


class QuestionDoesntExist(Exception):
    pass


class QuestionState:
    UNINITIALIZED = 0
    CLOSED = 1
    OPENED = 2
    ANSWERED = 3
    CANCELLED = 4


class QuestionFactory(IdFactory):

    _NAME = 'QUESTION_FACTORY'

    def __init__(self, db: IconScoreDatabase):
        name = QuestionFactory._NAME
        super().__init__(name, db)
        self._name = name
        self._db = db

    def create(self,
               user_uid: int,
               data: str,
               from_language: str,
               to_language: str,
               reward: int,
               level: int) -> int:
        uid = self.get_uid()
        question = Question(uid, self._db)
        question._user_uid.set(user_uid)
        question._answer_uid.set(0)
        question._data.set(data)
        question._from_language.set(from_language)
        question._to_language.set(to_language)
        question._reward.set(reward)
        question._level.set(level)
        question._state.set(QuestionState.OPENED)
        return uid


class Question:

    _NAME = 'QUESTION'

    # ================================================
    #  Initialization
    # ================================================
    def __init__(self, uid: int, db: IconScoreDatabase):
        self._name = f'{Question._NAME}_{uid}'
        self._user_uid = VarDB(f'{self._name}_USER_UID', db, value_type=int)
        self._answer_uid = VarDB(f'{self._name}_ANSWER_UID', db, value_type=int)
        self._data = VarDB(f'{self._name}_DATA', db, value_type=str)
        self._from_language = VarDB(f'{self._name}_FROM_LANGUAGE', db, value_type=str)
        self._to_language = VarDB(f'{self._name}_TO_LANGUAGE', db, value_type=str)
        self._reward = VarDB(f'{self._name}_REWARD', db, value_type=int)
        self._state = VarDB(f'{self._name}_STATE', db, value_type=int)
        self._level = VarDB(f'{self._name}_LEVEL', db, value_type=int)
        self._db = db
        self._uid = uid

    # ================================================
    #  Checks
    # ================================================
    def check_opened(self) -> None:
        if self._state.get() != QuestionState.OPENED:
            raise InvalidQuestionState(self._name, Utils.get_enum_name(QuestionState, self._state.get()))

    def check_initialized(self) -> None:
        if self._state.get() == QuestionState.UNINITIALIZED:
            raise InvalidQuestionState(self._name, Utils.get_enum_name(QuestionState, self._state.get()))

    def check_is_op(self, user_uid: int) -> None:
        if user_uid != self._user_uid.get():
            raise InvalidUserUid(self._name, self._user_uid.get(), user_uid)

    @staticmethod
    def check_level1_data(data: str) -> None:
        if len(data) > QUESTION_LEVEL_1_MAX_DATA_LENGTH:
            raise InvalidQuestionData()

    @staticmethod
    def check_level2_data(data: str) -> None:
        if len(data) > QUESTION_LEVEL_2_MAX_DATA_LENGTH:
            raise InvalidQuestionData()

    @staticmethod
    def check_level3_data(data: str) -> None:
        json_data = json_loads(data)
        word1, word2 = json_data['word1'], json_data['word2']
        if (len(word1) > QUESTION_LEVEL_3_MAX_DATA_LENGTH or
                len(word2) > QUESTION_LEVEL_3_MAX_DATA_LENGTH):
            raise InvalidQuestionData()

    @staticmethod
    def check_level4_data(data: str) -> None:
        pass

    @staticmethod
    def check_level5_data(data: str) -> None:
        pass

    # ================================================
    #  Private Methods
    # ================================================

    # ================================================
    #  Public Methods
    # ================================================
    def uid(self) -> int:
        return self._uid

    def reward(self) -> int:
        return self._reward.get()

    def user_uid(self) -> int:
        return self._user_uid.get()

    def cancel(self) -> None:
        self._state.set(QuestionState.CANCELLED)

    def select_answer(self, answer_uid: int) -> None:
        self._answer_uid.set(answer_uid)
        self._state.set(QuestionState.ANSWERED)

    def serialize(self) -> dict:
        return {
            'uid': self._uid,
            'user_uid': self._user_uid.get(),
            'answer_uid': self._answer_uid.get(),
            'state': Utils.get_enum_name(QuestionState, self._state.get()),
            'data': self._data.get(),
            'from_language': self._from_language.get(),
            'to_language': self._to_language.get(),
            'reward': self._reward.get(),
            'level': self._level.get()
        }

    def delete(self) -> None:
        self._user_uid.remove()
        self._answer_uid.remove()
        self._data.remove()
        self._from_language.remove()
        self._to_language.remove()
        self._reward.remove()
        self._state.remove()
        self._level.remove()


class QuestionDB(UIDLinkedListDB):
    _NAME = 'QUESTION_DB'

    def __init__(self, db: IconScoreDatabase):
        name = QuestionDB._NAME
        super().__init__(name, db)
        self._name = name
        self._db = db


class UserQuestionDB(UIDLinkedListDB):
    _NAME = 'USER_QUESTION_DB'

    def __init__(self, user_uid: int, db: IconScoreDatabase):
        name = f'{UserQuestionDB._NAME}_{user_uid}'
        super().__init__(name, db)
        self._name = name
        self._db = db


class UserOpenedQuestionDB(UIDLinkedListDB):
    _NAME = 'USER_OPENED_QUESTION_DB'

    def __init__(self, user_uid: int, db: IconScoreDatabase):
        name = f'{UserOpenedQuestionDB._NAME}_{user_uid}'
        super().__init__(name, db)
        self._name = name
        self._db = db
