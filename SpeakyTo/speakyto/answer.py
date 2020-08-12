# -*- coding: utf-8 -*-


from iconservice import *
from .consts import *
from ..scorelib.id_factory import *
from ..scorelib.utils import *
from ..scorelib.linked_list import *


class AnswerDBNotEmpty(Exception):
    pass


class AnswerDoesntExist(Exception):
    pass


class AnswerFactory(IdFactory):

    _NAME = 'ANSWER_FACTORY'

    def __init__(self, db: IconScoreDatabase):
        name = AnswerFactory._NAME
        super().__init__(name, db)
        self._name = name
        self._db = db

    def create(self,
               user_uid: int,
               question_uid: int,
               data: str) -> int:
        uid = self.get_uid()
        answer = Answer(uid, self._db)
        answer._user_uid.set(user_uid)
        answer._question_uid.set(question_uid)
        answer._data.set(data)
        return uid


class Answer:

    _NAME = 'ANSWER'

    # ================================================
    #  Initialization
    # ================================================
    def __init__(self, uid: int, db: IconScoreDatabase):
        self._name = f'{Answer._NAME}_{uid}'
        self._user_uid = VarDB(f'{self._name}_USER_UID', db, value_type=int)
        self._question_uid = VarDB(f'{self._name}_QUESTION_UID', db, value_type=int)
        self._data = VarDB(f'{self._name}_DATA', db, value_type=str)
        self._db = db
        self._uid = uid

    # ================================================
    #  Checks
    # ================================================

    # ================================================
    #  Private Methods
    # ================================================

    # ================================================
    #  Public Methods
    # ================================================
    def user_uid(self) -> int:
        return self._user_uid.get()

    def question_uid(self) -> int:
        return self._question_uid.get()

    def serialize(self) -> dict:
        return {
            'uid': self._uid,
            'user_uid': self._user_uid.get(),
            'question_uid': self._question_uid.get(),
            'data': self._data.get()
        }

    def delete(self) -> None:
        self._user_uid.remove()
        self._question_uid.remove()
        self._data.remove()


class AnswerDB(UIDLinkedListDB):
    _NAME = 'ANSWER_DB'

    def __init__(self, question_uid: int, db: IconScoreDatabase):
        name = f'{AnswerDB._NAME}_{question_uid}'
        super().__init__(name, db)
        self._name = name
        self._db = db

    # ================================================
    #  Checks
    # ================================================
    def check_empty(self) -> None:
        answer_count = len(self)
        if answer_count > 0:
            raise AnswerDBNotEmpty(self._name)
