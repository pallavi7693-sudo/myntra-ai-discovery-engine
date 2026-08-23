import os
import sys
import json
import pandas as pd

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

UNMET_NEED_TAXONOMY = [
    {
        "id": "price_value_confidence",
        "title": "Price & Value Confidence",
        "statement": "Need transparent price history trends and real-time sale drop nudges to verify optimal purchase timing before checkout.",
        "primary_barrier": "price",
        "associated_barriers": ["price"],
        "supporting_behaviors": ["wishlist", "purchase_postponed", "price_history", "discount_information"],
        "associated_outcome": "Prevents deal-hesitation waiting loops, reduces cart postponement, and triggers immediate buy action during price drops."
    },
    {
        "id": "quality_material_transparency",
        "title": "Tactile Quality & Fabric Feel Verification",
        "statement": "Need unedited fabric texture details and real wearer feedback to verify material durability and opacity before buying.",
        "primary_barrier": "quality_uncertainty",
        "associated_barriers": ["quality_uncertainty"],
        "supporting_behaviors": ["product_research", "reviews", "quality"],
        "associated_outcome": "Overcomes online fabric texture ambiguity and builds high consumer brand trust."
    },
    {
        "id": "delivery_fulfillment_predictability",
        "title": "Predictable Delivery Timelines & Date Commitments",
        "statement": "Need guaranteed delivery date commitments and courier dispatch tracking for time-sensitive occasion wear.",
        "primary_barrier": "delivery_concern",
        "associated_barriers": ["delivery_concern"],
        "supporting_behaviors": ["purchase_postponed", "delivery"],
        "associated_outcome": "Eliminates shipping delay anxiety and prevents cart abandonment for event-based purchases."
    },
    {
        "id": "return_exchange_frictionless",
        "title": "Risk-Free Return & Fee-Free Size Exchange Assurance",
        "statement": "Need clear, hassle-free return windows and free first size-exchange guarantees to mitigate post-order sizing regret.",
        "primary_barrier": "return_concern",
        "associated_barriers": ["return_concern"],
        "supporting_behaviors": ["recommendation_seeking", "purchase_postponed"],
        "associated_outcome": "Lowers purchasing risk for unfamiliar fashion brands and sizing-sensitive apparel."
    },
    {
        "id": "fit_size_confidence",
        "title": "Fit & Sizing Confidence Before Purchase",
        "statement": "Need greater confidence that a wishlisted fashion product will fit properly before checkout to avoid return hassle.",
        "primary_barrier": "size_uncertainty",
        "associated_barriers": ["size_uncertainty", "fit_uncertainty"],
        "supporting_behaviors": ["wishlist", "purchase_postponed", "product_research", "size_information"],
        "associated_outcome": "Reduces brand sizing doubts, eliminates size-swap returns, and accelerates wishlist-to-checkout conversion."
    },
    {
        "id": "social_proof_unfiltered",
        "title": "Unedited Real-Wearer Photos & Try-On Social Proof",
        "statement": "Need unedited real customer try-on photos and body-dimension-matched reviews to visualize actual product appearance.",
        "primary_barrier": "lack_of_reviews",
        "associated_barriers": ["lack_of_reviews"],
        "supporting_behaviors": ["product_research", "reviews", "styling"],
        "associated_outcome": "Fills critical social proof gaps for newly launched items lacking customer feedback."
    },
    {
        "id": "restock_availability_visibility",
        "title": "Restock Alerts & Size Availability Nudges",
        "statement": "Need real-time size restock notifications and inventory availability nudges for wishlisted out-of-stock items.",
        "primary_barrier": "availability",
        "associated_barriers": ["availability"],
        "supporting_behaviors": ["wishlist", "purchase_postponed"],
        "associated_outcome": "Recaptures lost demand for out-of-stock sizes when inventory is replenished."
    }
]

