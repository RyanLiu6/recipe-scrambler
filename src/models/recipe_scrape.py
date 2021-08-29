from mdutils.mdutils import MdUtils
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

        # Attributes to translate
        self.title = scraped.title()
        self.total_time = scraped.total_time()
        self.ingredients = scraped.ingredients()
        self.instructions = scraped.instructions().split("\n")

        self.__check_ingredients()

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
        if not file_name:
            file_name = f"Scrambled: {self.title}"

        md_file = MdUtils(file_name=file_name,title=self.title)
        md_file.new_line(f"Total Cooking Time: {self.total_time}")
        md_file.new_line()

        md_file.new_header(level=2, title="Ingredients")
        table_values = ["Ingredient", "Additional Info"]
        for item in self.ingredients:
            table_values.extend([item.ingredient, item.additional_info])
        md_file.new_line()
        md_file.new_table(columns=2, rows=len(self.ingredients) + 1, text=table_values, text_align='center')

        md_file.new_header(level=2, title="Instructions")
        for i in range(len(self.instructions)):
            md_file.new_line(f"{i + 1}: {self.instructions[i]}")
        md_file.new_line()

        md_file.new_table_of_contents(table_title='Contents', depth=2)
        md_file.create_md_file()

    """ ================ Helper functions ================"""
    def __check_ingredients(self):
        parsed_ingredients = []

        """
        Here, we:
        1. Check for allergies
        2. Convert them into Ingredient objects
        """
        for item in self.ingredients:
            parsed_ingredients.append(Ingredient(item))

        self.ingredients = parsed_ingredients

    def __translate(self, language):
        title_time = self.translator.translate_batch([self.title, self.total_time], language)
        self.title = title_time[0].text
        self.total_time = title_time[1].text

        for item in self.ingredients:
            result = self.translator.translate(item.ingredient, language)
            item.ingredient = result.text

            if item.additional_info:
                result = self.translator.translate(item.additional_info, language)
                item.additional_info = result.text

        instructions = self.translator.translate_batch(self.instructions, language)
        translated_instructions = [item.text for item in instructions]

        if len(self.instructions) != len(translated_instructions):
            raise ValueError("Mismatched results for instructions")

        self.instructions = translated_instructions


class Ingredient:
    def __init__(self, input_text):
        values = input_text.split(",")

        for i in range(len(values)):
            values[i] = values[i].strip()

        self.ingredient = values[0]

        if len(values) > 1:
            self.additional_info = " ".join(values[1:])
        else:
            self.additional_info = ""
