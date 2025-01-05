import re

class PriceParser:
    def __init__(self, currency_code, currency_data, text):
        self.currency_code = currency_code
        self.currency_data = currency_data

        # Get name and plural name of currency
        name = currency_data["name"].replace(currency_data["demonym"], "") # Remove demonym from currency
        plural_name = name.replace(currency_data["majorSingle"], currency_data["majorPlural"])
        name = name.strip().upper()
        plural_name = plural_name.strip().upper()

        self.numbers = []
        self.text = text
        self.THOUSANDS_SEPARATORS = [",", ".", "_", " ", "'"]
        self.DECIMAL_SEPARATORS = [",", "."]

        """
        self.num_strings saves the position of each decimal separator and thousands separator for a number.

        For example, the number "1,234,567.89" would be stored as:

        {
            "123456789": {
                "decimal_separators": (".", 9),
                "thousands_separators": [(",", 1), (",", 5)]
            }
        }
        """
        self.separator_positions = {}

        """
        `self.symbol_condition` states when a currency symbol can be used in English.

        It contains 3 keys:

        - placed_before: currency symbol may be placed before a quantity.
        - placed_after: currency symbol may be placed after a quantity.
        - spaces_allowed: currency symbol may have a space between it and the amount.

        NOTE: for `currency_data['symbol']` and `currency_data['symbolNative']`,
        some currencies only allow you to place a symbol before or after the amount.
        However, this common grammatical mistake will be automatically converted.
        """

        self.symbol_condition = {
            currency_code: {
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

    def find_number(self, move_backwards: bool, symbol_index: int, condition: dict):
        # Finds number next to symbol_index
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

        if move_backwards:
            # Reverse num
            num = num[::-1]

        num = ''.join(num)
        num = num.strip()
        return num

    def find_currency_symbol(self, symbol, condition):
        """
        Matches currency symbol with numbers

        Examples:

        - $1,000.00. Finds '1000.00'
        - 234.000.000,20 USD. Finds '234,000,000,20'
        - USD 10000.00. Finds '10000.00'
        """

        # Stores indices of where the currency index occurs
        currency_indices = []
        matches = re.finditer(symbol, self.text)
        currency_indices = [(match.start(), match.end()) for match in matches]

        # Find numbers next to currency_indices
        numbers = []
        for start, end in currency_indices:
            if condition['placed_before'] == True:
                num = self.find_number(move_backwards=True, symbol_index=start, condition=condition)
                numbers.append(num)

            if condition['placed_after'] == True:
                num = self.find_number(move_backwards=False, symbol_index=end, condition=condition)
                numbers.append(num)

        numbers = [num for num in numbers if num != ''] # Remove whitespaces in list
        return numbers

    def find(self):
        self.results = {}
        for key in self.symbol_condition.keys():
            if key == '$':
                # If the symbol is a "$", escape it so that regex works
                self.results[key] = self.find_currency_symbol(r"\$", self.symbol_condition[key]) 
            else:
                self.results[key] = self.find_currency_symbol(key, self.symbol_condition[key])
        
        # Convert each string in self.results to a number
        for key in self.results.keys():
            for i, result in enumerate(self.results[key]):
                num_parser = NumberParser()
                num_parser.find(result)
                self.results[key][i] = num_parser.number

                # Store position of decimal and thousands separators
                self.separator_positions[num_parser.number_str] = {
                    'decimal_separator': num_parser.decimal_separator_pos,
                    'thousands_separator': num_parser.thousands_separator_pos
                }

        from pprint import pprint
        pprint(self.results)
        pprint(self.separator_positions)