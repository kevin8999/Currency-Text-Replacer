# Currency Exchange Calculator
This calculator takes in any piece of text and replaces the text inside it with the valid currency.

For example, suppose you want to convert EUR to USD, and you have this piece of text:

```plain
The car costs €10 000.
```

This program will output the following:

```plain
The car costs $10 389.
```

Note that the above assumes that 1 EUR = 1.0389 USD.

`currencies.json` was obtained from https://github.com/ourworldincode/currency/. It is licensed under the MIT license.

## Setup
To set up this repository, open up a command prompt. Then, complete the steps below.

First, download this repository.

```shell
git clone https://github.com/kevin8999/Currency-Exchange-Calculator
```

Second, change into the project's directory.

```shell
cd Currency-Exchange-Calculator/
```

You can now use the program. For instructions on how to use this program, please see [Usage](#usage).

## Usage
An overview of the program is given below.

```plain
Convert text from currency A to currency B using current exchange rates.

options:
  -h, --help            show this help message and exit
  -t TEXT, --text TEXT  Text that you would like to convert.
  -f FILE, --file FILE  File containing the message you would like to convert.
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        Name of output file. Default: output.txt
  -a CURRENCY_FROM, --currency_from CURRENCY_FROM
                        Currency you would like to convert from. Currency must conform to ISO 4217 standard.
  -b CURRENCY_TO, --currency_to CURRENCY_TO
                        Currency you would like to convert to. Currency must conform to ISO 4217 standard.
```

### Example Usage
To convert from USD to CAD using `message.txt` as your message, use the following command.

```shell
python currency_text_converter.py -a USD -b CAD -f message.txt
```

To convert from USD to CAD by passing in a string, use the following command.

```shell
python currency_text_converter.py -a USD -b CAD -t "Example_text_here"
```

## Important Notes
For information about supported currencies, please see https://www.exchangerate-api.com/docs/supported-currencies.

Additionally, this program will break if run on text such as the following:

```plain
25 USD 15
3 $5
```

This is because the program is unsure if the currency symbol belongs to the number before it or the number after it.