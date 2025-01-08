import requests
import time
from datetime import datetime, timezone, UTC
import json


class ExchangeRates:
    def __init__(self, exchange_rate_file='exchange_rates.json'):
        self.exchange_rate_file = exchange_rate_file
        self.ONE_DAY = 24 * 60 * 60
        self.last_update_time = None
        self.URL = "https://open.er-api.com/v6/latest/USD"

    def check_last_update(self):
        # Checks when exchange rates were last updated. Exchange rates update once every 24 hours, so there's no need to update more often than that.
        try:
            with open(self.exchange_rate_file, 'r') as file:
                self.content = json.load(file)
        except:
            print(f"{self.exchange_rate_file} not found.")
            self.is_outdated = True
        else:
            self.next_update_time = self.content["time_next_update_unix"]
            self.last_update_time = self.content["time_last_update_unix"]
            
            current_unix_time = datetime.now(timezone.utc).timestamp()

            self.is_outdated = current_unix_time > self.next_update_time

    def update(self):
        self.check_last_update()

        try:
            last_update_time_str = datetime.fromtimestamp(self.last_update_time, UTC).strftime("%Y-%m-%d %H:%M:%SZ")
        except:
            last_update_time_str = "Never"
    
        if self.is_outdated:
            print(f"Exchange rates are outdated. Last updated: {last_update_time_str}.")
        else:
            next_update = datetime.fromtimestamp(self.next_update_time, UTC).strftime("%Y-%m-%d %H:%M:%SZ")
            print(f"Exchange rates are up to date. Last updated: {last_update_time_str}. Next available update: {next_update}")
            return

        response = requests.get(self.URL)

        if response:
            print(f"Successfully retrieved exchange rates. Status code: {response.status_code}")
        else:
            raise Exception(f"Unable to retrieve exchange rates: Error Code {response.status_code}")

        data = response.json()

        # Write to file
        output_file = open(self.exchange_rate_file, "w")
        json.dump(data, output_file, indent=4)
        output_file.close()

if __name__ == '__main__':
    exchange_rates = ExchangeRates()
    exchange_rates.update()
