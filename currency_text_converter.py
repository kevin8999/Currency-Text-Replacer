import json
import argparse

def find_currency(text, symbol):
    pass

def convert(amount, currency_from, currency_to):
    if currency_from == currency_to:
        return original_amount

    # Call API for conversion

def main(text, currency_code):
    with open('currencies.json') as file:
        data = json.load(file)

    # Find currency symbols in text
    currency_data = data[currency_code]

    # Generate all possible currency symbols
    name = currency_data["name"].replace(currency_data["demonym"], "") # Remove demonym from currency
    plural_name = name.replace(currency_data["majorSingle"], currency_data["majorPlural"])
    name = name.strip().upper()
    plural_name = plural_name.strip().upper()

    """
    `currency_symbols` states when a currency symbol can be used in English.

    It contains 3 keys:

    - placed_before: currency symbol may be placed before a quantity.
    - placed_after: currency symbol may be placed after a quantity.
    - spaces_allowed: currency symbol may have a space between it and the amount.

    The `spaces_allowed` key, contains values that state when spaces are used for currency symbols in English.

    - 0: spaces are forbidden. They must NOT be used.
    - 1: spaces are required. They MUST be used.
    - 2: spaces are optional. They may or may not be used.

    NOTE: for `currency_data['symbol']` and `currency_data['symbolNative']`,
    some currencies only allow you to place a symbol before or after the amount.
    However, this common grammatical mistake will be automatically converted.
    """

    currency_symbols = {
        currency_code: {
            'placed_before': True,
            'placed_after': True,
            'spaces_allowed': 1
        },
        currency_data['symbol']: {
            'placed_before': True,
            'placed_after': True,
            'spaces_allowed': 1
        },
        currency_data['symbolNative']: {
            'placed_before': True,
            'placed_after': True,
            'spaces_allowed': 0            
        },
        currency_data['name'].upper(): {
            'placed_before': False,
            'placed_after': True,
            'spaces_allowed': 2
        },
        name: {
            'placed_before': False,
            'placed_after': True,
            'spaces_allowed': 0
        },
        plural_name: {
            'placed_before': False,
            'placed_after': True,
            'spaces_allowed': 0
        }
    }    


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

    # Check if user enters BOTH args.text and args.file or NEITHER args.text nor args.file
    if args.text != None and args.file != None:
        raise ValueError("Cannot enter text and file at the same time. Please split your command into two separate commands.")
    elif args.text == None and args.file == None:
        raise ValueError("Please enter text or a file you would like to convert to.")

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