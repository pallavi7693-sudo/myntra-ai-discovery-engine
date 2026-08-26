import os
import sys
import glob
import json
import re
import pandas as pd

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Initialize VADER sentiment analyzer offline/quietly
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)

_sia = SentimentIntensityAnalyzer()

def analyze_sentiment_vader(text):
    """Calculates deterministic VADER sentiment scores without fabricating data for empty/unusable text."""
    if text is None:
        return {
            "sentiment_label": "Unknown",
            "sentiment_score": None,
            "sentiment_confidence": None,
            "components": {"neg": 0.0, "neu": 0.0, "pos": 0.0, "compound": 0.0}
        }
        
    text_str = str(text).strip()
    if len(text_str) < 5 or text_str.lower() in ["nan", "null", "none"]:
        return {
            "sentiment_label": "Unknown",
            "sentiment_score": None,
            "sentiment_confidence": None,
            "components": {"neg": 0.0, "neu": 0.0, "pos": 0.0, "compound": 0.0}
        }
        
    scores = _sia.polarity_scores(text_str)
    compound = round(scores["compound"], 4)
    pos = round(scores["pos"], 4)
    neg = round(scores["neg"], 4)
    neu = round(scores["neu"], 4)
    
    confidence = round(max(pos, neu, neg), 2)
    
    if pos >= 0.15 and neg >= 0.15 and -0.40 <= compound <= 0.40:
        label = "Mixed"
    elif compound >= 0.05:
        label = "Positive"
    elif compound <= -0.05:
        label = "Negative"
    else:
        label = "Neutral"
        
    return {
        "sentiment_label": label,
        "sentiment_score": compound,
        "sentiment_confidence": confidence,
        "components": {
            "neg": neg,
            "neu": neu,
            "pos": pos,
            "compound": compound
        }
    }

# Negation terms for 4-word window check (Edge Case 5.1)
NEGATION_TERMS = {'not', "don't", 'dont', 'never', 'no', "wouldn't", 'wouldnt', 'cannot', "can't", 'cant', 'without', 'hardly', 'barely'}

