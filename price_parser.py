import re
from number_parser import NumberParser
import copy

class PriceParser:
    '''
    Finds all prices associated with `currency_from` in `text`.
    '''

    def __init__(self, currency_from, currency_data, text):
        self.currency_from = currency_from
        self.text = text

        # Get name and plural name of currency
        name = currency_data["name"].replace(currency_data["demonym"], "") # Remove demonym from currency
        plural_name = name.replace(currency_data["majorSingle"], currency_data["majorPlural"])
        name = name.strip().upper()
        plural_name = plural_name.strip().upper()

        self.numbers = []
        self.THOUSANDS_SEPARATORS = [",", ".", "_", " ", "'"]
        self.DECIMAL_SEPARATORS = [",", "."]
        self.prices = {}
        self.found = {}

        # Stores indices of where the currency index occurs
        self.currency_indices = {}

        self.separator_positions = {}

        """
        `self.SYMBOL_CONDITION` states when a currency symbol can be used in English.

        It contains 3 keys:

        - placed_before: currency symbol may be placed before a quantity.
        - placed_after: currency symbol may be placed after a quantity.
        - spaces_allowed: currency symbol may have a space between it and the amount.

        NOTE: for `currency_data['symbol']` and `currency_data['symbolNative']`,
        some currencies only allow you to place a symbol before or after the amount.
        However, this common grammatical mistake will be automatically converted.
        """

        self.SYMBOL_CONDITION = {
            currency_from: {
                'placed_before': True,
                'placed_after': True,
                'spaces_allowed': "optional"
            },
            currency_data['symbol']: {
                'placed_before': True,
                'placed_after': True,
                'spaces_allowed': "optional" if len(currency_data['symbol']) > 1 else "required"
            },
            currency_data['symbolNative']: {
                'placed_before': True,
                'placed_after': True,
                'spaces_allowed': "forbidden"          
            },
            currency_data['name'].upper(): {
                'placed_before': False,
                'placed_after': True,
                'spaces_allowed': "optional"
            },
            name: {
                'placed_before': False,
                'placed_after': True,
                'spaces_allowed': "required"
            },
            plural_name: {
                'placed_before': False,
                'placed_after': True,
                'spaces_allowed': "required"
            }
        }

    def find_number(self, move_backwards: bool, symbol_index: int, condition: dict) -> str:
        """
        Finds number located next to symbol_index.

        symbol_index is the location of the currency symbol.

        Examples

        Original    Output
        "$1,000"    "1,000"
        "$10.000"   "10.000"

        This function works by identifying if the consecutive character is a digit
        or a valid thousands or decimal separator.

        - If the consecutive character is a valid separator, continue appending to number
        - If the consecutive character is NOT a valid separator, stop and return the number
        """

        i = symbol_index

        num = []
        while i < len(self.text):
            if move_backwards:
                char = self.text[i-1]
            else:
                char = self.text[i]

            try:
                int(char)
            except:
                # If the first character before the currency symbol is a space and spaces are allowed or permitted, move onto the next character
                if (condition["spaces_allowed"] == "required" or condition["spaces_allowed"] == "optional") and \
                    abs(symbol_index - i) == 0 and \
                    char == " ":
                        if move_backwards:
                            i -= 1
                        else:
                            i += 1
                        continue
                elif condition["spaces_allowed"] == "forbidden" and \
                    abs(symbol_index - i) == 0 and \
                    char == " ":
                        break
                
                if char in self.THOUSANDS_SEPARATORS:
                    # Test to see if consecutive character after thousands separator is a number
                    try:
                        next_char = self.text[i-2] if move_backwards else self.text[i+1]
                        int(next_char)
                    except:
                        break
                    else:
                        num.append(char)
                        if move_backwards:
                            i -= 1
                        else:
                            i += 1
                        continue
                else:
                    break
            else:
                num.append(char)
                if move_backwards:
                    i -= 1
                else:
                    i += 1

        if num == []:
            return None

        if move_backwards:
            # Reverse num
            num = num[::-1]

        num = ''.join(num)
        num = num.strip()
        return num

    def find(self):
        self.prices = []

        # Find each symbol in self.text
        for key in self.SYMBOL_CONDITION.keys():
            condition = self.SYMBOL_CONDITION[key]

            # If the symbol is a "$", escape it so that regex works.
            # "$" in regex matches to the end of a string/line
            if key == '$':
                symbol = r"\$"
            else:
                symbol = key

            matches = re.finditer(symbol, self.text)
            self.currency_indices[key] = [(match.start(), match.end()) for match in matches]
        
        # Find numbers next to self.currency_indices
        print(self.currency_indices)
        numbers = []

        for key in self.currency_indices.keys():
            symbol_matches = self.currency_indices[key]
            condition = self.SYMBOL_CONDITION[key]
            print(f"Key: {key}")
            for match in symbol_matches:
                '''
                TODO: if a currency symbol is next to two numbers, create a preference for numbers next to symbols with no space

                Example:

                "25 $35 bills."

                In that instance, prefer "35" over "25"
                '''

                start, end = match
                
                symbol_placed = ''
                if condition['placed_before'] == True:
                    num = self.find_number(move_backwards=True, symbol_index=start, condition=condition)
                    numbers.append({
                            'symbol': key,
                            'amount': num,
                            'symbol_placed': 'after'
                        })

                if condition['placed_after'] == True:
                    num = self.find_number(move_backwards=False, symbol_index=end, condition=condition)
                    numbers.append({
                            'symbol': key,
                            'amount': num,
                            'symbol_placed': 'before'
                        })

            for i, number in enumerate(numbers):
                if number['amount'] == None:
                    numbers.pop(i)

        self.prices = numbers

        # Convert each string in self.prices to a number
        for i, price in enumerate(self.prices):
            # TODO: fix error in loop where it loops over same dictionary key
            amount = price['amount']
            num_parser = NumberParser(amount)
            num_parser.find()
            self.prices[i]["value"] = num_parser.result
        
