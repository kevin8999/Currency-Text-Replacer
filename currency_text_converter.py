import json
import argparse
import re
from number_parser import NumberParser
from price_parser import PriceParser
from update_exchange_rates import ExchangeRates
import subprocess


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
        USD_amount = amount_from / self.exchange_rates[currency_from]

        # Convert USD_amount to target currency
        amount_to = USD_amount * self.exchange_rates[currency_to]
        return amount_to
        

def main(text, currency_from, currency_to):
    with open('currencies.json') as file:
        data = json.load(file)

    # Find all prices in text that use currency_from
    currency_data = data[currency_from]
    price_parser = PriceParser(currency_from, currency_data, text)
    price_parser.find()
    print(price_parser.results)

    # Get current exchange rates
    print("Updating exchange rates...")
    update_rates_cmd = "python update_exchange_rates.py".split()
    subprocess.run(update_rates_cmd)

    # Convert currencies
    currency_converter = CurrencyConverter()
    converted_values = {}
    for key in price_parser.results:
        converted_values[key] = []
        for i, result in enumerate(price_parser.results[key]):
            converted = currency_converter.convert(result, currency_from, currency_to)

            # Round based on number of decimal places in original number
            try:
                num = price_parser.separator_positions[key][i]['number']
                num_decimal_places = len(num)-1 - price_parser.separator_positions[key][i]['decimal_sep_pos'][1]
            except:
                num_decimal_places = 0

            rounded = round(converted, num_decimal_places)
            converted_values[key].append(rounded)

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

    main(text, args.currency_from, args.currency_to)