# Keyword taxonomies with pattern rules
TAXONOMY_PATTERNS = {
    "purchase_barriers": {
        "price": [r'\bprice\b', r'\bexpensive\b', r'\bcost\b', r'\bcostly\b', r'\bhigh price\b', r'\btoo high\b', r'\boverpriced\b', r'\brs\b', r'\brupees\b', r'₹'],
        "size_uncertainty": [r'\bsize\b', r'\bsizing\b', r'\bmedium\b', r'\bsmall\b', r'\blarge\b', r'\bxl\b', r'\bxxl\b', r'\bchart\b', r'\bfit chart\b'],
        "fit_uncertainty": [r'\bfit\b', r'\bfitting\b', r'\bloose\b', r'\btight\b', r'\balteration\b', r'\bbody type\b'],
        "quality_uncertainty": [r'\bquality\b', r'\bfabric\b', r'\bmaterial\b', r'\bcloth\b', r'\bcheap\b', r'\bthin\b', r'\bsee through\b', r'\bcolor bleed\b', r'\bshrink\b'],
        "lack_of_reviews": [r'\breview\b', r'\breviews\b', r'\brating\b', r'\bratings\b', r'\bno review\b', r'\bfeedback\b'],
        "return_concern": [r'\breturn\b', r'\breturns\b', r'\brefund\b', r'\bexchange\b', r'\bpickup\b', r'\bpolicy\b'],
        "delivery_concern": [r'\bdelivery\b', r'\bshipping\b', r'\bcourier\b', r'\barrive\b', r'\blate\b', r'\btracking\b'],
        "availability": [r'\bout of stock\b', r'\bstock\b', r'\brestock\b', r'\bunavailable\b', r'\bsold out\b'],
        "lack_of_urgency": [
            r'\bnot urgent\b', r'\bno urgency\b', r'\bno hurry\b', r'\bno rush\b', r'\bin no rush\b',
            r'\bnon-urgent\b', r'\bnon urgent\b', r'\blacks urgency\b', r'\bno immediate need\b',
            r'\bjust saving\b', r'\bjust bookmarking\b', r'\bfor later\b', r'\bsaving for later\b',
            r'\bsometime\b', r'\bsomeday\b', r'\beventually\b', r'\bwhenever\b', r'\bno deadline\b',
            r'\bcasual wishlist\b', r'\bno occasion\b', r'\bjust keeping\b', r'\bhold off\b', r'\bholding off\b',
            r'\bno time pressure\b', r'\blater on\b', r'\bkeep in wishlist\b', r'\bkept in wishlist\b', r'\bkeep it in wishlist\b'
        ]
    },
    "user_behavior": {
        "wishlist": [r'\bwishlist\b', r'\bwishlisted\b', r'\bwish listing\b', r'\bsaved\b', r'\bshortlist\b'],
        "purchase_intent": [r'\bbuy\b', r'\bpurchase\b', r'\bbought\b', r'\border\b', r'\bordering\b', r'\bwant to get\b', r'\bplanning to buy\b'],
        "purchase_postponed": [r'\bwait\b', r'\bwaiting\b', r'\bpostpone\b', r'\bdelay\b', r'\bholding off\b', r'\blater\b', r'\bnext sale\b', r'\bpayday\b'],
        "product_comparison": [r'\bversus\b', r'\bvs\b', r'\bcompared\b', r'\bcomparing\b', r'\bor ajio\b', r'\bor nykaa\b', r'\bor zara\b', r'\bbetter than\b'],
        "recommendation_seeking": [r'\brecommend\b', r'\bsuggest\b', r'\bsuggestions\b', r'\blooking for\b', r'\bany good\b'],
        "product_research": [r'\bresearch\b', r'\bchecking\b', r'\breading reviews\b', r'\blooking at\b']
    },
    "information_needs": {
        "reviews": [r'\breview\b', r'\breviews\b', r'\bexperience\b', r'\brating\b'],
        "size_information": [r'\bsize chart\b', r'\bsizing info\b', r'\btrue to size\b', r'\bmeasurements\b'],
        "fit_information": [r'\bhow does it fit\b', r'\bfit guide\b', r'\btry on\b'],
        "styling": [r'\bstyle\b', r'\bstyling\b', r'\bhow to wear\b', r'\boutfit\b', r'\bpair with\b'],
        "quality": [r'\bfabric quality\b', r'\bmaterial info\b', r'\bdurable\b'],
        "price_history": [r'\blowest price\b', r'\bprice history\b', r'\bprice drop\b'],
        "discount_information": [r'\bcoupon\b', r'\bdiscount\b', r'\bsale date\b', r'\boffer\b'],
        "urgency_triggers": [r'\blimited stock\b', r'\burgent\b', r'\bprice drop alert\b', r'\bhurry\b']
    },
    "decision_factors": {
        "price": [r'\bprice\b', r'\bcost\b', r'\bcheap\b', r'\baffordable\b', r'\bbudget\b', r'\bvalue\b'],
        "fit": [r'\bfit\b', r'\bfitting\b'],
        "size": [r'\bsize\b', r'\bsizing\b'],
        "style": [r'\bstyle\b', r'\blooks\b', r'\bpretty\b', r'\bdesign\b', r'\bcolor\b', r'\baesthetic\b'],
        "quality": [r'\bquality\b', r'\bfabric\b', r'\bmaterial\b'],
        "reviews": [r'\breviews\b', r'\bratings\b', r'\bsocial proof\b'],
        "brand": [r'\bbrand\b', r'\broadster\b', r'\bhrx\b', r'\bmango\b', r'\bzara\b', r'\bhm\b', r'\banouk\b'],
        "urgency": [r'\burgent\b', r'\burgency\b', r'\bdeadline\b', r'\boccasion\b', r'\bneed soon\b']
    },
    "opportunity_area": {
        "better_size_guidance": [r'\bsize\b', r'\bsizing\b', r'\bchart\b'],
        "better_fit_information": [r'\bfit\b', r'\bfitting\b', r'\bbody\b'],
        "stronger_social_proof": [r'\breview\b', r'\breviews\b', r'\brating\b'],
        "better_price_visibility": [r'\bprice\b', r'\bcost\b', r'\bdiscount\b', r'\bcoupon\b'],
        "better_product_comparison": [r'\bcompare\b', r'\bvs\b', r'\bbetter\b'],
        "better_quality_information": [r'\bquality\b', r'\bfabric\b', r'\bmaterial\b'],
        "better_return_information": [r'\breturn\b', r'\brefund\b', r'\bexchange\b'],
        "create_purchase_urgency": [r'\burgency\b', r'\blimited time\b', r'\bstock count\b', r'\bprice drop alert\b', r'\bhurry\b', r'\bfor later\b', r'\bnot urgent\b', r'\bno hurry\b']
    }
}

