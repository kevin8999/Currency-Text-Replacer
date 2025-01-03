import json
import argparse
import re
#import requests

def find_pattern(text, pattern):
    # Returns all instances of `pattern` in `text`
    regex = rf"{pattern}"
    finder = re.compile(regex)
    matches = finder.findall(text)
    print(matches)
    return matches

def find_currency_symbol(text, symbol, condition):
    # Look for symbol in text

    """
    Matches currency symbol with numbers

    Examples:

    - $1,000.00
    - 234.000.000,00 USD
    - USD 10000.00
    """

    # Stores indices of where the currency index occurs
    currency_indices = []
    matches = re.finditer(symbol, text)
    currency_indices = [(match.start(), match.end()) for match in matches]
    print(currency_indices)

    quit()

    # Find numbers next to currency_indices
    for start, end in currency_indices:
        if condition['placed_before'] == True:
            i = start
            while True:
                char = text[i-1]
                try:
                    int(char)
                except:
                    # If the first character before the currency symbol is a space and spaces are allowed or permitted, move onto the next character
                    if (condition["spaces_allowed"] == "required" or condition["spaces_allowed"] == "optional") and \
                        i == start-1 and \
                        char == " ":
                            i -= 1
                            continue
                    elif condition["spaces_allowed"] == "forbidden" and \
                        i == start-1 and \
                        char == " ":
                            break

                    # If the character is a valid thousands separator, move onto the next character
                    if char == "," or char == "." or char == " ":
                        i -= 1
                        continue

                    break
                else:
                    i -= 1

        if condition['placed_after'] == True:
            pass

        try:
            float(word)
        except:
            continue

        decimal_separator = None
        if "," in word or "." in word:
            # Determine if "," or "." occurs last to find decimal separator

            # Get all indexes of commas and periods and find the index where each occurs
            commas = [index for index, char in enumerate(text) if char == ","]
            periods = [index for index, char in enumerate(text) if char == "."]
            last_comma = max(commas)
            last_period = max(periods)
            
            if last_comma > last_period: decimal_separator = ","
            elif last_period > last_comma: decimal_separator = "."
        else:
            number = int(word)

def convert_currency(amount, currency_from, currency_to):
    if currency_from == currency_to:
        return original_amount

    # Call API for conversion

def main(text, currency_code):
    with open('currencies.json') as file:
        data = json.load(file)

    currency_data = data[currency_code]

    # Generate all possible currency symbols
    name = currency_data["name"].replace(currency_data["demonym"], "") # Remove demonym from currency
    plural_name = name.replace(currency_data["majorSingle"], currency_data["majorPlural"])
    name = name.strip().upper()
    plural_name = plural_name.strip().upper()

    """
    `symbol_condition` states when a currency symbol can be used in English.

    It contains 3 keys:

    - placed_before: currency symbol may be placed before a quantity.
    - placed_after: currency symbol may be placed after a quantity.
    - spaces_allowed: currency symbol may have a space between it and the amount.

    NOTE: for `currency_data['symbol']` and `currency_data['symbolNative']`,
    some currencies only allow you to place a symbol before or after the amount.
    However, this common grammatical mistake will be automatically converted.
    """

    symbol_condition = {
        currency_code: {
            'placed_before': True,
            'placed_after': True,
            'spaces_allowed': "optional"
        },
        currency_data['symbol']: {
            'placed_before': True,
            'placed_after': True,
            'spaces_allowed': "required"
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

    results = {}

    for key in symbol_condition.keys():
        if key == '$':
            # If the symbol is a "$", escape it so that regex works
            results[key] = find_currency_symbol(text, r"\$", symbol_condition[key]) 
        else:
            results[key] = find_currency_symbol(text, key, symbol_condition[key])
    from pprint import pprint
    pprint(results)


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