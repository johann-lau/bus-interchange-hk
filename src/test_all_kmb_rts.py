import requests
from config import *
import json

data = requests.get(f"{KMB_ENDPOINT}/route-stop").json()["data"]
with open("kmb_all_routes.json", "x") as f:
    json.dump(
        data,
        f,
        ensure_ascii=False,
        indent=4,
    )