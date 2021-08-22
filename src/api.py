from deepl import Translator
from dotenv import dotenv_values


class TranslationClient:
    def __init__(self):
        config = dotenv_values(".env")
        self.client = Translator(config["API_KEY"])

        # Create a target_languages list without English in it
        self.target_languages = []
        for language in self.client.get_target_languages():
            if "en" in language.code.lower():
                continue
            else:
                self.target_languages.append(language.code)

    def translate(self, message, target_language):
        """
        Translate's one message into target language.

        Args:
            message: String message. This should be a single sentence.
            target_language: Language code to translate message to.
        """
        return self.__translate_helper(message, target_language)

    def translate_batch(self, messages, target_language):
        """
        Translate a list of messages into target language.

        Args:
            messages: List of string messages.
            target_language: Language code to translate message to.
        """
        return self.__translate_helper(messages, target_language)

    def translate_file(self, input_file, output_file, target_language):
        """
        Translate a local file into target language.

        Args:
            input_file: Input file to translate.
            output_file: Output file to write to.
            target_language: Language code to translate message to.
        """
        self.client.translate_document_from_filepath(input_file, output_file, target_lang=target_language)

    """ ================ Helper functions ================ """
    def __translate_helper(self, text, target_language):
        self.__check_limit()

        result = self.client.translate_text(text, target_lang=target_language)
        return result

    def __check_limit(self):
        usage = self.client.get_usage()
        if usage.character.limit_exceeded:
            raise Exception("Character limit exceeded for this month.")
