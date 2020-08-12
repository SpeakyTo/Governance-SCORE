# -*- coding: utf-8 -*-

from iconservice import *


class InvalidLanguageCode(Exception):
    pass


class ISO_639_1:

    supported_languages = [
        "en", 	# English
        "es", 	# Spanish
        "zh", 	# Chinese
        "fr", 	# French
        "de", 	# German
        "ko", 	# Korean
        "ru", 	# Russian
        "ja", 	# Japanese
    ]

    @staticmethod
    def check_valid_code(code: str):
        if not code in ISO_639_1.supported_languages:
            raise InvalidLanguageCode(code, ISO_639_1.supported_languages)
