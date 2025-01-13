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

        # Convert to price notation (with 2 decimal places), unless num_decimal_places equals 0
        price = Decimal(str(converted)).quantize(Decimal(".01"), rounding=ROUND_DOWN)

        price = str(price)

        # Add thousands separators if present in original string
        thousands_separators = result['value']['separator_positions']['thousands']
        try:
            sep_pos = [pos for (symbol, pos) in thousands_separators]
            # Only one type of thousands separator is used, so grabbing only the first one will give you
            # the thousands separator for the number
            sep_symbol = thousands_separators[0][0]
            decimal_separator = result['value']['separator_positions']['decimal'][0]
        except TypeError:
            # Raises error if decimal_separator = None
            decimal_separator = None
        except:
            pass
        else:
            # Split price at decimal separator if it exists
            price = price.split(decimal_separator)
            whole_num = list(price[0])

            # Number of digits per thousands group
            digits_in_thousands_group = None
            if result['value']['uses_indian_thousands_system']:
                # Add 1 to account for list index
                digits_in_thousands_group = 2

                # Insert first thousands separator
                whole_num.insert(-3, sep_symbol)

                # Insert all other thousands separators
                i = len(whole_num) - 6
                while i > 0:
                    whole_num.insert(i, sep_symbol)
                    i -= digits_in_thousands_group
            else:
                # Add 1 to account for list index
                digits_in_thousands_group = 3 + 1

                # Insert first thousands separator
                # If length % 3 = 0, set it to 3 because numbers do not begin with a thousands separator
                first_thous_pos = 3 if len(whole_num) % 3 == 0 else len(whole_num) % 3
                whole_num.insert(first_thous_pos, sep_symbol)

                # Insert all other thousands separators
                i = first_thous_pos + digits_in_thousands_group
                while i < len(whole_num):
                    whole_num.insert(i, sep_symbol)
                    i += digits_in_thousands_group
                
            whole_num = ''.join(whole_num)
            price[0] = whole_num

            price = f'{decimal_separator}'.join(price)

        converted_values.append(price)
    
    print(f"\tPrices converted to {currency_to}.")
    
    print("Original\tNew")
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