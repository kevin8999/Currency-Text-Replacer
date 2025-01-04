"""
Finds numbers in string format and converts them to integer.

Numbers that can be parsed include:

- 1,234,567.89
- 1.234.567,89
- 1 234 567,89

Access the final number using self.number.

Access decimal separator and thousand separator positions using self.decimal_separator_pos and self.thousand_separator_pos
"""

class NumberParser:
    def __init__(self, number: str) -> None:
        # self.number_str will be converted to self.number in NumberParser
        self.number_str = number
        self.number = None

        # Create list of strings from 0 to 9
        self.VALID_DIGITS = [str(i) for i in range(10)]

        self.decimal_separator_pos = -1
        self.thousands_separator_pos = []
        self.SEPARATORS = [",", ".", "_", " ", "'"]
        self.DECIMAL_SEPARATORS = [",", "."]

    def find(self):
        separators_found = []

        # Find separators and check if digit is a valid digit
        for digit in self.number_str:
            if digit in self.SEPARATORS:
                separators_found.append(digit)
                continue
            if digit not in self.VALID_DIGITS:
                raise ValueError(f"{digit} is not a number.")

        num_separators_found = len(set(separators_found))

        if num_separators_found == 1:
            thousands_separator = separators_found[0]
            self.number = self.number_str.replace(thousands_separator, "")
            self.number = float(self.number)
        elif num_separators_found == 2:
            decimal_separator = separators_found[-1]
            thousands_separator = separators_found[0]

            # Find position of decimal and thousands separator
            self.decimal_separator_pos = self.number_str.find(decimal_separator)
            self.thousands_separator_pos = [(thousands_separator, i) for i, digit in enumerate(self.number_str) if digit == thousands_separator]

            if decimal_separator in self.DECIMAL_SEPARATORS:
                whole_number, decimal = self.number_str.split(decimal_separator)

                whole_number = whole_number.replace(thousands_separator, "")

                # Combine whole_number and decimal separated by "." to turn into float
                self.number = whole_number + "." + decimal
                self.number = float(self.number)
            else:
                raise ValueError(f"{decimal_separator} is not a valid decimal separator.")

        elif num_separators_found > 2:
            raise ValueError(f"Found more than 2 separators. {self.number_str} must have 2 or fewer unique separators. Separators found: {separators_found}")
