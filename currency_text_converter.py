import json
import argparse
import re
from number_parser import NumberParser
from price_parser import PriceParser


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
        

def main(text, currency_code):
    with open('currencies.json') as file:
        data = json.load(file)

    currency_data = data[currency_code]
    price_parser = PriceParser(currency_code, currency_data, text)
    price_parser.find()


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
    parser.add_argument('-c', '--currency',
                        required=True,
                        help='Name of currency you would like to convert to. This program uses the ISO 4217 standard.')

    args = parser.parse_args()
    args.currency = args.currency.upper()

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
    if args.currency not in valid_currencies:
        raise ValueError(f"{args.currency} was not found in valid_currencies.txt.")

    main(text, args.currency)