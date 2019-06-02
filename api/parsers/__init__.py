import re

NUMBER_MAP = {
    "one": 1,
    "uno": 1,
    "two": 2,
    "deuce": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "elevent": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20}


class Parser():

    def parse_number(self, text):
        """Parses out the first number from the given text"""
        return self.parse_numbers(text)[0]

    def parse_numbers(self, text):
        """Parses all the numbers from the given text"""
        numbers = []
        if type(text) is str:
            tokens = self.get_tokens(text)
            for token in tokens:
                try:
                    number = NUMBER_MAP.get(token, int(token))
                    break
                except ValueError:
                    pass
        else:
            try:
                numbers.append(int(text))
            except ValueError:
                pass
        return number

    def get_tokens(self, text):
        """Returns a list of tokens"""
        text.replace(" ", "\s").lower()
        return re.split(r';|,\s', text)


def parse_number(text):
    """Returns the first number in the text"""
    Parser().parse_number(text)
