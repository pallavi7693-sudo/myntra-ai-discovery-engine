import os
import csv
from collections import Counter

# Priority order: price_drop > sale > wishlist > purchase_intent > availability > delivery > product_link
INTENT_CATEGORIES = [
    (
      "price_drop",
[
    "price drop", "price down", "price reduced", "price decrease",
    "cheaper", "lower price", "reduce price", "waiting for price",
    "when will the price drop", "price kab kam", "price kam",
    "price will go down", "will the price go down",
    "when will price decrease", "when will price reduce",
    "wait for discount", "wait for sale",
    "cheaper during sale", "will it get cheaper",
    "price too high", "too expensive", "expensive",
    "worth the price", "price is high"
]
    ),
    (
        "sale",
[
    "sale", "discount", "offer", "deal", "coupon", "promo",
    "sale price", "sale kab", "discount kab",
    "when is the sale", "when will the sale",
    "sale when", "next sale", "upcoming sale",
    "any sale", "any discount", "any offer",
    "big sale", "mega sale", "sale season",
    "discount available", "discount please",
    "offer available", "offer please",
    "coupon code", "promo code"
]
    ),
    (
    "wishlist",
    [
        "wishlist", "wish list", "wishlisted", "saved",
        "save this", "save this item", "want this", "i want this",
        "want it", "i need this", "need this", "need it", "i want it",
        "i need it", "add to wishlist", "adding this", "add this",
        "added to wishlist", "keeping this in wishlist",
        "keeping this", "ill save this", "will save this",
        "love this", "must have", "have to buy",
        "gonna buy", "going to buy"
    ]
),
    (
        "purchase_intent",
        [
            "buy", "buying", "purchase", "purchased", "ordered",
            "order", "will buy", "where can i buy"
        ]
    ),
    (
        "availability",
        [
            "available", "availability", "out of stock", "restock",
            "restock please", "when will it be available"
        ]
    ),
    (
        "delivery",
        [
            "delivery", "delivered", "shipping", "delayed",
            "cancelled", "cancellation"
        ]
    ),
    (
        "product_link",
        [
            "link", "product link", "send link", "share link",
            "link please", "where is the link", "link of this"
        ]
    )
]

def classify_intent(comment_text):
    """
    Classifies comment text into a primary intent category based on priority order:
    price_drop > sale > wishlist > purchase_intent > availability > delivery > product_link.
    Returns (intent_category, matched_keyword) or (None, None) if no match.
    """
    if not comment_text or not isinstance(comment_text, str):
        return None, None
        
    text_lower = comment_text.lower()
    
    for category_name, keywords in INTENT_CATEGORIES:
        for keyword in keywords:
            if keyword in text_lower:
                return category_name, keyword
                
    return None, None

def filter_youtube_comments():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    input_file = os.path.join(project_root, "Raw Data", "youtube_comments_real.csv")
    output_file = os.path.join(project_root, "Raw Data", "youtube_comments_filtered_real.csv")
    if not os.path.exists(input_file):
        print(f"[!] Error: Input file not found at {input_file}")
        print("Please ensure Raw Data/youtube_comments_test.csv exists before running.")
        return

    total_read = 0
    filtered_rows = []
    category_counts = Counter({category_name: 0 for category_name, _ in INTENT_CATEGORIES})

    with open(input_file, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        
        for row in reader:
            total_read += 1
            comment_body = row.get("comment", "")
            
            category, matched_keyword = classify_intent(comment_body)
            
            if category:
                category_counts[category] += 1
                filtered_rows.append({
                    "comment": row.get("comment", ""),
                    "author": row.get("author", ""),
                    "published_at": row.get("published_at", ""),
                    "like_count": row.get("like_count", 0),
                    "video_id": row.get("video_id", ""),
                    "intent_category": category,
                    "matched_keyword": matched_keyword
                })

    fieldnames = [
        "comment",
        "author",
        "published_at",
        "like_count",
        "video_id",
        "intent_category",
        "matched_keyword"
    ]

    with open(output_file, mode="w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(filtered_rows)

    print("=======================================================")
    print(" YouTube Comments Filtering Report")
    print("=======================================================")
    print(f" Total Comments Read        : {total_read}")
    print(f" Total Relevant Comments    : {len(filtered_rows)}")
    print("-------------------------------------------------------")
    print(" Intent Category Breakdown:")
    for category_name, _ in INTENT_CATEGORIES:
        count = category_counts[category_name]
        print(f"   - {category_name:<18} : {count}")
    print("-------------------------------------------------------")
    print(f" Saved Filtered File To     : {output_file}")
    print("=======================================================")

if __name__ == "__main__":
    filter_youtube_comments()
