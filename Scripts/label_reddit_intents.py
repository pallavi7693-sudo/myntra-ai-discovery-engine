import os
import csv
import re
from collections import Counter

# Strong Myntra & Multi-Platform E-commerce Specific Context Signals
# Note: Generic words ("buy", "price", "sale", "delivery", "brand", "fashion")
# and standalone brand names ("Nike", "Zara", "H&M") are strictly EXCLUDED.
STRONG_MYNTRA_ECOMMERCE_SIGNALS = [
    r"\bmyntrasucks\b",
    r"\beors\b",                      # End of Reason Sale
    r"\bmyncash\b",                   # Myntra cash rewards
    r"\bekart\b",                     # Myntra/Flipkart logistics partner
    r"\bmyntra app\b",
    r"\bonline shopping app\b",
    r"\be-?commerce platform\b",
    r"\bshopping site\b",
    r"\bcourier partner\b",
    r"\bajio\b",                      # Competing Indian fashion e-commerce platforms
    r"\bnykaa fashion\b",
    r"\burbanic\b"
]

# Specific Multi-Word / Domain-Specific Regex Patterns for Intent Classification
INTENT_PATTERNS = {
    "wishlist": [
        r"\bwishlist\b", r"\bwish list\b", r"\bwishlisting\b", r"\badded to wishlist\b",
        r"\badd to wishlist\b", r"\bwishlist limit\b", r"\bkeep in wishlist\b", r"\bsaved to wishlist\b"
    ],
    "price_drop": [
        r"\bprice drop\b", r"\bprice down\b", r"\bprice reduced\b", r"\bprice decrease\b",
        r"\bwaiting for price\b", r"\bwhen will price\b", r"\bprice dropped\b",
        r"\bcheaper during sale\b", r"\bprice is high\b", r"\bprice changed\b"
    ],
    "sale_discount": [
        r"\bend of reason sale\b", r"\beors\b", r"\bbig fashion festival\b", r"\bbff\b",
        r"\bon sale\b", r"\bsale price\b", r"\bduring sale\b", r"\bupcoming sale\b",
        r"\bnext sale\b", r"\bsale live\b", r"\brepublic sale\b"
    ],
    "coupon": [
        r"\bmyncash\b", r"\bcoupon code\b", r"\bpromo code\b", r"\bextra discount\b",
        r"\bbank offer\b", r"\bcard offer\b", r"\bdaily cash\b", r"\breward system\b",
        r"\bplatform fee\b"
    ],
    "restock_availability": [
        r"\bout of stock\b", r"\bback in stock\b", r"\brestock\b", r"\brestocking\b",
        r"\bwhen will it be available\b", r"\bstock out\b", r"\bsize not available\b",
        r"\bsize available\b"
    ],
    "purchase_intent": [
        r"\bwant to buy\b", r"\bplanning to buy\b", r"\bordering the\b", r"\bplaced an order\b",
        r"\bplaced order\b", r"\bgoing to buy\b", r"\bbought this\b", r"\bwhere to buy\b",
        r"\bwhere can i buy\b", r"\bordered the same\b"
    ],
    "product_quality": [
        r"\bfake product\b", r"\bcounterfeit\b", r"\bauthentic\b", r"\bnot original\b",
        r"\bpoor quality\b", r"\bquality issue\b", r"\bstitching\b", r"\bfabric quality\b",
        r"\bwrong size\b", r"\bsize issue\b", r"\btrue to size\b"
    ],
    "delivery": [
        r"\bdelivery delayed\b", r"\bdelayed order\b", r"\bdelayed delivery\b",
        r"\bnot delivered\b", r"\bekart\b", r"\btracking status\b", r"\bdelivery date\b",
        r"\bdelivery agent\b", r"\bout for delivery\b", r"\bsort facility\b"
    ],
    "cancellation_refund": [
        r"\bcancel order\b", r"\bcancelled by myntra\b", r"\bdenied return\b",
        r"\brefund status\b", r"\bmoney back\b", r"\breturn issue\b",
        r"\binitiate refund\b", r"\bexchange issue\b", r"\bcancelled\b", r"\brefund\b"
    ],
    "customer_service": [
        r"\bcustomer care\b", r"\bcustomer service\b", r"\bsupport team\b",
        r"\bgrievance\b", r"\bhelp center\b", r"\bescalated\b",
        r"\bticket raised\b", r"\bcustomer support\b"
    ],
    "product_discovery": [
        r"\bbrand recommendation\b", r"\balternative to\b", r"\bsimilar product\b",
        r"\bcomparison between\b", r"\bwhich brand is best\b", r"\bsuggest me\b",
        r"\brecommendations for\b"
    ]
}

def is_myntra_relevant(text):
    """
    Conservative Myntra Relevance Evaluator:
    
    1. Explicit "Myntra" check: If text contains "Myntra", return True.
    2. If "Myntra" is not mentioned, require AT LEAST TWO distinct strong 
       Myntra/e-commerce context signals (e.g., eors, myncash, ekart, online shopping app).
    3. Generic words ("buy", "price", "sale", "quality", "brand", "fashion") or 
       single brand names ("Nike", "Zara") alone are NOT sufficient and will return False.
    """
    if not text or not isinstance(text, str):
        return False, False

    text_lower = text.lower()

    # 1. Condition 1: Explicit Myntra check (word boundary match)
    if re.search(r"\bmyntra\b", text_lower):
        return True, True  # (is_relevant, has_explicit_myntra)

    # 2. Condition 2: Require at least TWO distinct strong Myntra/e-commerce signals
    distinct_signals = set()
    for pattern in STRONG_MYNTRA_ECOMMERCE_SIGNALS:
        if re.search(pattern, text_lower):
            distinct_signals.add(pattern)
            if len(distinct_signals) >= 2:
                return True, False  # (is_relevant, has_explicit_myntra)

    # Condition 5: Otherwise mark as irrelevant
    return False, False

