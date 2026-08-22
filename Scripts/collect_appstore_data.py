import requests
import csv

APP_ID = "1022363908"

url = f"https://itunes.apple.com/in/rss/customerreviews/id={APP_ID}/sortBy=mostRecent/json"

response = requests.get(url)
data = response.json()

entries = data.get("feed", {}).get("entry", [])

with open("Raw Data/nykaa_appstore.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    for review in entries:
        writer.writerow([
            review.get("id", {}).get("label", ""),
            "Nykaa",
            "App Store",
            f"https://apps.apple.com/in/app/nykaa-makeup-beauty-shopping/id={APP_ID}",
            review.get("author", {}).get("name", {}).get("label", ""),
            review.get("updated", {}).get("label", ""),
            review.get("content", {}).get("label", ""),
            "Nykaa App Store reviews",
            "English"
        ])

print(f"Collected {len(entries)} Nykaa App Store reviews.")