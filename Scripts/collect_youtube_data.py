import os
import sys
import csv
from googleapiclient.discovery import build

# Helper function to load .env file automatically
def load_env_file():
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, val = line.split("=", 1)
                        os.environ[key.strip()] = val.strip().strip('"').strip("'")

# Load environment variables from .env
load_env_file()

API_KEY = os.getenv("YOUTUBE_API_KEY")

if not API_KEY:
    print("[!] ERROR: YOUTUBE_API_KEY not found in environment variables or .env file.")
    print("Please add YOUTUBE_API_KEY=your_key to your .env file.")
    sys.exit(1)

youtube = build("youtube", "v3", developerKey=API_KEY)

# YouTube videos to collect comments from
VIDEO_IDS = [
    "-_V7b-F2vFc",
    "k__Yf85C7M4",
    "QNBzPrsD65s",
    "Ua4_P2eZrTU",
    "owLbOEl5_bo",
]
all_comments = []

for video_id in VIDEO_IDS:
    print(f"\nCollecting comments from video: {video_id}")

    response = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=100,
        textFormat="plainText"
    ).execute()

    items = response.get("items", [])

    for item in items:
        comment = item["snippet"]["topLevelComment"]["snippet"]

        all_comments.append([
            comment.get("textDisplay", ""),
            comment.get("authorDisplayName", ""),
            comment.get("publishedAt", ""),
            comment.get("likeCount", 0),
            video_id
        ])

    print(f"Collected {len(items)} comments from {video_id}")

# Save all collected comments
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
output_dir = os.path.join(project_root, "Raw Data")

os.makedirs(output_dir, exist_ok=True)

output_file = os.path.join(output_dir, "youtube_comments_real.csv")

with open(output_file, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    writer.writerow([
        "comment",
        "author",
        "published_at",
        "like_count",
        "video_id"
    ])

    writer.writerows(all_comments)

print("\n===================================")
print(f"Total comments collected: {len(all_comments)}")
print(f"Saved to: {output_file}")
print("===================================")