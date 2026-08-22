# Technical Specification: Stage 3 Hybrid Retrieval & Grounding Engine

> **Target Module:** Vector Indexing, Hybrid Semantic Retrieval & Evidence Grounding  
> **Input Dataset:** `Processed Data/myntra_multidimensional_enriched.json` (5,706 records)  
> **Output Artifacts:** `Processed Data/vector_index.parquet`, `Processed Data/vector_embeddings.npy`, `Scripts/hybrid_retrieval_engine.py`  
> **Compliance:** Strict compliance with the 8 Explicit Stage 3 Safeguards.

---

## 1. The 8 Mandatory Stage 3 Safeguards

```
[User Query] ──► [Query Filter Compiler] ──► [1. Filter Full Dataset (Eligible Population = Denominator)]
                                        ├──► [2. Compute Scoped Quantification Over Full Eligible Population]
                                        └──► [3. Vector Semantic Search on Filtered Subset ──► Top-K Evidence Display Only]
```

1. **Top-K Display Rule:** Top-K semantic retrieval (e.g. Top 5 quotes) is **ONLY** used for evidence display and quote grounding. Top-K must **NEVER** be used as the denominator for business metrics or percentages.
2. **Full Population Quantification Rule:** Quantification operates over 100% of the eligible population matching the metadata filter scope in the dataset, not just the Top-K retrieved snippets.
3. **Exposed Metric Schema:** Every quantitative result must expose:
   - `numerator`: Exact count of matching records.
   - `denominator`: Total count of eligible records matching the scope.
   - `population_scope`: Name and description of the population segment.
   - `applied_filters`: Key-value map of explicit metadata filters applied.
4. **Filter Traceability Rule:** `compile_query_filters()` must map filters directly to explicit terms in the user query or documented semantic rules. Silent/invented filters are strictly prohibited.
5. **No Independent Opportunity Declaration:** Stage 3 retrieves grounded evidence only. It must NOT independently re-rank or declare final business opportunities.
6. **Data Immutability:** Preserves `primary_intent` (634 rows) and all Stage 2 `analytical_dimensions` and `evidence` fields without modification.
7. **Retrieval Payload `population_scope` Object:** Every retrieval output payload must expose:
   ```json
   "population_scope": {
     "applied_filters": { "purchase_status": "postponed" },
     "eligible_population_size": 450,
     "retrieved_evidence_records_count": 5
   }
   ```
8. **Verbatim & Record ID Traceability:** Every evidence quote must include `record_id`, `source_file`, `source_channel`, `platform_brand`, and verbatim text.

---

## 2. Structured Retrieval Output Schema

```json
{
  "query": "Why do users postpone wishlisted products due to size uncertainty?",
  "population_scope": {
    "applied_filters": {
      "purchase_status": "postponed",
      "purchase_barriers": ["size_uncertainty"]
    },
    "eligible_population_size": 59,
    "total_dataset_size": 5706,
    "retrieved_evidence_records_count": 5
  },
  "quantification": {
    "metric_title": "size_uncertainty",
    "numerator": 59,
    "denominator": 1202,
    "percentage": 4.9,
    "population_name": "purchase-hesitation conversations",
    "applied_filters": { "purchase_barriers": ["size_uncertainty"] },
    "formatted_text": "4.9% of purchase-hesitation conversations (59/1202) mentioned size_uncertainty."
  },
  "retrieved_evidence": [
    {
      "rank": 1,
      "record_id": "reddit_myntra_labeled.csv_42",
      "source_file": "reddit_myntra_labeled.csv",
      "source_channel": "reddit",
      "platform_brand": "myntra",
      "similarity_score": 0.89,
      "primary_intent": "wishlist",
      "verbatim_text": "I love this dress on Myntra but I'm holding off buying because size M might be too short.",
      "evidence_quote": "holding off buying because size M might be too short"
    }
  ]
}
```
