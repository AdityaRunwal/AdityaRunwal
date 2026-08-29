import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

USERNAME = "AdityaRunwal"

url = f"https://github.com/users/{USERNAME}/contributions"

headers = {
"User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

days = []

# GitHub contribution calendar cells

for cell in soup.select("td.ContributionCalendar-day"):
    date = cell.get("data-date")
    level = cell.get("data-level")

    if date and level is not None:
        days.append({
            "date": date,
            "level": int(level)
        })


data = {
"username": USERNAME,
"updated_at": datetime.now().isoformat(),
"days": days
}

with open("data/contributions.json", "w", encoding="utf-8") as file:
    json.dump(data, file, indent=2)

print(f"Fetched {len(days)} contribution days successfully!")
