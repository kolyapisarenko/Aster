import pandas as pd
import requests
from pathlib import Path

URL = "https://en.wikipedia.org/wiki/List_of_circulating_currencies"
SAVE_PATH = Path("./data")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

response = requests.get(URL, headers=headers)

tables = pd.read_html(response.text, attrs={"class": "wikitable"})

df = tables[0]

df = df[df.columns[2:4]]

SAVE_PATH.mkdir(parents=True, exist_ok=True)

df.to_csv(SAVE_PATH / "currency.csv")