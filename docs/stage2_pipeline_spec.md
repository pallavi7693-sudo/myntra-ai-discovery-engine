# Technical Specification: Stage 2 Multi-Dimensional Pipeline (Validated & Corrected)

> **Pipeline Target:** Multi-Dimensional Behavioral Signal Extraction & Evidence-Grounded Analytics  
> **Output Dataset:** `Processed Data/myntra_multidimensional_enriched.json`  
> **Compliance:** 100% adherence to `docs/edge_case.md` and user validation requirements.

---

## 1. Primary Intent Immutability Rule
- The column `primary_intent` from `reddit_myntra_labeled.csv` (634 rows) is strictly immutable. It must be read directly and written identically to the output JSON without modification or re-classification.

---

## 2. Updated Multi-Dimensional Taxonomy Schema

Every processed record in `Processed Data/myntra_multidimensional_enriched.json` will conform to the following schema:

```json
{
  "record_id": "string",
  "source_file": "string",
  "source_channel": "reddit | playstore | appstore | youtube",
  "platform_brand": "myntra | ajio | nykaa",
  "raw_text": "string",
  "processed_text_with_context": "string",
  "primary_intent": "original_intent_preserved_unmodified",
  "user_segment": "price_sensitive | fit_hesitant | research_heavy | wishlist_heavy | general_shopper",
  "analytical_dimensions": {
    "user_behavior": ["wishlist", "purchase_intent", "purchase_completed", "purchase_postponed", "product_comparison", "recommendation_seeking", "product_research", "bookmarking"],
    "purchase_stage": "discovery | consideration | shortlist | purchase_intent | post_purchase",
    "purchase_status": "purchased | likely_to_purchase | postponed | abandoned | uncertain",
    "purchase_barriers": ["price", "size_uncertainty", "fit_uncertainty", "quality_uncertainty", "lack_of_reviews", "return_concern", "delivery_concern", "availability", "trust", "styling_uncertainty", "occasion_uncertainty"],
    "information_needs": ["reviews", "size_information", "fit_information", "styling", "quality", "price_history", "discount_information", "availability", "alternatives", "social_validation", "product_comparison"],
    "decision_factors": ["price", "fit", "size", "style", "occasion", "quality", "reviews", "brand", "social_validation", "availability"],
    "opportunity_area": ["better_size_guidance", "better_fit_information", "stronger_social_proof", "better_price_visibility", "better_product_comparison", "better_styling_guidance", "better_quality_information", "better_return_information"]
  },
  "evidence": {
    "user_behavior": [
      { "label": "wishlist", "text_quote": "added this dress to my wishlist" }
    ],
    "purchase_barriers": [
      { "label": "price", "text_quote": "waiting for the price to drop" }
    ],
    "information_needs": [],
    "decision_factors": [
      { "label": "size", "text_quote": "unsure if medium will fit" }
    ],
    "opportunity_area": [
      { "label": "better_size_guidance", "text_quote": "wish they provided exact sleeve measurements" }
    ]
  }
}
```

---

## 3. Strict Schema Rules & Edge-Case Safeguards

### Rule 1: Strict Single Enum for `purchase_status`
Every record MUST contain **EXACTLY ONE** value from the strict enum set:
- `purchased`: Purchase completed.
- `likely_to_purchase`: Active purchase intent without expressed hesitation.
- `postponed`: Purchase delayed due to price, stock, size, or review waiting.
- `abandoned`: Order canceled, returned, or purchase rejected.
- `uncertain`: Consideration state with unresolved friction or exploratory inquiry.

### Rule 2: Evidence-Grounded `opportunity_area`
- `opportunity_area` MUST NEVER be inferred automatically from a barrier alone.
- An opportunity tag is assigned **ONLY** when explicit supporting text exists in the conversation (e.g. user requesting clearer size charts, price history, or honest reviews). Every opportunity tag MUST have a corresponding quote in `evidence.opportunity_area`.

### Rule 3: Verbatim Evidence Traceability (`evidence` field)
- Every dimension array tag must be linked to its exact supporting verbatim quote in `evidence`.
- Format: `{"label": "<category_name>", "text_quote": "<supporting_text_snippet>"}`.

### Rule 4: Thread Context Inheritance Safeguard (Edge Case 3.2)
- Prepend parent post title as `[Context: {parent_title}]` to Reddit comments.
- **Child Override Safeguard**: Evaluate comment text first. If the comment contains strong explicit complaints or queries (e.g., `cancellation_refund`, `delivery_delay`), the comment text takes precedence and parent topic attribution is suppressed.

### Rule 5: Negation Window Safeguard (Edge Case 5.1)
- Inspect a 4-word preceding window before any pattern keyword for negation tokens (`not`, `don't`, `never`, `no`, `wouldn't`, `cannot`). If negation is present, suppress tag assignment.

---

## 4. Denominator Scoping & Anti-Double-Counting Rules

1. **Exact Denominator Reporting**: All quantitative statistics must explicitly state:
   - `numerator`: Number of unique matching records.
   - `denominator`: Total population records in the specified segment.
   - `population_name`: Name of the sub-population.
   - Example: `"31.7% of purchase-hesitation conversations (140/450) mentioned price."`
2. **Record-Level Deduplication**: A single record contributes at most **1 count** to any given metric category, preventing double-counting if keywords appear multiple times in the same text.
