import os
import pdfkit
import tempfile

from src.api import TranslationClient


class Recipe:
    def __init__(self, recipe_url):
        """
        Constructor for recipe class (PDF version).

        Args:
            recipe_url: A https link to a recipe.
        """
        self.recipe_url = recipe_url
        self.translator = TranslationClient()

    def scramble_recipe(self, runs=None):
        """
        Translates a recipe. It will translate it n + 1 times, where n is runs, and the
        last one being back into English.

        If runs is not set, the function will attempt to translate to all languages
        available to DeepL.

        Args:
            runs: Optional int; How many times to translate a recipe into a foreign (non-English)
                language before a final translation back to English is done. Default is None.
        """
        if not runs:
            runs = len(self.translator.target_languages)

        # Scramble!
        recipe_file = "recipe.pdf"
        pdfkit.from_url(self.recipe_url, recipe_file)

        for i in range(runs):
            language = self.translator.target_languages[i]

            self.translator.translate_file(recipe_file, recipe_file, language)

        # Translate back into English
        self.translator.translate_file(recipe_file, recipe_file, "EN")

