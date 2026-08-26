import os
import sys
import json
import pandas as pd

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

SEVERITY_WEIGHTS = {
    "better_return_information": 1.5,
    "better_quality_information": 1.4,
    "better_price_visibility": 1.3,
    "stronger_social_proof": 1.2,
    "create_purchase_urgency": 1.2,
    "better_size_guidance": 1.1,
    "better_fit_information": 1.1,
    "better_product_comparison": 1.0
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def compute_opportunity_matrix(quantification_file="Processed Data/quantification_results.json"):
    if not os.path.isabs(quantification_file):
        quantification_file = os.path.join(BASE_DIR, quantification_file)
        
    if not os.path.exists(quantification_file):
        raise FileNotFoundError(f"Quantification file missing at {quantification_file}. Run Stage 2/3 first.")
        
    with open(quantification_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    opp_raw = data.get("opportunity_matrix", [])
    
    scored_opportunities = []
    for item in opp_raw:
        area_name = item["metric_title"]
        freq_pct = item["percentage"]
        num = item["numerator"]
        denom = item["denominator"]
        pop_name = item["population_name"]
        
        weight = SEVERITY_WEIGHTS.get(area_name, 1.0)
        opp_score = round(freq_pct * weight, 2)
        
        scored_opportunities.append({
            "opportunity_area": area_name,
            "raw_frequency_pct": freq_pct,
            "numerator": num,
            "denominator": denom,
            "population_name": pop_name,
            "severity_weight": weight,
            "opportunity_score": opp_score,
            "formatted_score": f"{area_name} (Score: {opp_score} | Share: {freq_pct}% [{num}/{denom}])"
        })
        
    # Sort by weighted opportunity score descending
    scored_opportunities.sort(key=lambda x: x["opportunity_score"], reverse=True)
    return scored_opportunities

if __name__ == "__main__":
    matrix = compute_opportunity_matrix()
    print("==================================================")
    print("WEIGHTED OPPORTUNITY MATRIX (FREQUENCY x SEVERITY)")
    print("==================================================\n")
    for rank, item in enumerate(matrix, 1):
        print(f"Rank {rank}: {item['opportunity_area']}")
        print(f"   Score: {item['opportunity_score']} (Weight: {item['severity_weight']}x | Frequency: {item['raw_frequency_pct']}% [{item['numerator']}/{item['denominator']}])\n")
