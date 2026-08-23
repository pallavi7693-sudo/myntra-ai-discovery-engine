import os
import json
import numpy as np
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DOMAIN_KEYWORDS = [
    "myntra", "ajio", "nykaa", "wishlist", "item", "items", "product", "products",
    "price", "cost", "expensive", "cheap", "discount", "sale", "coupon", "myncash",
    "size", "sizing", "fit", "fitting", "quality", "fabric", "material", "return",
    "refund", "exchange", "delivery", "shipping", "order", "buy", "purchase", "bought",
    "cart", "review", "rating", "outfit", "style", "fashion", "brand", "clothing",
    "apparel", "dress", "shirt", "shoe", "shoes", "delay", "wait", "postpone", "hesitat",
    "barrier", "friction", "recommend", "compare", "shortlist", "bookmark", "save", "saving",
    "eors", "bff", "ekart", "haul", "try on", "reddit", "youtube", "app", "store",
    "unmet", "need", "needs", "gap", "emerge", "conversation", "conversations",
    "segment", "segments", "differ", "differs", "shopper", "shoppers",
    "behavior", "behaviors", "behaviour", "behaviours"
]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class HybridRetrievalEngine:
    def __init__(self, index_path="Processed Data/vector_index.json", matrix_path="Processed Data/vector_embeddings.npz"):
        if not os.path.isabs(index_path):
            index_path = os.path.join(BASE_DIR, index_path)
        if not os.path.isabs(matrix_path):
            matrix_path = os.path.join(BASE_DIR, matrix_path)
            
        if not os.path.exists(index_path) or not os.path.exists(matrix_path):
            raise FileNotFoundError(f"Vector index files not found at {index_path} or {matrix_path}.")
            
        with open(index_path, "r", encoding="utf-8") as f:
            self.index_data = json.load(f)
            
        self.metadata_store = self.index_data["metadata_store"]
        self.total_dataset_size = len(self.metadata_store)
        self.tfidf_matrix = sparse.load_npz(matrix_path)
        
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            sublinear_tf=True,
            max_features=5000,
            vocabulary={feat: idx for idx, feat in enumerate(self.index_data["feature_names"])},
            stop_words='english'
        )
        self.vectorizer.idf_ = np.array(self.index_data["idf_weights"])
        
    def compile_query_filters(self, user_query):
        """Safeguard 4: Traceable Query Filter Compiler with Myntra Friction Rule."""
        q_lower = user_query.lower()
        filters = {"platform_brand": "myntra"} # Strictly Myntra for evidence quotes per user directive
        
        if "size" in q_lower:
            filters["purchase_barriers"] = "size_uncertainty"
        elif "fit" in q_lower:
            filters["purchase_barriers"] = "fit_uncertainty"
        elif "price" in q_lower or "cost" in q_lower or "expensive" in q_lower:
            filters["purchase_barriers"] = "price"
        elif "quality" in q_lower or "fabric" in q_lower:
            filters["purchase_barriers"] = "quality_uncertainty"
        elif "review" in q_lower:
            filters["purchase_barriers"] = "lack_of_reviews"
        elif "return" in q_lower or "refund" in q_lower:
            filters["purchase_barriers"] = "return_concern"
        elif "delivery" in q_lower or "delay" in q_lower or "shipping" in q_lower:
            filters["purchase_barriers"] = "delivery_concern"
            
        if "postpone" in q_lower or "wait" in q_lower or "delay" in q_lower or "prevent" in q_lower or "friction" in q_lower or "barrier" in q_lower:
            filters["purchase_status"] = "postponed"
            
        return filters

    def filter_eligible_population(self, applied_filters):
        if not applied_filters:
            return self.metadata_store
            
        eligible_records = []
        for r in self.metadata_store:
            dims = r.get("analytical_dimensions", {})
            match = True
            
            for key, val in applied_filters.items():
                if key in ["is_segment_query", "is_ted_query"]:
                    continue
                elif key == "purchase_barriers":
                    if val not in dims.get("purchase_barriers", []):
                        match = False
                        break
                elif key == "purchase_status":
                    if dims.get("purchase_status") != val:
                        match = False
                        break
                elif key == "platform_brand":
                    if r.get("platform_brand") != val:
                        match = False
                        break
                elif key == "source_channel":
                    if r.get("source_channel") != val:
                        match = False
                        break
                elif key == "user_behavior":
                    if val not in dims.get("user_behavior", []):
                        match = False
                        break
                        
            if match:
                eligible_records.append(r)
                
        return eligible_records

    def get_topic_keywords_for_question(self, query_text):
        """Maps query text to relevant evidence topic keywords."""
        q_lower = query_text.lower()
        
        # Check if query is related to domain
        if not any(kw in q_lower for kw in DOMAIN_KEYWORDS):
            return []
            
        if any(kw in q_lower for kw in ["save", "saving", "bookmark", "bookmarking", "wishlist", "only save", "why do users add", "add to"]):
            return ["wishlist", "saved", "price drop", "sale", "discount", "later", "buy later", "outfit", "bookmark"]
        elif "prevent" in q_lower or "prevents" in q_lower or "barrier" in q_lower or "friction" in q_lower:
            return ["price", "expensive", "quality", "fabric", "delivery", "return", "refund", "size"]
        elif "uncertainties" in q_lower or "uncertainty" in q_lower or "doubt" in q_lower:
            return ["fabric", "quality", "material", "size", "fit", "sizing", "return fee", "exchange"]
        elif "postpone" in q_lower or "delay" in q_lower or "wait" in q_lower:
            return ["wait", "waiting", "sale", "discount", "coupon", "delivery", "late", "shipping"]
        elif "compare" in q_lower or "shortlist" in q_lower or "versus" in q_lower or "vs" in q_lower:
            return ["compare", "vs", "versus", "quality", "fabric", "price", "better than", "material"]
        elif "outside" in q_lower or "seek" in q_lower or "reddit" in q_lower or "youtube" in q_lower:
            return ["reddit", "youtube", "review", "reviews", "fabric", "try on", "haul", "tracker"]
        elif "fit" in q_lower or "size" in q_lower or "role" in q_lower:
            return ["price", "cost", "quality", "fabric", "size", "fit", "review", "rating"]
        elif "segment" in q_lower or "differ" in q_lower or "shopper" in q_lower:
            return ["price", "discount", "sale", "size", "fit", "review", "quality", "material"]
        elif "unmet" in q_lower or "needs" in q_lower or "need" in q_lower:
            return ["price drop", "alert", "fabric", "photo", "size", "exchange", "return", "fee"]
        else:
            return ["price", "quality", "fabric", "size", "fit", "delivery", "return", "wishlist", "save"]

    def execute_hybrid_retrieval(self, query_text, top_k=4, user_filters=None, min_similarity_threshold=0.05):
        """Executes Hybrid Retrieval strictly over Myntra Evidence Records."""
        applied_filters = self.compile_query_filters(query_text) if user_filters is None else user_filters
        
        # Enforce Myntra-only for evidence quotes
        applied_filters["platform_brand"] = "myntra"
        
        eligible_records = self.filter_eligible_population(applied_filters)
        eligible_pop_size = len(eligible_records)
        
        myntra_hesitations = [
            r for r in self.metadata_store
            if r.get("platform_brand") == "myntra" and (
                len(r.get("analytical_dimensions", {}).get("purchase_barriers", [])) > 0 or
                r.get("analytical_dimensions", {}).get("purchase_status") == "postponed"
            )
        ]
        ref_denominator = len(myntra_hesitations)
        pop_name = "Myntra purchase-hesitation conversations"

        barrier_key = applied_filters.get("purchase_barriers")
        if barrier_key:
            barrier_count = sum(1 for r in myntra_hesitations if barrier_key in r.get("analytical_dimensions", {}).get("purchase_barriers", []))
            pct = round((barrier_count / ref_denominator * 100), 1) if ref_denominator > 0 else 0.0
            formatted_txt = f"{pct}% of {pop_name} ({barrier_count}/{ref_denominator}) mentioned {barrier_key}."
        else:
            barrier_count = eligible_pop_size
            pct = 100.0
            formatted_txt = f"{eligible_pop_size} relevant Myntra consumer records evaluated across multi-channel touchpoints."
            
        quantification_result = {
            "target_filter": applied_filters,
            "numerator": barrier_count,
            "denominator": ref_denominator,
            "percentage": pct,
            "population_scope": pop_name,
            "applied_filters": applied_filters,
            "formatted_text": formatted_txt
        }

        required_keywords = self.get_topic_keywords_for_question(query_text)
        
        # If query is completely off-topic (no required keywords and no domain terms), return empty evidence
        if not required_keywords and not any(kw in query_text.lower() for kw in DOMAIN_KEYWORDS):
            return {
                "query": query_text,
                "population_scope": {
                    "applied_filters": applied_filters,
                    "eligible_population_size": 0,
                    "reference_denominator_size": ref_denominator,
                    "total_dataset_size": self.total_dataset_size,
                    "retrieved_evidence_records_count": 0
                },
                "quantification": quantification_result,
                "retrieved_evidence": []
            }

        search_prompt = f"{query_text} {' '.join(required_keywords)}".strip()
        query_vec = self.vectorizer.transform([search_prompt])
        
        eligible_indices = [r["vector_id"] for r in eligible_records]
        retrieved_evidence = []
        
        if eligible_indices:
            sub_matrix = self.tfidf_matrix[eligible_indices]
            sim_scores = cosine_similarity(query_vec, sub_matrix).flatten()
            
            sorted_cand_indices = np.argsort(sim_scores)[::-1]
            seen_quote_keys = set()
            
            for cand_idx in sorted_cand_indices:
                if len(retrieved_evidence) >= top_k:
                    break
                    
                score = float(round(sim_scores[cand_idx], 4))
                if score < min_similarity_threshold:
                    continue
                    
                record = eligible_records[cand_idx]
                
                # STRICT USER RULE: NEVER RETURN AJIO OR NYKAA QUOTES
                if record.get("platform_brand") != "myntra":
                    continue
                    
                # STRICT USER RULE: EXCLUDE EVIDENCE MARKS AS 'OTHER'
                if str(record.get("primary_intent", "")).lower() == "other":
                    continue
                    
                raw_txt = record["raw_text"].strip()
                raw_txt_lower = raw_txt.lower()
                
                # Exclude generic UI / App feedback
                if any(term in raw_txt_lower for term in ["interface", "user friendly", "flexibility", "bug", "app crash", "newer one"]):
                    continue
                    
                # Must contain topic keyword matching the answer if required_keywords is present
                if required_keywords and not any(kw in raw_txt_lower for kw in required_keywords):
                    continue
                    
                if len(raw_txt) < 25:
                    continue
                    
                # ENTIRE RELATED CONVERSATION CONTEXT
                full_conversation = record.get("processed_text_with_context", raw_txt)
                if not full_conversation or len(full_conversation.strip()) < 10:
                    full_conversation = raw_txt
                    
                norm_key = full_conversation.lower()[:60]
                if norm_key in seen_quote_keys:
                    continue
                seen_quote_keys.add(norm_key)
                
                retrieved_evidence.append({
                    "evidence_rank": len(retrieved_evidence) + 1,
                    "record_id": record["record_id"],
                    "source_file": record["source_file"],
                    "source_channel": record["source_channel"],
                    "platform_brand": "myntra",
                    "similarity_score": score,
                    "primary_intent": record["primary_intent"],
                    "user_segment": record.get("user_segment", "general_shopper"),
                    "sentiment_analysis": record.get("sentiment_analysis", {}),
                    "verbatim_text": raw_txt[:300],
                    "evidence_quote": full_conversation[:500]
                })
                
        return {
            "query": query_text,
            "population_scope": {
                "applied_filters": applied_filters,
                "eligible_population_size": eligible_pop_size,
                "reference_denominator_size": ref_denominator,
                "total_dataset_size": self.total_dataset_size,
                "retrieved_evidence_records_count": len(retrieved_evidence)
            },
            "quantification": quantification_result,
            "retrieved_evidence": retrieved_evidence
        }

if __name__ == "__main__":
    engine = HybridRetrievalEngine()
    res = engine.execute_hybrid_retrieval("Why do users add fashion products to their wishlist?", top_k=4)
    print("\nMYNTRA-ONLY EVIDENCE QUOTES TEST:")
    for ev in res["retrieved_evidence"]:
        print(f"  • Brand: {ev['platform_brand'].upper()} | Channel: {ev['source_channel'].upper()} | Quote: \"{ev['evidence_quote'][:60]}...\"")