def detect_unmet_needs(json_path=None):
    if json_path is None:
        json_path = os.path.join(BASE_DIR, "Processed Data", "myntra_multidimensional_enriched.json")
        
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Enriched dataset not found at {json_path}.")
        
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    df = pd.DataFrame(data)
    total_records = len(df)
    
    # Myntra Purchase-Hesitation Sub-Population
    def is_myntra_friction(r):
        if r.get("platform_brand") != "myntra":
            return False
        dims = r.get("analytical_dimensions", {})
        barriers = dims.get("purchase_barriers", [])
        status = dims.get("purchase_status", "")
        stage = dims.get("purchase_stage", "")
        return len(barriers) > 0 or status == "postponed" or stage in ["consideration", "shortlist"]
        
    myntra_friction_df = df[df.apply(is_myntra_friction, axis=1)]
    hesitation_denom = len(myntra_friction_df)
    
    detected_needs = []
    
    for item in UNMET_NEED_TAXONOMY:
        need_barriers = item["associated_barriers"]
        
        # Filter matching records in Myntra friction sub-population
        matched = myntra_friction_df[
            myntra_friction_df["analytical_dimensions"].apply(
                lambda d: any(b in d.get("purchase_barriers", []) for b in need_barriers) if isinstance(d, dict) else False
            )
        ]
        
        evidence_count = len(matched)
        if evidence_count == 0:
            continue
            
        unique_datasets = sorted(list(matched["source_file"].unique()))
        unique_channels = sorted(list(matched["source_channel"].unique()))
        
        share_pct = round((evidence_count / hesitation_denom * 100), 1) if hesitation_denom > 0 else 0.0
        total_share_pct = round((evidence_count / total_records * 100), 1)
        
        # Recurrence Strength Scoring Rule
        if evidence_count >= 100 and len(unique_datasets) >= 3:
            strength = "High"
        elif evidence_count >= 30 and len(unique_datasets) >= 2:
            strength = "Medium"
        else:
            strength = "Low"
            
        # Top 3 verbatim consumer quotes
        quotes = []
        for idx, row in matched.head(3).iterrows():
            sent_info = row.get("sentiment_analysis", {})
            quotes.append({
                "source_file": row["source_file"],
                "source_channel": row["source_channel"],
                "raw_text": row["raw_text"],
                "primary_intent": row.get("primary_intent", "unclassified"),
                "sentiment_label": sent_info.get("sentiment_label", "Neutral")
            })
            
        detected_needs.append({
            "unmet_need_id": item["id"],
            "title": item["title"],
            "statement": item["statement"],
            "strength": strength,
            "evidence_count": evidence_count,
            "hesitation_denominator": hesitation_denom,
            "share_pct": share_pct,
            "total_corpus_count": total_records,
            "total_share_pct": total_share_pct,
            "unique_datasets_count": len(unique_datasets),
            "unique_datasets": unique_datasets,
            "unique_channels_count": len(unique_channels),
            "unique_channels": unique_channels,
            "associated_purchase_barrier": item["primary_barrier"].replace("_", " ").title(),
            "associated_purchase_barrier_raw": item["primary_barrier"],
            "associated_purchase_behavior": "Purchase Postponed / Cart Waiting",
            "supporting_behavioral_signals": item["supporting_behaviors"],
            "associated_user_outcome": item["associated_outcome"],
            "representative_evidence": quotes
        })
        
    # Sort detected unmet needs by strength (High > Medium > Low) and evidence count
    strength_rank = {"High": 0, "Medium": 1, "Low": 2}
    detected_needs = sorted(detected_needs, key=lambda x: (strength_rank.get(x["strength"], 3), -x["evidence_count"]))
    
    # Add ranking index
    for idx, need in enumerate(detected_needs, 1):
        need["rank"] = idx
        
    results_payload = {
        "summary": {
            "total_unmet_needs_detected": len(detected_needs),
            "myntra_friction_denominator": hesitation_denom,
            "total_dataset_records": total_records
        },
        "ranked_unmet_needs": detected_needs
    }
    
    output_path = os.path.join(BASE_DIR, "Processed Data", "unmet_needs_results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results_payload, f, indent=2)
        
    return results_payload

if __name__ == "__main__":
    print("==================================================")
    print("RUNNING UNMET NEED DETECTION ENGINE")
    print("==================================================\n")
    res = detect_unmet_needs()
    print(f"Detected {res['summary']['total_unmet_needs_detected']} consistent unmet needs:\n")
    for n in res["ranked_unmet_needs"]:
        print(f"  #{n['rank']} {n['title']} [{n['strength']} Strength]")
        print(f"     Statement: \"{n['statement']}\"")
        print(f"     Evidence: {n['evidence_count']}/{n['hesitation_denominator']} ({n['share_pct']}%) | Datasets: {n['unique_datasets_count']} | Channels: {n['unique_channels_count']}\n")
    print("==================================================")
