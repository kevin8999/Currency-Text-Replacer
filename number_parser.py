class NumberParser:
    """
    Parses numbers in string format and converts them to integer.

    For example, the following strings are converted to floats

    Original Number     Float
    "1,234,567"         1234567.0
    "1 234 567.89"      1234567.89

    Access the float using self.number and the original number using self.string

    Access decimal separator and thousand separator positions using self.decimal_separator_pos and self.thousand_separator_pos
    """
    def __init__(self, number) -> None:
        # self.string will be converted to self.number in NumberParser
        self.value = None
        self.string = number
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

    def find(self, use_thousands_separator_for_single_unique_separator=True):
        '''
        Finds self.number in self.string.

        If a number contains only one unique separator, it is not known if the separator represents
        a thousands separator or a decimal separator.

        `use_thousands_separator_for_single_unique_separator` determines if NumberParser.find()
        should assume that unique separator is a *thousands* separator or not.

        Example if `use_thousands_separator_for_single_unique_separator = False`

        Original    New
        "3,125"     3.125
        "10,000"    10.0
        "3.141"     3.141

        Example if `use_thousands_separator_for_single_unique_separator = True`

        Original    New
        "3,125"     3125.0
        "10,000"    10000.0
        "3.141"     3141.0

        By default, use_thousands_separator_for_single_unique_separator is True.
        '''

        # Find separators and check if digit is a valid digit
        separators_found = []
        for digit in self.string:
            if digit in self.SEPARATORS:
                separators_found.append(digit)
                continue
            elif digit not in self.VALID_DIGITS:
                raise ValueError(f"{digit} is not a number.")

        unique_separators = len(set(separators_found))

        if unique_separators == 0:
            self.number = float(self.string)
        elif unique_separators == 1:
            '''
            IMPORTANT: if the number of separators found is 1, it is not known if the separator is for thousands or decimals.
            
            If there is only one unique separator, use_thousands_separator_for_single_unique_separator determines if the unique
            separator is a thousands separator or a decimal separator.
            '''

            if (self.string[-4] in self.SEPARATORS or len(separators_found) > 1) and use_thousands_separator_for_single_unique_separator:
                # Assumes that the separator is a thousands separator
                thousands_separator = self.string[-4]
                self.thousands_separator_pos = [(digit, i) for i, digit in enumerate(self.string) if digit in self.SEPARATORS]
                self.number = self.string.replace(thousands_separator, "")
                self.number = float(self.number)
            else:
                decimal_separator = separators_found[-1]
                self.decimal_separator_pos = (decimal_separator, self.string.find(decimal_separator))
                whole_number, decimal = self.string.split(decimal_separator)
                self.num_decimal_places = len(decimal)
                self.number = float(whole_number + "." + decimal)

        elif unique_separators == 2:
            decimal_separator = separators_found[-1]
            thousands_separator = separators_found[0]

            # Find position of decimal and thousands separator
            self.decimal_separator_pos = (decimal_separator, self.string.find(decimal_separator))
            self.thousands_separator_pos = [(thousands_separator, i) for i, digit in enumerate(self.string) if digit == thousands_separator]

            if decimal_separator in self.DECIMAL_SEPARATORS:
                whole_number, decimal = self.string.split(decimal_separator)

                whole_number = whole_number.replace(thousands_separator, "")

                # Combine whole_number and decimal separated by "." to turn into float
                self.number = whole_number + "." + decimal
                self.number = float(self.number)
                self.num_decimal_places = len(decimal)
            else:
                raise ValueError(f"{decimal_separator} is not a valid decimal separator.")

        elif unique_separators > 2:
            raise ValueError(f"Found more than 2 separators. {self.string} must have 2 or fewer unique separators. Separators found: {separators_found}")

        # Check if number_str uses the Indian numbering system
        if unique_separators >= 1 and isinstance(self.thousands_separator_pos, list):
            thousands = self.string.split(thousands_separator)

            # Test all thousands groups in middle to see if number uses Indian thousands system
            for group in thousands[1:-1]:
                if len(group) == 2:
                    self.uses_indian_thousands_sys = True
                    break

    @property
    def result(self) -> dict:
        return {
            'number': self.number,
            'string': self.string,
            'separator_positions': {
                'decimal': self.decimal_separator_pos,
                'thousands': self.thousands_separator_pos
            },
            'uses_indian_thousands_system': self.uses_indian_thousands_sys
        }