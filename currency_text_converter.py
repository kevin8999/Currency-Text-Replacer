import json
import argparse
import re
from number_parser import NumberParser
from price_parser import PriceParser
from update_exchange_rates import ExchangeRates
import subprocess
import time
from decimal import Decimal, ROUND_DOWN


class CurrencyConverter:
    def __init__(self, exchange_rate_file='exchange_rates.json'):
        self.exchange_rate_file = exchange_rate_file
        with open(self.exchange_rate_file) as file:
            data = json.load(file)

        self.exchange_rates = data["rates"]

    def convert(self, amount_from: float, currency_from: str, currency_to: str) -> float:
        currencies = [currency_from.upper(), currency_to.upper()]
        for currency in currencies:
            try:
                self.exchange_rates[currency]
            except:
                raise KeyError(f"{currency} not found in {self.exchange_rate_file}.")

        # Convert amount_from to USD
        USD_rate = self.exchange_rates[currency_from]
        USD_amount = amount_from['value']['number'] / USD_rate

        # Convert USD_amount to target currency
        amount_to = USD_amount * self.exchange_rates[currency_to]
        return amount_to


def format_number(num: str, thousands_separator=",", decimal_separator=".", uses_indian_thousands_system=False) -> str:
    """
    Format a number according to specified thousands and decimal separators,
    with an option to use the Indian numbering system.

    The Indian numbering system divides numbers into groups of two after the rightmost thousands group.

    Examples are given below.

    Raw number  Indian numbering system
    100000      1,00,000
    10000000    10,00,000

    This function takes a number as a string and formats it with the specified
    separators. It can format the number in either the Indian or standard
    thousands system.

    Parameters:
    - num (str): The number to be formatted, provided as a string.
    - thousands_separator (str): The character to use as the thousands separator (default is ",").
    - decimal_separator (str): The character to use as the decimal separator (default is ".").
    - uses_indian_thousands_system (bool): If True, formats the number using the Indian numbering system;
                                           if False, uses the standard system (default is False).

    Returns:
    - str: A string representation of the number formatted with the specified separators.

    Example:
    >>> format_number("30000000")
    '3,00,00,000'
    
    >>> format_number("1234567.89", uses_indian_thousands_system=True)
    '12,34,567.89'
    
    >>> format_number("1234567.89", thousands_separator=".", decimal_separator=",")
    '1.234.567,89'

    Raises:
    - ValueError: If the input is not a valid number string.
    """

    num_str = str(num)
    
    # Split the number into the integer and decimal parts (if any)
    if decimal_separator in num_str:
        integer_part, decimal_part = num_str.split(decimal_separator)
    else:
        integer_part = num_str
        decimal_part = ''
    
    # Reverse the integer part for easier processing
    integer_part = integer_part[::-1]
    
    # Create a list to hold the formatted parts
    formatted_parts = []
    
    # Process the last three digits (thousands)
    formatted_parts.append(integer_part[:3])
    
    # Process the remaining digits into groups of two or three
    num_thousands_places = 2 if uses_indian_thousands_system else 3
    for i in range(3, len(integer_part), num_thousands_places):
        formatted_parts.append(integer_part[i:i+num_thousands_places])
    
    # Reverse the formatted parts and join them with thousands_separator
    formatted_parts.reverse()
    formatted_number = thousands_separator.join(formatted_parts)
    
    # Add the decimal part back if it exists
    if decimal_part:
        formatted_number += decimal_separator + decimal_part
    
    return formatted_number


