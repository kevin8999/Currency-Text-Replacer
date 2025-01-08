class NumberParser:
    def __init__(self) -> None:
        """
        Finds numbers in string format and converts them to integer.

        Numbers that can be parsed include:

        - 1,234,567.89
        - 1.234.567,89
        - 1 234 567,89

        Access the final number using self.number.

        Access decimal separator and thousand separator positions using self.decimal_separator_pos and self.thousand_separator_pos
        """

        # self.number_str will be converted to self.number in NumberParser
        self.number = None

        # Create list of strings from 0 to 9
        self.VALID_DIGITS = [str(i) for i in range(10)]

        self.decimal_separator_pos = None
        self.thousands_separator_pos = None
        self.SEPARATORS = [",", ".", "_", " ", "'"]
        self.DECIMAL_SEPARATORS = [",", "."]

        '''
        The Indian numbering system groups the first three digits to the left of the decimal point.
        However, groups thereafter use two digits as separators.
        See https://en.wikipedia.org/wiki/Indian_numbering_system for more information.
        '''
        self.uses_indian_thousands_sys = False

    def find(self, number, use_thousands_separator_for_single_unique_separator=True):
        self.number_str = number

        # Find separators and check if digit is a valid digit
        separators_found = []
        for digit in self.number_str:
            if digit in self.SEPARATORS:
                separators_found.append(digit)
                continue
            if digit not in self.VALID_DIGITS:
                raise ValueError(f"{digit} is not a number.")

        unique_separators = len(set(separators_found))

        if unique_separators == 0:
            self.number = float(self.number_str)
        elif unique_separators == 1:
            '''
            IMPORTANT: if the number of separators found is 1, it is not known if the separator is for thousands or decimals
            '''

            # Check if 3rd to last digit is a thousands separator
            if (self.number_str[-4] in self.SEPARATORS or len(separators_found) > 1) and use_thousands_separator_for_single_unique_separator:
                thousands_separator = self.number_str[-4]
                self.thousands_separator_pos = [(digit, i) for i, digit in enumerate(self.number_str) if digit in self.SEPARATORS]
                self.number = self.number_str.replace(thousands_separator, "")
                self.number = float(self.number)
            else:
                decimal_separator = separators_found[-1]
                self.decimal_separator_pos = (decimal_separator, self.number_str.find(decimal_separator))
                whole_number, decimal = self.number_str.split(decimal_separator)
                self.num_decimal_places = len(decimal)
                self.number = float(whole_number + "." + decimal)

        elif unique_separators == 2:
            decimal_separator = separators_found[-1]
            thousands_separator = separators_found[0]

            # Find position of decimal and thousands separator
            self.decimal_separator_pos = (decimal_separator, self.number_str.find(decimal_separator))
            self.thousands_separator_pos = [(thousands_separator, i) for i, digit in enumerate(self.number_str) if digit == thousands_separator]

            if decimal_separator in self.DECIMAL_SEPARATORS:
                whole_number, decimal = self.number_str.split(decimal_separator)

                whole_number = whole_number.replace(thousands_separator, "")

                # Combine whole_number and decimal separated by "." to turn into float
                self.number = whole_number + "." + decimal
                self.number = float(self.number)
                self.num_decimal_places = len(decimal)
            else:
                raise ValueError(f"{decimal_separator} is not a valid decimal separator.")

        elif unique_separators > 2:
            raise ValueError(f"Found more than 2 separators. {self.number_str} must have 2 or fewer unique separators. Separators found: {separators_found}")

        # Check if number_str uses the Indian numbering system
        if unique_separators >= 1 and isinstance(self.thousands_separator_pos, list):
            thousands = self.number_str.split(thousands_separator)

            # Test all thousands groups in middle to see if number uses Indian thousands system
            for group in thousands[1:-1]:
                if len(group) == 2:
                    self.uses_indian_thousands_sys = True
                    break

    @property
    def results(self) -> dict:
        return {
            'number_str': self.number_str,
            'number': self.number,
            'separator_positions': {
                'decimal': self.decimal_separator_pos,
                'thousands': self.thousands_separator_pos
            }
        }