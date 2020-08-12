
from iconservice import *
from .user_account import *


class Experience:

    ANSWER_QUESTION = 10
    CREATE_QUESTION = 100
    SELECT_ANSWER = 200
    SELECT_ANSWER_BONUS_REWARD = 200
    ANSWER_SELECTED = 500


class ExperienceTable:

    _table = [
        0,      # Level 1
        1000,   # Level 2
        4000,   # Level 3
        12000,  # Level 4
        24000,  # Level 5
        40000   # Level 6
    ]

    MAX_LEVEL = len(_table)

    @classmethod
    def get_level(cls, experience: int) -> int:
        if experience < 0:
            return 0

        for i in range(len(cls._table) - 1):
            if (cls._table[i] <= experience < cls._table[i + 1]):
                return i + 1

        return cls.MAX_LEVEL


class ExperienceSystem:

    _NAME = 'EXPERIENCE_SYSTEM'

    def __init__(self, interface, db: IconScoreDatabase):
        name = f'{ExperienceSystem._NAME}'
        self._interface = interface
        self._name = name
        self._db = db

    def get_experience(self, user_uid: int) -> int:
        Logger.warning(f"user_uid={user_uid}")
        user_address = UserAccount(user_uid, self._db).address()
        Logger.warning(f"user_address={user_address}")
        return self._interface.balanceOf(user_address)

    def get_level(self, user_uid: int) -> int:
        experience = self.get_experience(user_uid)
        return ExperienceTable.get_level(experience)

    def give_experience(self, user_uid: int, amount: int) -> None:
        user_address = UserAccount(user_uid, self._db).address()
        self._interface.treasury_withdraw(user_address, amount)

    def remove_experience(self, user_uid: int, amount: int) -> None:
        user_experience = self.get_experience(user_uid)
        user_address = UserAccount(user_uid, self._db).address()
        if user_experience > amount:
            self._interface.treasury_deposit(user_address, amount)
        else:
            self._interface.treasury_deposit(user_address, user_experience)
