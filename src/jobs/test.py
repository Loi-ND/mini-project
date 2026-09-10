import requests

url = "https://api.frankfurter.dev/v2/rate/USD/VND"

response = requests.get(url)
response.raise_for_status()

data = response.json()

rate = data["rate"]
print(rate)