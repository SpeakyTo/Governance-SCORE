

from iconservice import *
from .checks import *
from .version import *
from .consts import *
from .maintenance import *
from .speakyto.user_account import *
from .speakyto.question import *
from .speakyto.answer import *
from .speakyto.level import *
from .speakyto.iso_639_1 import *
from .interfaces.irc2 import *


class InvalidCallParameters(Exception):
    pass


class SpeakyTo(IconScoreBase):
    """ SpeakyTo SCORE Base implementation """

    _NAME = 'SpeakyToGovernance'

    # ================================================
    #  Event Logs
    # ================================================
    @eventlog
    def ShowException(self, exception: str):
        pass

    @eventlog(indexed=1)
    def QuestionCreatedEvent(self, uid: int):
        pass

    @eventlog(indexed=1)
    def AnswerCreatedEvent(self, uid: int):
        pass

    @eventlog(indexed=1)
    def UserAccountCreatedEvent(self, uid: int):
        pass

    # ================================================
    #  Initialization
    # ================================================
    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self._experience_contract = VarDB(f'{SpeakyTo._NAME}_EXPERIENCE_CONTRACT', db, value_type=Address)

    def on_install(self) -> None:
        super().on_install()
        SCOREMaintenance(self.db).disable()
        Version(self.db).update(VERSION)

    def on_update(self) -> None:
        super().on_update()
        version = Version(self.db)

        version.update(VERSION)

    # ================================================
    #  Migration methods
    # ================================================

    # ================================================
    #  Internal methods
    # ================================================
    def _do_refund_question_reward(self, question: Question) -> None:
        if question.reward() > 0:
            question_user = UserAccount(question.user_uid(), self.db)
            self.icx.transfer(question_user.address(), question.reward())

    def _do_remove_experience_create_question(self, question: Question) -> None:
        experience_interface = self._experience_interface()
        experience_system = ExperienceSystem(experience_interface, self.db)
        experience_system.remove_experience(question.user_uid(), Experience.CREATE_QUESTION)

    def _do_cancel_question(self, question: Question) -> None:

        # Refund the reward (if any) to OP
        self._do_refund_question_reward(question)
        # Remove experience
        self._do_remove_experience_create_question(question)

        # Change question state
        question.cancel()
        UserQuestionDB(question.user_uid(), self.db).remove(question.uid())
        UserOpenedQuestionDB(question.user_uid(), self.db).remove(question.uid())

    def _do_delete_question(self, question: Question) -> None:

        # Refund the reward (if any) to OP
        self._do_refund_question_reward(question)
        # Remove experience
        self._do_remove_experience_create_question(question)

        # Delete question and all associated answers
        UserQuestionDB(question.user_uid(), self.db).remove(question.uid())
        UserOpenedQuestionDB(question.user_uid(), self.db).remove(question.uid())
        QuestionDB(self.db).remove(question.uid())

        answers = list(AnswerDB(question.uid(), self.db))
        for answer_uid in answers:
            AnswerDB(question.uid(), self.db).remove(answer_uid)
            answer = Answer(answer_uid, self.db)
            answer.delete()

        question.delete()

    def _create_question_in_databases(self, question_uid: int, user_uid: int) -> None:
        QuestionDB(self.db).append(question_uid)
        UserQuestionDB(user_uid, self.db).append(question_uid)
        UserOpenedQuestionDB(user_uid, self.db).append(question_uid)

    def _experience_interface(self):
        return self.create_interface_score(self._experience_contract.get(), IRC2Interface)

    # ================================================
    #  Checks
    # ================================================

    # ================================================
    #  External methods (write access)
    # ================================================
    @catch_error
    @check_maintenance
    @external
    @payable
    def create_user_account(self, avatar_uid: int, username: str) -> None:
        user_address = self.msg.sender

        # -- Checks
        UserAccounts(self.db).check_doesnt_exist(user_address)

        # -- OK from here
        user_uid = UserAccountFactory(self.db).create(user_address, avatar_uid, username)
        UserAccounts(self.db).add(user_uid, self.msg.sender)

        self.UserAccountCreatedEvent(user_uid)

    @catch_error
    @check_maintenance
    @external
    @payable
    def create_question_level1(self, data: str, from_language: str, to_language: str) -> None:
        """ How To Say ... from ... in ... ? """
        user_uid = UserAccounts(self.db).get_user_uid(self.msg.sender)
        user = UserAccount(user_uid, self.db)
        reward = self.msg.value
        experience_interface = self._experience_interface()

        # -- Checks
        level_system = LevelSystem(experience_interface, self.db)
        level_system.check_can_create_question(user.uid(), 1)
        Question.check_level1_data(data)
        ISO_639_1.check_valid_code(from_language)
        ISO_639_1.check_valid_code(to_language)

        # -- OK from here
        question_uid = QuestionFactory(self.db).create(
            user.uid(),
            data,
            from_language,
            to_language,
            reward,
            1)
        self.QuestionCreatedEvent(question_uid)

        self._create_question_in_databases(question_uid, user.uid())

        # Give XP to OP
        experience_system = ExperienceSystem(experience_interface, self.db)
        experience_system.give_experience(user.uid(), Experience.CREATE_QUESTION)

    @catch_error
    @check_maintenance
    @external
    @payable
    def create_question_level2(self, data: str, from_language: str, to_language: str) -> None:
        """ What does ... means from ... in ... ? """
        user_uid = UserAccounts(self.db).get_user_uid(self.msg.sender)
        user = UserAccount(user_uid, self.db)
        reward = self.msg.value
        experience_interface = self._experience_interface()

        # -- Checks
        level_system = LevelSystem(experience_interface, self.db)
        level_system.check_can_create_question(user.uid(), 2)
        Question.check_level2_data(data)
        ISO_639_1.check_valid_code(from_language)
        ISO_639_1.check_valid_code(to_language)

        # -- OK from here
        question_uid = QuestionFactory(self.db).create(
            user.uid(),
            data,
            from_language,
            to_language,
            reward,
            2)
        self.QuestionCreatedEvent(question_uid)

        self._create_question_in_databases(question_uid, user.uid())

        # Give XP to OP
        experience_system = ExperienceSystem(experience_interface, self.db)
        experience_system.give_experience(user.uid(), Experience.CREATE_QUESTION)

    @catch_error
    @check_maintenance
    @external
    @payable
    def create_question_level3(self, data: str, from_language: str, to_language: str) -> None:
        """ What's the difference between ... and ... in ... ? """
        user_uid = UserAccounts(self.db).get_user_uid(self.msg.sender)
        user = UserAccount(user_uid, self.db)
        reward = self.msg.value
        experience_interface = self._experience_interface()

        # -- Checks
        level_system = LevelSystem(experience_interface, self.db)
        level_system.check_can_create_question(user.uid(), 3)
        Question.check_level3_data(data)
        ISO_639_1.check_valid_code(from_language)
        ISO_639_1.check_valid_code(to_language)

        # -- OK from here
        question_uid = QuestionFactory(self.db).create(
            user.uid(),
            data,
            from_language,
            to_language,
            reward,
            3)
        self.QuestionCreatedEvent(question_uid)

        self._create_question_in_databases(question_uid, user.uid())

        # Give XP to OP
        experience_system = ExperienceSystem(experience_interface, self.db)
        experience_system.give_experience(user.uid(), Experience.CREATE_QUESTION)

    @catch_error
    @check_maintenance
    @external
    @payable
    def create_question_level4(self, data: str, from_language: str, to_language: str) -> None:
        """ Show me an example (from ... in ...) """
        user_uid = UserAccounts(self.db).get_user_uid(self.msg.sender)
        user = UserAccount(user_uid, self.db)
        reward = self.msg.value
        experience_interface = self._experience_interface()

        # -- Checks
        level_system = LevelSystem(experience_interface, self.db)
        level_system.check_can_create_question(user.uid(), 4)
        Question.check_level4_data(data)
        ISO_639_1.check_valid_code(from_language)
        ISO_639_1.check_valid_code(to_language)

        # -- OK from here
        question_uid = QuestionFactory(self.db).create(
            user.uid(),
            data,
            from_language,
            to_language,
            reward,
            4)
        self.QuestionCreatedEvent(question_uid)

        self._create_question_in_databases(question_uid, user.uid())

        # Give XP to OP
        experience_system = ExperienceSystem(experience_interface, self.db)
        experience_system.give_experience(user.uid(), Experience.CREATE_QUESTION)

    @catch_error
    @check_maintenance
    @external
    @payable
    def create_question_level5(self, data: str, from_language: str, to_language: str) -> None:
        """ Ask me anything (from ... in ...) """
        user_uid = UserAccounts(self.db).get_user_uid(self.msg.sender)
        user = UserAccount(user_uid, self.db)
        reward = self.msg.value
        experience_interface = self._experience_interface()

        # -- Checks
        level_system = LevelSystem(experience_interface, self.db)
        level_system.check_can_create_question(user.uid(), 5)
        Question.check_level5_data(data)
        ISO_639_1.check_valid_code(from_language)
        ISO_639_1.check_valid_code(to_language)

        # -- OK from here
        question_uid = QuestionFactory(self.db).create(
            user.uid(),
            data,
            from_language,
            to_language,
            reward,
            5)
        self.QuestionCreatedEvent(question_uid)

        self._create_question_in_databases(question_uid, user.uid())

        # Give XP to OP
        experience_system = ExperienceSystem(experience_interface, self.db)
        experience_system.give_experience(user.uid(), Experience.CREATE_QUESTION)

    @catch_error
    @check_maintenance
    @external
    def answer_question(self, question_uid: int, data: str) -> None:
        user_uid = UserAccounts(self.db).get_user_uid(self.msg.sender)
        user = UserAccount(user_uid, self.db)
        question = Question(question_uid, self.db)
        experience_interface = self._experience_interface()

        # -- Checks
        user.check_answer_cooldown(self.now())
        question.check_opened()

        # -- OK from here
        answer_uid = AnswerFactory(self.db).create(
            user.uid(),
            question_uid,
            data)
        self.AnswerCreatedEvent(answer_uid)

        answers = AnswerDB(question_uid, self.db)
        answers.append(answer_uid)

        # Set the latest answer as now
        user.set_last_answer_timestamp(self.now())

        # Give XP to answer poster
        experience_system = ExperienceSystem(experience_interface, self.db)
        experience_system.give_experience(user.uid(), Experience.ANSWER_QUESTION)

    @catch_error
    @check_maintenance
    @external
    def select_answer(self, answer_uid: int) -> None:
        user_uid = UserAccounts(self.db).get_user_uid(self.msg.sender)
        user = UserAccount(user_uid, self.db)
        answer = Answer(answer_uid, self.db)
        question = Question(answer.question_uid(), self.db)
        experience_interface = self._experience_interface()

        # -- Checks
        question.check_opened()
        question.check_is_op(user.uid())

        # -- OK from here
        # Set the question as answered
        question.select_answer(answer_uid)
        UserOpenedQuestionDB(question.user_uid(), self.db).remove(question.uid())

        # Give XP to OP and answer poster
        experience_system = ExperienceSystem(experience_interface, self.db)
        experience_system.give_experience(user.uid(), Experience.SELECT_ANSWER)
        experience_system.give_experience(answer.user_uid(), Experience.ANSWER_SELECTED)

        # Send ICX reward if any
        if question.reward() > 0:
            answer_user = UserAccount(answer.user_uid(), self.db)
            self.icx.transfer(answer_user.address(), question.reward())
            # Bonus XP
            experience_system.give_experience(user.uid(), Experience.SELECT_ANSWER_BONUS_REWARD)

    @catch_error
    @check_maintenance
    @external
    def cancel_question(self, question_uid: int) -> None:
        user_uid = UserAccounts(self.db).get_user_uid(self.msg.sender)
        user = UserAccount(user_uid, self.db)
        question = Question(question_uid, self.db)

        # -- Checks
        question.check_opened()
        question.check_is_op(user.uid())
        AnswerDB(question_uid, self.db).check_empty()

        # -- OK from here
        self._do_cancel_question(question)

    @payable
    def fallback(self):
        pass

    @catch_error
    @check_maintenance
    @external
    def tokenFallback(self, _from: Address, _value: int, _data: bytes) -> None:
        pass

    # ================================================
    #  External methods (readonly)
    # ================================================
    # --- Meta methods
    @catch_error
    @external(readonly=True)
    def maintenance_enabled(self) -> bool:
        return SCOREMaintenance(self.db).is_enabled()

    @catch_error
    @external(readonly=True)
    def version(self) -> str:
        return Version(self.db).get()

    @external(readonly=True)
    def name(self) -> str:
        return SpeakyTo._NAME

    # ========= App methods =========
    # ------ Q&A System ------
    @catch_error
    @external(readonly=True)
    def get_question(self, question_uid: int) -> dict:
        question = Question(question_uid, self.db)
        return question.serialize()

    @catch_error
    @external(readonly=True)
    def get_questions(self, offset: int) -> list:
        return [
            Question(question_uid, self.db).serialize()
            for question_uid in QuestionDB(self.db).select(offset)
        ]

    @catch_error
    @external(readonly=True)
    def get_answer(self, answer_uid: int) -> dict:
        answer = Answer(answer_uid, self.db)
        return answer.serialize()

    @catch_error
    @external(readonly=True)
    def get_answers(self, question_uid: int, offset: int) -> list:
        return [
            Answer(answer_uid, self.db).serialize()
            for answer_uid in AnswerDB(question_uid, self.db).select(offset)
        ]

    @catch_error
    @external(readonly=True)
    def get_experience_contract(self) -> Address:
        return self._experience_contract.get()

    @catch_error
    @external(readonly=True)
    def get_supported_languages(self) -> list:
        return ISO_639_1.supported_languages

    @catch_error
    @external(readonly=True)
    def get_user_uid(self, user_address: Address) -> int:
        return UserAccounts(self.db).get_user_uid(user_address)

    # ------ User System ------
    @catch_error
    @external
    def set_user_avatar(self, avatar_uid: int) -> None:
        user_uid = UserAccounts(self.db).get_user_uid(self.msg.sender)

        # -- Checks
        UserAccount.check_avatar(avatar_uid)
        # -- OK from here
        user = UserAccount(user_uid, self.db)
        user.set_avatar(avatar_uid)

    @catch_error
    @external
    def set_user_username(self, username: str) -> None:
        user_uid = UserAccounts(self.db).get_user_uid(self.msg.sender)

        # -- Checks
        UserAccount.check_username(username)

        # -- OK from here
        user = UserAccount(user_uid, self.db)
        user.set_username(username)

    @catch_error
    @external(readonly=True)
    def get_user_account(self, user_uid: int) -> dict:
        user = UserAccount(user_uid, self.db)
        return user.serialize()

    @catch_error
    @external(readonly=True)
    def get_user_level(self, user_uid: int) -> int:
        experience_system = ExperienceSystem(self._experience_interface(), self.db)
        return experience_system.get_level(user_uid)

    @catch_error
    @external(readonly=True)
    def get_user_experience(self, user_uid: int) -> int:
        experience_system = ExperienceSystem(self._experience_interface(), self.db)
        return experience_system.get_experience(user_uid)

    @catch_error
    @external(readonly=True)
    def get_user_questions(self, user_uid: int, offset: int) -> list:
        return [
            Question(question_uid, self.db).serialize()
            for question_uid in UserQuestionDB(user_uid, self.db).select(offset)
        ]

    # ================================================
    #  Operator methods
    # ================================================
    @catch_error
    @external
    @only_owner
    def set_maintenance_mode(self, mode: int) -> None:
        if mode == SCOREMaintenanceMode.ENABLED:
            SCOREMaintenance(self.db).enable()
        elif mode == SCOREMaintenanceMode.DISABLED:
            SCOREMaintenance(self.db).disable()

    @catch_error
    @external
    @only_owner
    def admin_cancel_question(self, question_uid: int) -> None:
        question = Question(question_uid, self.db)
        question.check_initialized()
        self._do_cancel_question(question)

    @catch_error
    @external
    @only_owner
    def admin_delete_question(self, question_uid: int) -> None:
        question = Question(question_uid, self.db)
        question.check_initialized()
        self._do_delete_question(question)

    @catch_error
    @external
    @only_owner
    def set_experience_contract(self, address: Address) -> None:
        self._experience_contract.set(address)
