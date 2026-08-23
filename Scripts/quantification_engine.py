import os
import sys
import json
import pandas as pd

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def load_enriched_dataset(json_path="Processed Data/myntra_multidimensional_enriched.json"):
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Enriched dataset not found at {json_path}. Run Stage 2 first.")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return pd.DataFrame(data)

def format_scoped_metric(metric_title, count, total_population, population_name):
    """Enforce explicit denominator scoping with platform brand distinction."""
    pct = round((count / total_population * 100), 1) if total_population > 0 else 0.0
    return {
        "metric_title": metric_title,
        "numerator": count,
        "denominator": total_population,
        "percentage": pct,
        "population_name": population_name,
        "formatted_text": f"{pct}% of {population_name} ({count}/{total_population}) mentioned {metric_title.lower()}."
    }

def run_quantification_analysis():
    json_path = "Processed Data/myntra_multidimensional_enriched.json"
    print("==================================================")
    print("MYNTRA-SCOPED PURCHASE FRICTION & WISHLIST INTENT QUANTIFICATION")
    print("==================================================\n")
    
    df = load_enriched_dataset(json_path)
    total_records = len(df)
    
    # 1. SCOPED MYNTRA-ONLY FRICTION POPULATION (USER RULE)
    # Purchase friction is analyzed ONLY on Myntra customer reviews/discussions
    def is_myntra_friction_record(row):
        if row.get("platform_brand") != "myntra":
            return False
        dims = row.get("analytical_dimensions", {})
        barriers = dims.get("purchase_barriers", [])
        status = dims.get("purchase_status", "")
        stage = dims.get("purchase_stage", "")
        return len(barriers) > 0 or status == "postponed" or stage in ["consideration", "shortlist"]
        
    myntra_friction_df = df[df.apply(is_myntra_friction_record, axis=1)]
    myntra_friction_denom = len(myntra_friction_df)
    myntra_pop_name = "Myntra purchase-hesitation conversations"
    
    print(f"--- Population Scoping ---")
    print(f"Total Dataset Records (All Brands): {total_records}")
    print(f"Myntra-Only Scoped Friction Sub-Population: {myntra_friction_denom} records\n")
    
    # 2. Compute Myntra Purchase Barrier Frequencies
    barrier_counts = {}
    for idx, row in myntra_friction_df.iterrows():
        barriers = row.get("analytical_dimensions", {}).get("purchase_barriers", [])
        for b in barriers:
            barrier_counts[b] = barrier_counts.get(b, 0) + 1
            
    print("--- Myntra Purchase Barrier Findings (Exact Myntra Denominators) ---")
    scoped_barrier_results = []
    for barrier, count in sorted(barrier_counts.items(), key=lambda x: x[1], reverse=True):
        metric_info = format_scoped_metric(barrier, count, myntra_friction_denom, myntra_pop_name)
        scoped_barrier_results.append(metric_info)
        print(f"  • {metric_info['formatted_text']}")
    print()
    
    # 3. Compute Myntra Opportunity Area Scored Matrix
    opp_counts = {}
    for idx, row in myntra_friction_df.iterrows():
        opps = row.get("analytical_dimensions", {}).get("opportunity_area", [])
        for o in opps:
            opp_counts[o] = opp_counts.get(o, 0) + 1
            
    print("--- Myntra Opportunity Area Rankings ---")
    opportunity_matrix = []
    for opp, count in sorted(opp_counts.items(), key=lambda x: x[1], reverse=True):
        metric_info = format_scoped_metric(opp, count, myntra_friction_denom, myntra_pop_name)
        opportunity_matrix.append(metric_info)
        print(f"  • {metric_info['formatted_text']}")
        
    # 4. Multi-Platform Wishlist Intent Population (All Platforms)
    def is_wishlist_intent_record(row):
        dims = row.get("analytical_dimensions", {})
        behaviors = dims.get("user_behavior", [])
        return "wishlist" in behaviors or "bookmarking" in behaviors or row.get("primary_intent") == "wishlist"
        
    wishlist_all_df = df[df.apply(is_wishlist_intent_record, axis=1)]
    wishlist_denom = len(wishlist_all_df)
    
    # 5. SENTIMENT ANALYSIS QUANTIFICATION (UNDERSTAND -> QUANTIFY)
    df["sent_label"] = df["sentiment_analysis"].apply(lambda s: s.get("sentiment_label", "Unknown") if isinstance(s, dict) else "Unknown")
    usable_sent_df = df[df["sent_label"] != "Unknown"]
    usable_sent_denom = len(usable_sent_df)
    
    overall_sentiment_dist = {}
    if usable_sent_denom > 0:
        for lbl, cnt in usable_sent_df["sent_label"].value_counts().items():
            pct = round((cnt / usable_sent_denom * 100), 1)
            overall_sentiment_dist[lbl] = {
                "numerator": cnt,
                "denominator": usable_sent_denom,
                "percentage": pct,
                "formatted_text": f"{pct}% ({cnt}/{usable_sent_denom}) of usable records had {lbl.lower()} sentiment."
            }
            
    # Sentiment by Purchase Barrier Category (Myntra Sub-Population)
    barrier_sentiment = {}
    for barrier in barrier_counts.keys():
        sub_barrier = myntra_friction_df[myntra_friction_df["analytical_dimensions"].apply(lambda d: barrier in d.get("purchase_barriers", []))]
        sub_usable = sub_barrier[sub_barrier["sentiment_analysis"].apply(lambda s: s.get("sentiment_label", "Unknown") != "Unknown" if isinstance(s, dict) else False)]
        sub_denom = len(sub_usable)
        dist = {}
        if sub_denom > 0:
            for lbl, cnt in sub_usable["sentiment_analysis"].apply(lambda s: s.get("sentiment_label")).value_counts().items():
                pct = round((cnt / sub_denom * 100), 1)
                dist[lbl] = {
                    "numerator": cnt,
                    "denominator": sub_denom,
                    "percentage": pct,
                    "formatted_text": f"{pct}% ({cnt}/{sub_denom}) of '{barrier}' friction records expressed {lbl.lower()} sentiment."
                }
        barrier_sentiment[barrier] = {
            "total_barrier_records": len(sub_barrier),
            "usable_denominator": sub_denom,
            "distribution": dist
        }
        
    # Sentiment for Postponed Purchases
    postponed_df = myntra_friction_df[myntra_friction_df["analytical_dimensions"].apply(lambda d: d.get("purchase_status") == "postponed")]
    postponed_usable = postponed_df[postponed_df["sentiment_analysis"].apply(lambda s: s.get("sentiment_label", "Unknown") != "Unknown" if isinstance(s, dict) else False)]
    postponed_denom = len(postponed_usable)
    postponed_dist = {}
    if postponed_denom > 0:
        for lbl, cnt in postponed_usable["sentiment_analysis"].apply(lambda s: s.get("sentiment_label")).value_counts().items():
            pct = round((cnt / postponed_denom * 100), 1)
            postponed_dist[lbl] = {
                "numerator": cnt,
                "denominator": postponed_denom,
                "percentage": pct,
                "formatted_text": f"{pct}% ({cnt}/{postponed_denom}) of postponed purchase records expressed {lbl.lower()} sentiment."
            }
            
    results_payload = {
        "dataset_summary": {
            "total_records_all_brands": total_records,
            "usable_sentiment_denominator": usable_sent_denom,
            "myntra_friction_population_denominator": myntra_friction_denom,
            "all_brands_wishlist_intent_denominator": wishlist_denom
        },
        "myntra_scoped_barriers": scoped_barrier_results,
        "opportunity_matrix": opportunity_matrix,
        "sentiment_quantification": {
            "overall_sentiment_distribution": overall_sentiment_dist,
            "barrier_sentiment_breakdown": barrier_sentiment,
            "postponed_purchase_sentiment": {
                "total_postponed_records": len(postponed_df),
                "usable_denominator": postponed_denom,
                "distribution": postponed_dist
            }
        }
    }
    
    output_report_path = "Processed Data/quantification_results.json"
    with open(output_report_path, "w", encoding="utf-8") as f:
        json.dump(results_payload, f, indent=2)
        
    print("\n==================================================")
    print(f"QUANTIFICATION ANALYSIS COMPLETE (MYNTRA-SCOPED FRICTION)")
    print(f"Saved results to: {output_report_path}")
    print("==================================================")
    return results_payload

if __name__ == "__main__":
    run_quantification_analysis()
