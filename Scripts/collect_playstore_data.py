from google_play_scraper import reviews, Sort
import csv

APP_ID = "com.fsn.nds"

result, _ = reviews(
    APP_ID,
    lang="en",
    country="in",
    sort=Sort.NEWEST,
    count=1000
)

with open("Raw Data/nykaa_playstore.csv", "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    for review in result:
        writer.writerow([
            review["reviewId"],
            "Nykaa Fashion",
            "Google Play",
            "Review",
            f"https://play.google.com/store/apps/details?id={APP_ID}",
            review["userName"],
            review["at"],
            review["content"],
            "Nykaa Fashion Google Play reviews",
            "English"
        ])

print(f"Collected {len(result)} Nykaa Fashion reviews.")