def main(text, currency_from, currency_to, output_file):
    with open('currencies.json') as file:
        data = json.load(file)

    # Find all prices in text that use currency_from
    print("Finding prices...")
    start = time.time()
    currency_data = data[currency_from]
    price_parser = PriceParser(currency_from, currency_data, text)
    price_parser.find()
    end = time.time()
    print("\tPrices found.")

    # Get current exchange rates
    print("Updating exchange rates...")
    update_rates_cmd = "python update_exchange_rates.py".split()
    subprocess.run(update_rates_cmd)

    # Convert currencies
    currency_converter = CurrencyConverter()
    converted_values = []
    print(f"Converting currencies from {currency_from} to {currency_to}...")
    for result in price_parser.prices:
        converted = currency_converter.convert(result, currency_from, currency_to)

        # Round based on number of decimal places in original number
        try:
            decimal_pos = result['value']['separator_positions']['decimal'][1]
            num_decimal_places = decimal_pos-1
        except:
            num_decimal_places = 0

        # Convert to price notation (with 2 decimal places)
        price = Decimal(str(converted)).quantize(Decimal(".01"), rounding=ROUND_DOWN)

        price = str(price)

        # Get decimal separator if it exists
        try:
            decimal_separator = result['value']['separator_positions']['decimal'][0]
        except:
            decimal_separator = None

        # Add thousands separators if present in original string
        thousands_separators = result['value']['separator_positions']['thousands']
        try:
            # Only one type of thousands separator is used, so grabbing only the first one will give you
            # the thousands separator for the number
            thousands_sep = thousands_separators[0][0]
        except:
            thousands_sep = ""

        price = price.split(decimal_separator)

        # If price was not split into two, it means that the result did not have a decimal separator.
        if len(price) == 1:
            # Force price to have a decimal separator and split it
            decimal_separator = "."
            price = price[0].split(decimal_separator)

        uses_indian_thousands_system = result["value"]["uses_indian_thousands_system"]
        num = float(price[0] + price[1])
        new_price = format_number(num=num, thousands_separator=thousands_sep, uses_indian_thousands_system=uses_indian_thousands_system)
        converted_values.append(new_price)

    for i, value in enumerate(converted_values):
        print(f"{price_parser.prices[i]['amount']}\t\t{value}")

    # Write to file
    print(f"Writing to changes to {output_file}...")

    """
    with open(output_file, "w") as file:
        file.write(new_text)
    """

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert text from currency A to currency B using current exchange rates.")

    # Command flags
    parser.add_argument('-t', '--text',
                        required=False,
                        help='Text that you would like to convert.')
    parser.add_argument('-f', '--file',
                        required=False,
                        help='File containing the message you would like to convert.')
    parser.add_argument('-o', '--output_file',
                        required=False,
                        default='output.txt',
                        help='Name of output file. Default: output.txt')
    parser.add_argument('-a', '--currency_from',
                        required=True,
                        help='Currency you would like to convert from. Currency must conform to ISO 4217 standard.')
    parser.add_argument('-b', '--currency_to',
                        required=True,
                        help='Currency you would like to convert to. Currency must conform to ISO 4217 standard.')

    args = parser.parse_args()
    args.currency_from = args.currency_from.upper()
    args.currency_to = args.currency_to.upper()

    # Raise error if user enters BOTH args.text and args.file or NEITHER args.text nor args.file
    if args.text != None and args.file != None:
        raise ValueError("Cannot enter text and file at the same time. Please split your command into two separate commands.")
    elif args.text == None and args.file == None:
        raise ValueError("Please enter text (-t \"sample text here\") or a file (-f file.txt) you would like to convert to.")

    # Assign text based on argument not inputted by user
    text = None
    if args.text == None:
        with open(args.file) as file:
            text = file.read()
    elif args.file == None:
        text = args.text

    # Check if currency is in valid_currencies.txt
    with open('valid_currencies.txt') as file:
        valid_currencies = file.read().splitlines() 
    if args.currency_from not in valid_currencies:
        raise ValueError(f"{args.currency_from} was not found in valid_currencies.txt.")
    if args.currency_to not in valid_currencies:
        raise ValueError(f"{args.currency_to} was not found in valid_currencies.txt.")

    if args.currency_from == args.currency_to:
        print(f"Input currency is the same as output currency. Input: {args.currency_from}. Output: {args.currency_to}.")
        print("Conversion was not performed.")
        quit()

    main(text, args.currency_from, args.currency_to, args.output_file)