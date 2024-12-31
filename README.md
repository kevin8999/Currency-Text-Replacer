# Currency Exchange Calculator
This calculator takes in any piece of text and replaces the text inside it with the valid currency.

For example, suppose you want to convert EUR to USD and you have this piece of text:

```plain
The car costs €10 000.
```

This program will output the following:

```plain
The car costs $10,389.
```

Note that the above assumes that 1 EUR = 1.0389 USD.

`currencies.json` was obtained from https://github.com/ourworldincode/currency/. It is licensed under the MIT license.