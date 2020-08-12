# -*- coding: utf-8 -*-


from iconservice import *
from .consts import *
from ..scorelib.utils import *
from ..scorelib.linked_list import *


class AnswerCooldownNotReached(Exception):
    pass


class InvalidUserAccountUsername(Exception):
    pass


class InvalidUserAccountAvatar(Exception):
    pass


class UserAccountDoesntExist(Exception):
    pass


class UserAccountAlreadyExists(Exception):
    pass


class UserAccounts(UIDLinkedListDB):
    _NAME = 'USER_ACCOUNTS'

    def __init__(self, db: IconScoreDatabase):
        name = f'{UserAccounts._NAME}'
        super().__init__(name, db)
        self._address_to_uid_map = DictDB(f'{name}_ADDRESS_TO_UID_MAP', db, value_type=int)
        self._name = name
        self._db = db

    def check_doesnt_exist(self, user_address: Address) -> None:
        if self._address_to_uid_map[str(user_address)] != 0:
            raise UserAccountAlreadyExists(self._name, str(user_address))

    def check_exists(self, user_address: Address) -> None:
        if self._address_to_uid_map[str(user_address)] == 0:
            raise UserAccountDoesntExist(self._name, str(user_address))

    def add(self, user_uid: int, user_address: Address):
        self._address_to_uid_map[str(user_address)] = user_uid
        self.append(user_uid)

    def get_user_uid(self, user_address: Address) -> int:
        self.check_exists(user_address)
        return self._address_to_uid_map[str(user_address)]


class UserAccountFactory(IdFactory):

    _NAME = 'USER_ACCOUNT_FACTORY'

    def __init__(self, db: IconScoreDatabase):
        name = UserAccountFactory._NAME
        super().__init__(name, db)
        self._name = name
        self._db = db

    def create(self,
               address: Address,
               avatar_uid: int,
               username: str) -> int:
        uid = self.get_uid()
        user = UserAccount(uid, self._db)
        user._avatar_uid.set(avatar_uid)
        user._username.set(username)
        user._address.set(address)
        return uid


class UserAccount:
    _NAME = 'USER_ACCOUNT'

    # ================================================
    #  Initialization
    # ================================================
    def __init__(self, uid: int, db: IconScoreDatabase):
        name = f'{UserAccount._NAME}_{uid}'
        self._last_answer_timestamp = VarDB(f'{name}_LAST_ANSWER_TIMESTAMP', db, value_type=int)
        self._avatar_uid = VarDB(f'{name}_AVATAR_UID', db, value_type=int)
        self._username = VarDB(f'{name}_USERNAME', db, value_type=str)
        self._address = VarDB(f'{name}_ADDRESS', db, value_type=Address)
        self._name = name
        self._uid = uid
        self._db = db

    # ================================================
    #  Checks
    # ================================================
    def check_answer_cooldown(self, now: int) -> None:
        last = self._last_answer_timestamp.get()
        if last == 0:
            # No answer yet
            return

        if (last + ANSWER_COOLDOWN) > now:
            raise AnswerCooldownNotReached(self._name, last + ANSWER_COOLDOWN, now)

    @staticmethod
    def check_username(username: str) -> None:
        if len(username) > 50:
            raise InvalidUserAccountUsername(username)

    @staticmethod
    def check_avatar(avatar: int) -> None:
        if not avatar in list(range(1, USER_AVATARS_COUNT + 1)):
            raise InvalidUserAccountAvatar(avatar)

    # ================================================
    #  Private Methods
    # ================================================

    # ================================================
    #  Public Methods
    # ================================================
    def uid(self) -> int:
        return self._uid

    def address(self) -> Address:
        return self._address.get()

    def set_last_answer_timestamp(self, now: int) -> None:
        self._last_answer_timestamp.set(now)

    def set_username(self, username: str) -> None:
        self._username.set(username)

    def set_avatar(self, avatar_uid: int) -> None:
        self._avatar_uid.set(avatar_uid)

    def serialize(self) -> dict:
        return {
            'uid': self._uid,
            'address': self._address.get(),
            'avatar_uid': self._avatar_uid.get(),
            'username': self._username.get(),
        }