def has_negation_before(words, idx, window=4):
    """Check 4-word preceding window for negation tokens (Edge Case 5.1)."""
    start_idx = max(0, idx - window)
    preceding_words = [w.lower().strip(".,!?\"'") for w in words[start_idx:idx]]
    return any(neg in preceding_words for neg in NEGATION_TERMS)

def extract_dimensions_from_text(text):
    """Extract analytical_dimensions arrays respecting negation windows."""
    clean_text = str(text).lower()
    words = clean_text.split()
    
    extracted = {
        "user_behavior": set(),
        "purchase_barriers": set(),
        "information_needs": set(),
        "decision_factors": set(),
        "opportunity_area": set()
    }
    
    for dim_key, categories in TAXONOMY_PATTERNS.items():
        for category_name, patterns in categories.items():
            for pattern in patterns:
                matches = list(re.finditer(pattern, clean_text))
                for match in matches:
                    # Find word index of match
                    char_pos = match.start()
                    word_idx = len(clean_text[:char_pos].split())
                    
                    # Apply negation window safeguard
                    if not has_negation_before(words, word_idx):
                        extracted[dim_key].add(category_name)
                        break # Found valid non-negated match for this category
                        
    # Convert sets to sorted lists
    return {k: sorted(list(v)) for k, v in extracted.items()}

def derive_purchase_stage_and_status(dimensions, text, primary_intent):
    """Derive purchase_stage and purchase_status."""
    behaviors = set(dimensions["user_behavior"])
    barriers = set(dimensions["purchase_barriers"])
    
    # Stage derivation
    if "purchase_completed" in behaviors or "bought" in str(text).lower():
        stage = "post_purchase"
        status = "purchased"
    elif "purchase_intent" in behaviors:
        stage = "purchase_intent"
        status = "postponed" if "purchase_postponed" in behaviors else "likely_to_purchase"
    elif "wishlist" in behaviors or "product_comparison" in behaviors:
        stage = "consideration"
        status = "postponed" if ("purchase_postponed" in behaviors or len(barriers) > 0) else "uncertain"
    elif "recommendation_seeking" in behaviors:
        stage = "discovery"
        status = "uncertain"
    else:
        stage = "consideration" if len(barriers) > 0 else "discovery"
        status = "abandoned" if primary_intent in ["cancellation_refund", "customer_service"] else "uncertain"
        
    return stage, status

