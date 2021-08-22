import os


from recipe_scrapers import scrape_me


from src.api import TranslationClient


class Recipe:
    def __init__(self, recipe_url):
        """
        Constructor for recipe class (scraper version).

        Using the API:
        scraper = scrape_me('https://www.allrecipes.com/recipe/158968/spinach-and-feta-turkey-burgers/')

        Args:
            recipe_url: A https link to a recipe.
        """
        scraped = scrape_me(recipe_url)

        self.__check_ingredients(scraped)

        # Attributes to translate
        self.title = scraped.title()
        self.total_time = scraped.total_time()
        self.ingredients = scraped.ingredients()
        self.instructions = scraped.instructions().split("\n")

        # Keep a copy for comparison's sake later
        self.original_title = self.title
        self.original_total_time = self.total_time
        self.original_ingredients = self.ingredients
        self.original_instructions = self.instructions

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
        for i in range(runs):
            language = self.translator.target_languages[i]

            self.__translate(language)

        # Translate back into English
        self.__translate("EN-US")

    def write_to_disk(self, file_name=None):
        """
        Writes the recipe to a text file to disk.

        Args:
            file_name: Optional; File name to wrtie to.
        """
        if not file_name:
            file_name = f"Scrambled: {self.title}.txt"

        with open(file_name, "w", newline="") as write_file:
            write_file.write(self.title)
            write_file.write("\n\n\n")

            write_file.write(self.total_time)
            write_file.write("\n\n\n")

            write_file.write("Ingredients:")
            for item in self.ingredients:
                write_file.write(f"{item}\n")
            write_file.write("\n\n\n")

            write_file.write("Instructions:")
            for item in self.instructions:
                write_file.write(f"{item}\n")
            write_file.write("\n\n\n")

    """ ================ Helper functions ================"""
    def __check_ingredients(self, recipe):
        # Check allergies
        # for item in recipe.ingredients():
        pass

    def __translate(self, language):
        title_time = self.translator.translate_batch([self.title, self.total_time], language)
        self.title = title_time[0].text
        self.total_time = title_time[1].text

        ingredients = self.translator.translate_batch(self.ingredients, language)
        translated_ingredients = [item.text for item in ingredients]

        if len(self.ingredients) != len(translated_ingredients):
            raise ValueError("Mismatched results for ingredients")

        self.ingredients = translated_ingredients

        instructions = self.translator.translate_batch(self.instructions, language)
        translated_instructions = [item.text for item in instructions]

        if len(self.instructions) != len(translated_instructions):
            raise ValueError("Mismatched results for instructions")

        self.instructions = translated_instructions