def classify_row(row):
    """
    Strict rule-based classifier using regex word boundaries, phrase matching,
    and confidence level computation.
    """
    title = str(row.get("post_title") or row.get("title") or "").strip()
    body = str(row.get("text") or row.get("body") or row.get("content") or "").strip()
    context = str(row.get("post_context") or "").strip()
    candidate_intents = str(row.get("candidate_intents") or "").strip().lower()

    combined_text = f"{title} {body} {context}"

    # Evaluate conservative relevance
    is_relevant, has_explicit_myntra = is_myntra_relevant(combined_text)

    if not is_relevant:
        return "other", "", 0.0, False

    text_lower = combined_text.lower()
    scores = {}

    # Score Intent Categories using exact word boundaries
    for intent, patterns in INTENT_PATTERNS.items():
        score = 0.0
        for pattern in patterns:
            if re.search(pattern, text_lower):
                weight = 1.5 if r"\s" in pattern or " " in pattern else 1.0
                score += weight

        # candidate_intents acts ONLY as a supporting boost (+0.3) if text already matched an intent
        if score > 0 and candidate_intents and intent in candidate_intents:
            score += 0.3

        if score > 0:
            scores[intent] = score

    if not scores:
        return "other", "", 0.50 if has_explicit_myntra else 0.30, True

    # Sort intents by score descending
    sorted_intents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    primary_intent = sorted_intents[0][0]
    top_score = sorted_intents[0][1]

    secondary_list = [intent for intent, s in sorted_intents[1:] if s > 0]
    secondary_intents_str = "; ".join(secondary_list)

    # Confidence Scoring Logic:
    # - Explicit Myntra + strong intent phrase = high confidence (0.85 - 0.95)
    # - Strong intent phrase without explicit Myntra but with e-commerce context = medium confidence (0.70 - 0.75)
    # - Weak/fallback = low confidence (0.45)
    if has_explicit_myntra and top_score >= 1.5:
        confidence = 0.95
    elif has_explicit_myntra and top_score >= 1.0:
        confidence = 0.85
    elif not has_explicit_myntra and top_score >= 1.5:
        confidence = 0.75
    elif top_score >= 1.0:
        confidence = 0.65
    else:
        confidence = 0.45

    return primary_intent, secondary_intents_str, confidence, True

def process_reddit_intents(input_filename="reddit_myntra_cleaned.csv", output_filename="reddit_myntra_labeled.csv"):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    input_file = os.path.join(project_root, "Raw Data", input_filename)
    output_dir = os.path.join(project_root, "Processed Data")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, output_filename)

    if not os.path.exists(input_file):
        print(f"[!] Error: Input file not found at {input_file}")
        return

    total_rows = 0
    relevant_count = 0
    irrelevant_count = 0
    low_confidence_count = 0

    all_categories = list(INTENT_PATTERNS.keys()) + ["other"]
    primary_intent_counts = Counter({cat: 0 for cat in all_categories})

    labeled_rows = []
    fieldnames = []

    with open(input_file, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        if reader.fieldnames:
            fieldnames = list(reader.fieldnames)
        else:
            fieldnames = ["id", "source", "subreddit", "post_title", "text", "url", "date", "type"]

        # Ensure output columns exist
        new_columns = ["primary_intent", "secondary_intents", "intent_confidence", "is_relevant"]
        for col in new_columns:
            if col not in fieldnames:
                fieldnames.append(col)

        for row in reader:
            total_rows += 1
            primary, secondary, confidence, is_rel = classify_row(row)

            if is_rel:
                relevant_count += 1
            else:
                irrelevant_count += 1

            if confidence < 0.60:
                low_confidence_count += 1

            primary_intent_counts[primary] += 1

            enriched_row = dict(row)
            enriched_row["primary_intent"] = primary
            enriched_row["secondary_intents"] = secondary
            enriched_row["intent_confidence"] = f"{confidence:.2f}"
            enriched_row["is_relevant"] = str(is_rel)

            labeled_rows.append(enriched_row)

    # Write output CSV
    with open(output_file, mode="w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(labeled_rows)

    # Print Summary Report
    print("=======================================================")
    print(f" Intent Classification Summary: [{input_filename}]")
    print("=======================================================")
    print(f" Total Rows Processed       : {total_rows}")
    print(f" Relevant Rows              : {relevant_count}")
    print(f" Irrelevant Rows            : {irrelevant_count}")
    print(f" Low Confidence Rows (<0.60): {low_confidence_count}")
    print("-------------------------------------------------------")
    print(" Breakdown by Primary Intent:")
    for cat in all_categories:
        print(f"   - {cat:<22} : {primary_intent_counts[cat]}")
    print("-------------------------------------------------------")
    print(f" Output Saved To            : {output_file}")
    print("=======================================================\n")

if __name__ == "__main__":
    process_reddit_intents("reddit_myntra_cleaned.csv", "reddit_myntra_labeled.csv")
    add_cleaned = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Raw Data", "reddit_myntra_additional_cleaned.csv")
    if os.path.exists(add_cleaned):
        process_reddit_intents("reddit_myntra_additional_cleaned.csv", "reddit_myntra_additional_labeled.csv")