def process_single_file(file_path):
    """Process a single CSV dataset file and return enriched record list."""
    basename = os.path.basename(file_path)
    folder = os.path.dirname(file_path)
    
    # Detect channel & brand
    if "reddit" in basename:
        channel = "reddit"
        brand = "myntra"
    elif "playstore" in basename:
        channel = "playstore"
        brand = "ajio" if "ajio" in basename else ("nykaa" if "nykaa" in basename else "myntra")
    elif "appstore" in basename:
        channel = "appstore"
        brand = "nykaa" if "nykaa" in basename else "myntra"
    elif "youtube" in basename:
        channel = "youtube"
        brand = "myntra"
    else:
        channel = "web"
        brand = "myntra"
        
    # Load dataset safely
    df_check = pd.read_csv(file_path, nrows=2)
    is_headerless = False
    for col in df_check.columns:
        if any(term in str(col) for term in ["http", "Google Play", "App Store", "635d5742", "103afb18", "a85e6753"]):
            is_headerless = True
            break
            
    if is_headerless:
        df = pd.read_csv(file_path, header=None)
    else:
        df = pd.read_csv(file_path)
        
    records = []
    
    for idx, row in df.iterrows():
        # Text extraction
        if is_headerless:
            text_idx = 7 if df.shape[1] > 7 else (df.shape[1] - 3 if df.shape[1] >= 3 else 0)
            raw_text = str(row.iloc[text_idx]) if pd.notnull(row.iloc[text_idx]) else ""
            parent_context = ""
        elif 'body' in df.columns or 'title' in df.columns:
            title = str(row.get('title', '')) if pd.notnull(row.get('title')) else ""
            body = str(row.get('body', '')) if pd.notnull(row.get('body')) else ""
            parent_context = str(row.get('post_context', '')) if pd.notnull(row.get('post_context')) else ""
            raw_text = (title + " " + body).str.strip() if hasattr(title + " " + body, 'str') else (title + " " + body).strip()
        elif 'text' in df.columns:
            raw_text = str(row.get('text', ''))
            parent_context = ""
        elif 'comment' in df.columns:
            raw_text = str(row.get('comment', ''))
            parent_context = ""
        else:
            raw_text = str(row.iloc[0])
            parent_context = ""
            
        # Thread Context Merger with Child Override Safeguard (Edge Case 3.2)
        explicit_child_intent_keywords = ['support', 'refund', 'cancel', 'delivery', 'complaint', 'fraud', 'bad quality']
        child_has_explicit_divergence = any(kw in raw_text.lower() for kw in explicit_child_intent_keywords)
        
        if parent_context and not child_has_explicit_divergence:
            processed_text = f"[Context: {parent_context[:100]}] {raw_text}"
        else:
            processed_text = raw_text
            
        # Preserve original primary_intent strictly
        primary_intent = str(row.get('primary_intent', 'unclassified'))
        
        # Extract analytical dimensions
        dims = extract_dimensions_from_text(processed_text)
        
        # Map primary_intent signal into user_behavior if wishlist/price_drop
        if primary_intent == "wishlist" and "wishlist" not in dims["user_behavior"]:
            dims["user_behavior"].append("wishlist")
        if primary_intent == "price_drop" and "purchase_postponed" not in dims["user_behavior"]:
            dims["user_behavior"].append("purchase_postponed")
            dims["purchase_barriers"].append("price")
            
        stage, status = derive_purchase_stage_and_status(dims, processed_text, primary_intent)
        
        # User Segment
        if "price" in dims["purchase_barriers"]:
            segment = "price_sensitive"
        elif "size_uncertainty" in dims["purchase_barriers"] or "fit_uncertainty" in dims["purchase_barriers"]:
            segment = "fit_hesitant"
        elif "reviews" in dims["information_needs"]:
            segment = "research_heavy"
        elif "wishlist" in dims["user_behavior"]:
            segment = "wishlist_heavy"
        else:
            segment = "general_shopper"
            
        # Calculate sentiment analysis (UNDERSTAND stage)
        sentiment_info = analyze_sentiment_vader(processed_text)
        
        rec = {
            "record_id": f"{basename}_{idx}",
            "source_file": basename,
            "source_channel": channel,
            "platform_brand": brand,
            "raw_text": raw_text[:300],
            "processed_text_with_context": processed_text[:350],
            "primary_intent": primary_intent,
            "user_segment": segment,
            "sentiment_analysis": sentiment_info,
            "analytical_dimensions": {
                "user_behavior": dims["user_behavior"],
                "purchase_stage": stage,
                "purchase_status": status,
                "purchase_barriers": dims["purchase_barriers"],
                "information_needs": dims["information_needs"],
                "decision_factors": dims["decision_factors"],
                "opportunity_area": dims["opportunity_area"]
            }
        }
        records.append(rec)
        
    return records

def run_extraction_pipeline():
    raw_dir = "Raw Data"
    processed_dir = "Processed Data"
    
    all_files = sorted(glob.glob(os.path.join(raw_dir, "*.csv")) + glob.glob(os.path.join(processed_dir, "*.csv")))
    all_enriched_records = []
    
    print("==================================================")
    print("STARTING STAGE 2 MULTI-DIMENSIONAL EXTRACTION PIPELINE")
    print("==================================================\n")
    
    for fpath in all_files:
        fname = os.path.basename(fpath)
        print(f"--- Extracting dimensions for [{fname}] ---")
        file_records = process_single_file(fpath)
        all_enriched_records.extend(file_records)
        print(f"   Extracted {len(file_records)} enriched records.")
        
    output_path = os.path.join(processed_dir, "myntra_multidimensional_enriched.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_enriched_records, f, indent=2)
        
    print("\n==================================================")
    print(f"EXTRACTION COMPLETE: Enriched {len(all_enriched_records)} records.")
    print(f"Saved multi-dimensional dataset to: {output_path}")
    print("==================================================")
    return output_path

if __name__ == "__main__":
    run_extraction_pipeline()
