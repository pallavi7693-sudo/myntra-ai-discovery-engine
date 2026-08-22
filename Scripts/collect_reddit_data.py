import os
import sys
import csv
import time
import json
import urllib.request
import urllib.parse
from datetime import datetime

# Optional PRAW import
try:
    import praw
except ImportError:
    praw = None

# Search themes requested for Myntra & fashion-shopping behavior
SEARCH_THEMES = [
    "Myntra wishlist",
    "Myntra saved items",
    "Myntra waiting to buy",
    "Myntra price",
    "Myntra sale",
    "Myntra reviews",
    "Myntra fit",
    "Myntra size",
    "Myntra quality",
    "Myntra comparison",
    "Myntra alternatives",
    "Myntra out of stock",
    "Myntra purchase"
]

def fetch_via_public_json(theme, collected_ids):
    """
    Fetches public Reddit search data using Reddit's public .json endpoints.
    Strictly respects public access, rate limits, and standard headers.
    """
    records = []
    encoded_query = urllib.parse.quote(theme)
    url = f"https://www.reddit.com/search.json?q={encoded_query}&limit=50&sort=relevance"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MyntraProductDiscovery/1.0"
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                children = data.get("data", {}).get("children", [])
                
                for item in children:
                    post_data = item.get("data", {})
                    post_id = post_data.get("id")
                    
                    if post_id and post_id not in collected_ids:
                        collected_ids.add(post_id)
                        
                        created_utc = post_data.get("created_utc", 0)
                        created_date = datetime.fromtimestamp(created_utc).strftime('%Y-%m-%d %H:%M:%S') if created_utc else ""
                        permalink = post_data.get("permalink", "")
                        
                        records.append({
                            "id": f"post_{post_id}",
                            "source": "Reddit",
                            "subreddit": post_data.get("subreddit", ""),
                            "post_title": post_data.get("title", ""),
                            "text": post_data.get("selftext", ""),
                            "url": f"https://www.reddit.com{permalink}" if permalink else "",
                            "date": created_date,
                            "type": "post"
                        })
    except Exception as e:
        print(f"[!] Warning: Public fetch failed for theme '{theme}': {e}")
        
    return records

def fetch_via_praw(reddit, theme, collected_ids):
    """
    Fetches public Reddit data using official PRAW API credentials.
    """
    records = []
    try:
        search_results = reddit.subreddit("all").search(query=theme, limit=50)
        for submission in search_results:
            if submission.id not in collected_ids:
                collected_ids.add(submission.id)
                created_date = datetime.fromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S')
                
                records.append({
                    "id": f"post_{submission.id}",
                    "source": "Reddit",
                    "subreddit": submission.subreddit.display_name,
                    "post_title": submission.title,
                    "text": submission.selftext if submission.selftext else "",
                    "url": f"https://www.reddit.com{submission.permalink}",
                    "date": created_date,
                    "type": "post"
                })
            
            # Fetch top comments
            try:
                submission.comments.replace_more(limit=0)
                for comment in submission.comments[:10]:
                    if comment.id not in collected_ids:
                        collected_ids.add(comment.id)
                        comment_date = datetime.fromtimestamp(comment.created_utc).strftime('%Y-%m-%d %H:%M:%S')
                        
                        records.append({
                            "id": f"comment_{comment.id}",
                            "source": "Reddit",
                            "subreddit": comment.subreddit.display_name,
                            "post_title": submission.title,
                            "text": comment.body,
                            "url": f"https://www.reddit.com{comment.permalink}",
                            "date": comment_date,
                            "type": "comment"
                        })
            except Exception:
                pass
    except Exception as e:
        print(f"[!] Error retrieving PRAW data for '{theme}': {e}")
        
    return records

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

def main():
    load_env_file()
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT", "MyntraProductDiscovery/1.0")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    output_dir = os.path.join(project_root, "Raw Data")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "reddit_myntra_raw.csv")

    collected_ids = set()
    records = []

    use_praw = False
    if client_id and client_secret and praw is not None:
        print("[*] Initializing collector using official Reddit API credentials...")
        try:
            reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent
            )
            use_praw = True
        except Exception as e:
            print(f"[!] Failed to initialize PRAW: {e}. Falling back to public JSON mode.")

    if not use_praw:
        print("\n=======================================================")
        print("[*] Running in Public Access Mode (No API keys required)")
        print("[*] Rate limiting is active to strictly respect Reddit servers.")
        print("=======================================================\n")

    for theme in SEARCH_THEMES:
        print(f"[*] Searching Reddit for theme: '{theme}'...")
        if use_praw:
            theme_records = fetch_via_praw(reddit, theme, collected_ids)
        else:
            theme_records = fetch_via_public_json(theme, collected_ids)
            time.sleep(2)  # Pause 2 seconds between requests to strictly respect rate limits

        records.extend(theme_records)

    # Save to Raw Data/reddit_myntra_raw.csv
    fieldnames = ["id", "source", "subreddit", "post_title", "text", "url", "date", "type"]
    with open(output_file, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"\n[✓] Data collection complete! Total unique records collected: {len(records)}")
    print(f"[✓] Raw dataset saved to: {output_file}")

if __name__ == "__main__":
    main()
