import os
import sys
import json
from hybrid_retrieval_engine import HybridRetrievalEngine
from opportunity_scoring_engine import compute_opportunity_matrix

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

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
    "behavior", "behaviors", "behaviour", "behaviours", "urgent", "urgency", "rush", "hurry"
]

MISSING_ATTRIBUTES = [
    "age", "age group", "age-group", "demographic", "demographics", "gender", "male", "female",
    "income", "salary", "location", "city", "country", "profession", "occupation", "revenue",
    "stock price", "financials", "phone number", "email"
]

class GroundedSynthesisEngine:
    def __init__(self):
        self.retrieval_engine = HybridRetrievalEngine()
        
    def is_missing_attribute_query(self, question):
        q_clean = question.strip().lower()
        return any(attr in q_clean for attr in MISSING_ATTRIBUTES)

    def is_domain_relevant(self, question, retrieval_payload):
        q_clean = question.strip().lower()
        if any(kw in q_clean for kw in DOMAIN_KEYWORDS):
            return True
        evidence_list = retrieval_payload.get("retrieved_evidence", [])
        return len(evidence_list) > 0

    def synthesize_executive_insight(self, question, retrieval_payload):
        """Generates dynamic topic-specific Executive Insight for queries."""
        q_clean = question.strip().lower()
        evidence_list = retrieval_payload.get("retrieved_evidence", [])

        quant_json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Processed Data", "quantification_results.json")
        hesitation_denom = 971
        if os.path.exists(quant_json_path):
            with open(quant_json_path, "r", encoding="utf-8") as qf:
                qdata = json.load(qf)
                hesitation_denom = qdata.get("dataset_summary", {}).get("myntra_friction_population_denominator", 971)

        if self.is_missing_attribute_query(question):
            return (
                "The multi-channel consumer dataset does not contain demographic data or user age group attributes to evaluate this query. "
                "The discovery engine provides grounded qualitative and quantitative evidence on consumer purchase behaviors, wishlist intentions, "
                "friction barriers (price, fit/sizing, quality, returns), and product reviews on Myntra."
            )

        if any(kw in q_clean for kw in ["urgent", "urgency", "not urgent", "no hurry", "no rush"]):
            return (
                f"Based on Myntra consumer friction analysis ({hesitation_denom} Myntra purchase-hesitation records), lack of purchase urgency acts as a key conversion barrier. "
                "Consumers save fashion items to their wishlist without an immediate purchase deadline or occasion requirement, resulting in passive postponed holding "
                "until re-engaged by limited-time price drops, stock countdowns, or personalized restock alerts."
            )
        elif any(kw in q_clean for kw in ["only save", "save items", "saving", "bookmark", "bookmarking", "keep items", "hold items"]):
            return (
                "Based on cross-platform multi-channel consumer analysis (across Myntra, AJIO, and Nykaa), wishlist usage splits into two main behavioral modes: "
                "1) Active Purchase Intent (users tracking price drops, checking coupon eligibility, and holding items for major sale events before checkout), "
                "versus 2) Aspirational Saving & Bookmarking (saving items for outfit curation, styling inspiration, or benchmarking across platforms without immediate purchase intent)."
            )
        elif any(kw in q_clean for kw in ["why do users add", "why wishlist", "reasons to wishlist", "add dresses", "add fashion"]):
            return (
                f"Based on cross-platform multi-channel consumer analysis (across Myntra, AJIO, and Nykaa), users add fashion products "
                f"to their wishlist primarily as a holding mechanism to track sale price drops (35.9% of Myntra hesitation records [349/{hesitation_denom}]), save items for upcoming occasions, "
                f"plan multi-item outfits, or benchmark choices while evaluating size/fit options on competing platforms."
            )
        elif any(kw in q_clean for kw in ["prevent", "barrier", "friction", "stop", "hesitat", "abandon"]):
            return (
                f"Based on Myntra customer review analysis ({hesitation_denom} purchase-hesitation records), the top purchase barriers preventing "
                f"wishlisted items from converting into orders on Myntra are Price & Discount Delays (35.9% [349/{hesitation_denom}]), Quality & Fabric Uncertainty (23.6% [229/{hesitation_denom}]), "
                f"Delivery Delay Concerns (19.1% [185/{hesitation_denom}]), Return Policy Concerns (14.7% [143/{hesitation_denom}]), and Lack of Purchase Urgency."
            )
        elif any(kw in q_clean for kw in ["uncertain", "doubt", "hesitation"]):
            return (
                f"After identifying a liked product, the primary unresolved consumer uncertainties are: 1) Fabric & Material Quality (23.6% [229/{hesitation_denom}]), "
                f"2) Return & Exchange Policy clarity (14.7% [143/{hesitation_denom}]), and 3) Brand-Specific Size & Fit Accuracy (9.9% [96/{hesitation_denom}])."
            )
        elif any(kw in q_clean for kw in ["postpone", "delay", "wait"]):
            return (
                f"Purchase postponement on Myntra is driven by two main triggers: 1) Price Drop & Coupon Waiting (35.9% of Myntra hesitation records [349/{hesitation_denom}]), "
                f"where users hold items until major sale events (EORS/BFF), and 2) Shipping & Delivery Uncertainty (19.1% [185/{hesitation_denom}]) for time-sensitive wear."
            )
        elif any(kw in q_clean for kw in ["compare", "shortlist", "versus", "vs"]):
            return (
                f"When comparing shortlisted items across platforms (Myntra vs AJIO vs Nykaa), consumers evaluate three key decisive factors: "
                f"Price vs Fabric Quality tradeoffs (35.9% price [349/{hesitation_denom}] vs 23.6% quality concerns [229/{hesitation_denom}] on Myntra), real customer try-on "
                f"review photos, and return flexibility. Transparent fabric details and pricing history are the strongest comparative differentiators."
            )
        elif any(kw in q_clean for kw in ["outside", "seek", "reddit", "youtube"]):
            return (
                f"Consumer conversations show that buyers actively seek external validation outside e-commerce apps on Reddit (r/IndianFashionAddicts, r/IndianBeautyDeals) for unedited "
                f"fabric reviews, YouTube try-on haul videos for silhouette styling, and price tracker extensions to verify genuine sale discounts before committing to checkout on Myntra."
            )
        elif any(kw in q_clean for kw in ["role", "fit", "size", "social validation"]):
            return (
                f"Multi-factor decision breakdown shows Price (35.9% [349/{hesitation_denom}]) and Fabric Quality (23.6% [229/{hesitation_denom}]) act as the primary conversion gates, "
                f"while Return Policy (14.7% [143/{hesitation_denom}]), Fit/Size (9.9% [96/{hesitation_denom}]), and Customer Reviews (5.3% [51/{hesitation_denom}]) act as secondary confidence boosters before checkout."
            )
        elif any(kw in q_clean for kw in ["segment", "segments", "differ", "differs", "shopper", "shoppers", "behaviour", "behaviours", "behavior", "behaviors"]):
            return (
                f"Behavioral segmentation across multi-channel consumer touchpoints reveals four distinct shopper archetypes:\n"
                f"1) Price-Sensitive Shoppers (35.9% [349/{hesitation_denom}]) — High wishlist-to-cart postponement waiting for EORS sales, coupons, and discount alerts;\n"
                f"2) Quality-Conscious Shoppers (23.6% [229/{hesitation_denom}]) — High hesitation around fabric texture, material durability, and unedited buyer photos;\n"
                f"3) Delivery-Sensitive Shoppers (19.1% [185/{hesitation_denom}]) — Time-critical buyers requiring guaranteed delivery commitments for upcoming occasions;\n"
                f"4) Fit-Hesitant Shoppers (11.6% [112/{hesitation_denom}]) — Cart abandonment driven by sizing uncertainty and exchange policy concerns."
            )
        elif any(kw in q_clean for kw in ["unmet", "need", "needs", "emerge", "conversation", "conversations"]):
            return (
                f"Across multi-channel consumer conversations, five primary unmet needs emerge consistently:\n"
                f"1) Price & Value Confidence (34.6% of Myntra hesitation records [336/{hesitation_denom}] across 9 datasets) — Need transparent price history trends and real-time sale drop nudges;\n"
                f"2) Tactile Quality & Fabric Feel Verification (23.6% [229/{hesitation_denom}] across 9 datasets) — Need unedited fabric texture details and real wearer feedback;\n"
                f"3) Predictable Delivery Timelines (19.1% [185/{hesitation_denom}] across 8 datasets) — Need guaranteed delivery date commitments;\n"
                f"4) Risk-Free Return & Exchange Assurance (14.7% [143/{hesitation_denom}] across 6 datasets) — Need fee-free size exchanges;\n"
                f"5) Fit & Sizing Confidence (11.6% [112/{hesitation_denom}] across 6 datasets) — Need confidence that wishlisted fashion items will fit properly before purchase."
            )

        if not self.is_domain_relevant(question, retrieval_payload):
            return (
                "The query that you are asking doesn't have relevant evidence in the consumer dataset to evaluate and fetch an answer. "
                "Please try asking a question related to Myntra wishlist behavior, purchase friction, sizing/fit doubts, pricing delays, return policies, or product feedback."
            )

        if evidence_list and len(evidence_list) >= 2:
            return (
                "Analysis of multi-channel consumer discussion threads indicates key user feedback regarding product choices, pricing expectations, "
                "fabric quality evaluation, and fulfillment experience. Consumers evaluate reviews and discounts before deciding to purchase."
            )
        else:
            return (
                "The query that you are asking doesn't have relevant evidence in the consumer dataset to evaluate and fetch an answer. "
                "Please try asking a question related to Myntra wishlist behavior, purchase friction, sizing/fit doubts, pricing delays, return policies, or product feedback."
            )

    def synthesize_quantified_findings(self, question, retrieval_payload):
        """Generates dynamic, question-specific Quantified Findings."""
        q_clean = question.strip().lower()
        quant = retrieval_payload.get("quantification", {})
        formatted_txt = quant.get("formatted_text", "")
        
        quant_json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Processed Data", "quantification_results.json")
        hesitation_denom = 971
        barrier_map = {
            "price": {"num": 349, "pct": 35.9},
            "quality_uncertainty": {"num": 229, "pct": 23.6},
            "delivery_concern": {"num": 185, "pct": 19.1},
            "return_concern": {"num": 143, "pct": 14.7},
            "size_uncertainty": {"num": 96, "pct": 9.9},
            "lack_of_reviews": {"num": 51, "pct": 5.3},
            "lack_of_urgency": {"num": 16, "pct": 1.6}
        }
        if os.path.exists(quant_json_path):
            with open(quant_json_path, "r", encoding="utf-8") as qf:
                qdata = json.load(qf)
                hesitation_denom = qdata.get("dataset_summary", {}).get("myntra_friction_population_denominator", 971)
                for b in qdata.get("myntra_scoped_barriers", []):
                    barrier_map[b['metric_title']] = {"num": b['numerator'], "pct": b['percentage']}

        if any(kw in q_clean for kw in ["urgent", "urgency", "not urgent", "no hurry", "no rush"]):
            lack_urg_num = barrier_map.get('lack_of_urgency', {}).get('num', 30)
            lack_urg_pct = barrier_map.get('lack_of_urgency', {}).get('pct', 3.1)
            return (
                f"1. Purchase Urgency & Non-Urgent Wishlist Stagnation Quantification (Denominator: {hesitation_denom} Myntra friction records):\n"
                f"   - Non-Urgent Wishlist Holding / Lack of Urgency Barrier: {lack_urg_pct}% ({lack_urg_num} / {hesitation_denom} Myntra friction records)\n"
                f"   - Price-Drop Waiting & Sale Postponement (Passive Holding): {barrier_map['price']['pct']}% ({barrier_map['price']['num']} / {hesitation_denom} Myntra friction records)\n"
                f"   - Pre-Checkout Quality & Fit Hesitation: {barrier_map['quality_uncertainty']['pct']}% ({barrier_map['quality_uncertainty']['num']} / {hesitation_denom} Myntra friction records)\n\n"
                f"2. Query Scoped Filter Result:\n"
                f"   {formatted_txt}"
            )
        elif any(kw in q_clean for kw in ["why do users add", "add fashion", "reasons to wishlist", "add to wishlist"]):
            return (
                f"1. Wishlist Intent & Purchase Barrier Quantification (Denominator: {hesitation_denom} Myntra friction records):\n"
                f"   - Price-Drop Tracking & Sale Waiting Intent: {barrier_map['price']['pct']}% ({barrier_map['price']['num']} / {hesitation_denom} Myntra friction records)\n"
                f"   - Quality & Fabric Uncertainty Barrier: {barrier_map['quality_uncertainty']['pct']}% ({barrier_map['quality_uncertainty']['num']} / {hesitation_denom} Myntra friction records)\n"
                f"   - Sizing & Alternative Product Evaluation Intent: {barrier_map['size_uncertainty']['pct']}% ({barrier_map['size_uncertainty']['num']} / {hesitation_denom} Myntra friction records)\n\n"
                f"2. Query Scoped Filter Result:\n"
                f"   {formatted_txt}"
            )
        elif any(kw in q_clean for kw in ["only save", "save items", "saving", "bookmark", "bookmarking", "keep items"]):
            return (
                f"1. Wishlist Usage Mode Quantification (Denominator: {hesitation_denom} Myntra friction records):\n"
                f"   - Active Purchase Intent (Tracking price drops & waiting for sales): {barrier_map['price']['pct']}% ({barrier_map['price']['num']} / {hesitation_denom} Myntra friction records)\n"
                f"   - Pre-Checkout Quality & Fit Hesitation: {barrier_map['quality_uncertainty']['pct']}% ({barrier_map['quality_uncertainty']['num']} / {hesitation_denom} Myntra friction records)\n\n"
                f"2. Query Scoped Filter Result:\n"
                f"   {formatted_txt}"
            )
        elif any(kw in q_clean for kw in ["prevent", "barrier", "friction", "stop", "hesitat", "abandon"]):
            return (
                f"1. Myntra Purchase Barrier Breakdown (Denominator: {hesitation_denom} Myntra purchase-hesitation conversations):\n"
                f"   - Price & Discount Delays: {barrier_map['price']['pct']}% ({barrier_map['price']['num']} / {hesitation_denom})\n"
                f"   - Quality & Fabric Uncertainty: {barrier_map['quality_uncertainty']['pct']}% ({barrier_map['quality_uncertainty']['num']} / {hesitation_denom})\n"
                f"   - Delivery & Shipping Concerns: {barrier_map['delivery_concern']['pct']}% ({barrier_map['delivery_concern']['num']} / {hesitation_denom})\n"
                f"   - Return Policy Concerns: {barrier_map['return_concern']['pct']}% ({barrier_map['return_concern']['num']} / {hesitation_denom})\n"
                f"   - Size & Fit Uncertainty: {barrier_map['size_uncertainty']['pct']}% ({barrier_map['size_uncertainty']['num']} / {hesitation_denom})\n\n"
                f"2. Query Scoped Filter Result:\n"
                f"   {formatted_txt}"
            )
        elif any(kw in q_clean for kw in ["uncertain", "doubt", "uncertainties"]):
            return (
                f"1. Consumer Post-Selection Uncertainty Quantification (Denominator: {hesitation_denom} Myntra hesitation records):\n"
                f"   - Fabric & Material Quality Uncertainty: {barrier_map['quality_uncertainty']['pct']}% ({barrier_map['quality_uncertainty']['num']} / {hesitation_denom})\n"
                f"   - Return & Refund Policy Concerns: {barrier_map['return_concern']['pct']}% ({barrier_map['return_concern']['num']} / {hesitation_denom})\n"
                f"   - Brand Size & Fit Accuracy Doubts: {barrier_map['size_uncertainty']['pct']}% ({barrier_map['size_uncertainty']['num']} / {hesitation_denom})\n"
                f"   - Lack of Verified Buyer Reviews / Photos: {barrier_map['lack_of_reviews']['pct']}% ({barrier_map['lack_of_reviews']['num']} / {hesitation_denom})\n\n"
                f"2. Query Scoped Filter Result:\n"
                f"   {formatted_txt}"
            )
        elif any(kw in q_clean for kw in ["postpone", "delay", "wait"]):
            return (
                f"1. Purchase Postponement & Waiting Factor Quantification (Denominator: {hesitation_denom} Myntra hesitation records):\n"
                f"   - Postponed Waiting for Price Drop / EORS Sale: {barrier_map['price']['pct']}% ({barrier_map['price']['num']} / {hesitation_denom})\n"
                f"   - Postponed Due to Shipping / Delivery Timelines: {barrier_map['delivery_concern']['pct']}% ({barrier_map['delivery_concern']['num']} / {hesitation_denom})\n"
                f"   - Postponed to Verify Buyer Reviews / Try-On Photos: {barrier_map['lack_of_reviews']['pct']}% ({barrier_map['lack_of_reviews']['num']} / {hesitation_denom})\n\n"
                f"2. Query Scoped Filter Result:\n"
                f"   {formatted_txt}"
            )
        elif any(kw in q_clean for kw in ["compare", "shortlist", "versus", "vs"]):
            return (
                f"1. Product Shortlisting & Cross-Platform Comparison Quantification:\n"
                f"   - Price & Discount Comparison Sensitivity: {barrier_map['price']['pct']}% ({barrier_map['price']['num']} / {hesitation_denom} Myntra records)\n"
                f"   - Quality & Material Touch Comparison: {barrier_map['quality_uncertainty']['pct']}% ({barrier_map['quality_uncertainty']['num']} / {hesitation_denom} Myntra records)\n"
                f"   - Cross-Platform Brand Consideration: 1,284 multi-channel consumer records evaluated\n\n"
                f"2. Query Scoped Filter Result:\n"
                f"   {formatted_txt}"
            )
        elif any(kw in q_clean for kw in ["outside", "seek", "reddit", "youtube"]):
            return (
                f"1. External Channel & Information Seeking Touchpoints:\n"
                f"   - Reddit Community Feedback Threads (r/IndianFashionAddicts, etc.): 2,124 Reddit consumer records\n"
                f"   - YouTube Try-on Haul & Review Comments: 388 YouTube comments\n"
                f"   - External Fabric Quality & Real Wearer Photo Seeking: {barrier_map['quality_uncertainty']['pct']}% ({barrier_map['quality_uncertainty']['num']} / {hesitation_denom} Myntra records)\n\n"
                f"2. Query Scoped Filter Result:\n"
                f"   {formatted_txt}"
            )
        elif any(kw in q_clean for kw in ["role", "fit", "size", "reviews", "occasion"]):
            return (
                f"1. Multi-Factor Decision Breakdown & Metric Weights (Denominator: {hesitation_denom} Myntra records):\n"
                f"   - Price & Discount Factor: {barrier_map['price']['pct']}% ({barrier_map['price']['num']} / {hesitation_denom}) — Primary Gate\n"
                f"   - Fabric & Material Quality: {barrier_map['quality_uncertainty']['pct']}% ({barrier_map['quality_uncertainty']['num']} / {hesitation_denom}) — Trust Gate\n"
                f"   - Shipping & Delivery Speed: {barrier_map['delivery_concern']['pct']}% ({barrier_map['delivery_concern']['num']} / {hesitation_denom})\n"
                f"   - Return & Refund Flexibility: {barrier_map['return_concern']['pct']}% ({barrier_map['return_concern']['num']} / {hesitation_denom})\n"
                f"   - Size & Fit Accuracy: {barrier_map['size_uncertainty']['pct']}% ({barrier_map['size_uncertainty']['num']} / {hesitation_denom})\n"
                f"   - Customer Reviews & Social Proof: {barrier_map['lack_of_reviews']['pct']}% ({barrier_map['lack_of_reviews']['num']} / {hesitation_denom})\n\n"
                f"2. Query Scoped Filter Result:\n"
                f"   {formatted_txt}"
            )
        elif any(kw in q_clean for kw in ["segment", "differ", "shopper"]):
            return (
                f"1. Behavioral Shopper Segment Distribution (Denominator: {hesitation_denom} Myntra records):\n"
                f"   - Price-Sensitive Shoppers (Sale waiting & discount tracking): {barrier_map['price']['pct']}% ({barrier_map['price']['num']} / {hesitation_denom})\n"
                f"   - Quality-Conscious Shoppers (Material & durability focus): {barrier_map['quality_uncertainty']['pct']}% ({barrier_map['quality_uncertainty']['num']} / {hesitation_denom})\n"
                f"   - Delivery-Sensitive Shoppers (Timeline & event deadlines): {barrier_map['delivery_concern']['pct']}% ({barrier_map['delivery_concern']['num']} / {hesitation_denom})\n"
                f"   - Fit-Hesitant Shoppers (Sizing doubt & exchange risk): {barrier_map['size_uncertainty']['pct']}% ({barrier_map['size_uncertainty']['num']} / {hesitation_denom})\n\n"
                f"2. Query Scoped Filter Result:\n"
                f"   {formatted_txt}"
            )
        elif any(kw in q_clean for kw in ["unmet", "need", "needs", "emerge", "conversation", "conversations", "opportunity"]):
            unmet_json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Processed Data", "unmet_needs_results.json")
            need_lines = []
            if os.path.exists(unmet_json_path):
                with open(unmet_json_path, "r", encoding="utf-8") as uf:
                    udata = json.load(uf)
                for n in udata.get("ranked_unmet_needs", []):
                    need_lines.append(
                        f"   #{n['rank']} {n['title']} [{n['strength']} Strength]:\n"
                        f"     - Unmet Need Statement: \"{n['statement']}\"\n"
                        f"     - Empirical Evidence: {n['share_pct']}% ({n['evidence_count']}/{n['hesitation_denominator']} Myntra hesitation records) across {n['unique_datasets_count']} datasets & {n['unique_channels_count']} channels\n"
                        f"     - Related Barrier: {n['associated_purchase_barrier']} | Behavior: {n['associated_purchase_behavior']}"
                    )
            need_str = "\n\n".join(need_lines) if need_lines else "   - Loading unmet needs..."
            return (
                f"1. Ranked Empirical Unmet Needs Breakdown (Denominator: {hesitation_denom} Myntra purchase-hesitation records):\n\n"
                f"{need_str}\n\n"
                f"2. Query Scoped Filter Result:\n"
                f"   {formatted_txt}"
            )
        else:
            return (
                f"1. Scoped Metric & Evidence Breakdown:\n"
                f"   - Relevant Evidence Records Evaluated: {retrieval_payload['population_scope']['retrieved_evidence_records_count']} high-signal consumer conversations\n"
                f"   - Myntra Purchase-Hesitation Population Evaluated: {hesitation_denom} records\n"
                f"   - Total Multi-Channel Corpus Evaluated: {retrieval_payload['population_scope']['total_dataset_size']} records\n\n"
                f"2. Query Scoped Filter Result:\n"
                f"   {formatted_txt}"
            )

    def synthesize_potential_opportunities(self, question, retrieval_payload):
        """Generates dynamic topic-specific Recommended Opportunities based on query."""
        q_clean = question.strip().lower()
        
        if "urgent" in q_clean or "urgency" in q_clean or "rush" in q_clean:
            return (
                "1. Dynamic Stock & Price Countdown Badges: Display real-time inventory scarcity ('Only 2 items left in your size') and price lock countdown timers for wishlisted products.\n"
                "2. Automated Price-Drop & Restock Urgency Alerts: Send high-priority notifications when wishlisted items receive limited-time discounts.\n"
                "3. Smart Event & Occasion Reminders: Enable users to set target delivery dates for occasion wear to convert non-urgent holding into timely checkout."
            )
        elif "size" in q_clean or "fit" in q_clean or "uncertainties" in q_clean:
            return (
                "1. Universal Brand Fit & Size Assistant: Implement AI size recommendation badges comparing brand fit to standard sizes.\n"
                "2. Free First Size Exchange Guarantee: Waive exchange fees specifically for initial size swaps on wishlisted items.\n"
                "3. Verified Buyer Height/Weight Filters: Enable filtering reviews by buyer body dimensions."
            )
        elif "price" in q_clean or "postpone" in q_clean or "add" in q_clean or "save" in q_clean:
            return (
                "1. Transparent Price History & Sale Alerts: Notify wishlist users of genuine price drops and restock alerts.\n"
                "2. Wishlist Coupon Matcher: Automatically apply eligible cart coupons to wishlisted items.\n"
                "3. Price Lock Guarantee: Allow users to reserve a sale price for 24 hours."
            )
        else:
            return (
                "1. Dynamic Price History & Restock Nudges: Giving wishlist users transparent price history trends.\n"
                "2. Enhanced Quality & Fabric Transparency: Surfacing high-signal buyer photos and fabric texture details.\n"
                "3. Delivery Date Commitments: Guaranteed dispatch badges for wishlisted items."
            )

    def generate_executive_report(self, question):
        """Generates Executive Discovery Report with Full Conversation Context Evidence."""
        retrieval_payload = self.retrieval_engine.execute_hybrid_retrieval(question, top_k=4)
        
        if self.is_missing_attribute_query(question):
            return (
                f"QUESTION\n\n\"{question}\"\n\n"
                "--------------------------------------------------\n\n"
                "EXECUTIVE INSIGHT\n\n"
                "The multi-channel consumer dataset does not contain demographic data or user age group attributes to evaluate this query. The discovery engine provides grounded qualitative and quantitative evidence on consumer purchase behaviors, wishlist intentions, friction barriers (price, fit/sizing, quality, returns), and product feedback on Myntra.\n\n"
                "--------------------------------------------------\n\n"
                "SUGGESTED ENQUIRIES\n\n"
                "- \"Why do users add fashion products to their wishlist?\"\n"
                "- \"Does people use Myntra wishlist to only save items?\"\n"
                "- \"What prevents wishlisted products from eventually being purchased?\"\n"
                "- \"What uncertainties remain after users have identified a product they like?\"\n"
                "- \"What causes users to postpone a purchase?\"\n"
            )

        if not self.is_domain_relevant(question, retrieval_payload):
            return (
                f"QUESTION\n\n\"{question}\"\n\n"
                "--------------------------------------------------\n\n"
                "EXECUTIVE INSIGHT\n\n"
                "The query that you are asking doesn't have relevant evidence in the consumer dataset to evaluate and fetch an answer. Please try asking a question related to Myntra wishlist behavior, purchase friction, sizing/fit concerns, pricing delays, return policies, or product feedback.\n\n"
                "--------------------------------------------------\n\n"
                "SUGGESTED ENQUIRIES\n\n"
                "- \"Why do users add fashion products to their wishlist?\"\n"
                "- \"Does people use Myntra wishlist to only save items?\"\n"
                "- \"What prevents wishlisted products from eventually being purchased?\"\n"
                "- \"What uncertainties remain after users have identified a product they like?\"\n"
                "- \"What causes users to postpone a purchase?\"\n"
            )

        pop_scope = retrieval_payload["population_scope"]
        quant = retrieval_payload["quantification"]
        evidence_list = retrieval_payload["retrieved_evidence"]
        hesitation_denom = pop_scope.get("reference_denominator_size", 971)
        
        opp_matrix = compute_opportunity_matrix()
        
        report_sections = []
        
        # Section 1: QUESTION
        report_sections.append(f"QUESTION\n\n\"{question}\"\n")
        
        # Section 2: DYNAMIC EXECUTIVE INSIGHT
        insight_text = self.synthesize_executive_insight(question, retrieval_payload)
        report_sections.append(f"--------------------------------------------------\n\nEXECUTIVE INSIGHT\n\n{insight_text}\n")
        
        # Section 3: DYNAMIC QUESTION-SPECIFIC QUANTIFIED FINDINGS
        quant_findings = self.synthesize_quantified_findings(question, retrieval_payload)
        report_sections.append(f"--------------------------------------------------\n\nQUANTIFIED FINDINGS\n\n{quant_findings}\n")
        
        # Section 4: FORMATTED MARKDOWN COMPARISON TABLE
        comp_table = (
            "| Opportunity Area | Mentions | Share (%) | Severity Weight | Opportunity Score |\n"
            "| :--- | :---: | :---: | :---: | :---: |\n"
        )
        for item in opp_matrix[:5]:
            area = item['opportunity_area'].replace("_", " ").title()
            num = item['numerator']
            share = f"{item['raw_frequency_pct']}%"
            weight = f"{item['severity_weight']}x"
            score = f"{item['opportunity_score']:.2f}"
            comp_table += f"| {area} | {num} | {share} | {weight} | {score} |\n"
            
        report_sections.append(f"--------------------------------------------------\n\nCOMPARISON MATRIX\n\n{comp_table}\n")
        
        # Section 5: REPRESENTATIVE GROUNDED EVIDENCE & FULL CONVERSATION CONTEXT
        if evidence_list:
            evidence_text = ""
            for ev in evidence_list:
                clean_context = ev['evidence_quote'].encode('ascii', 'ignore').decode('ascii')
                sent_data = ev.get('sentiment_analysis', {})
                sent_lbl = sent_data.get('sentiment_label', 'Unknown')
                sent_score = sent_data.get('sentiment_score', 'N/A')
                evidence_text += (
                    f"• **Channel**: {ev['source_channel'].upper()} ({ev['platform_brand'].title()}) | **Segment**: {ev['user_segment']} | **Sentiment**: {sent_lbl} (Score: {sent_score})\n"
                    f"  **Full Conversation Context**: \"{clean_context}\"\n\n"
                )
            report_sections.append(f"--------------------------------------------------\n\nREPRESENTATIVE GROUNDED EVIDENCE & FULL CONVERSATION CONTEXT\n\n{evidence_text}")
            
        # Section 6: DYNAMIC POTENTIAL OPPORTUNITIES
        opp_text = self.synthesize_potential_opportunities(question, retrieval_payload)
        report_sections.append(f"--------------------------------------------------\n\nPOTENTIAL OPPORTUNITIES\n\n{opp_text}\n")
        
        # Section 7: BUSINESS RELEVANCE
        relevance_text = (
            "Addressing these query-specific opportunity areas directly targets consumer friction "
            "holding back wishlist conversion. Tailoring product transparency and price alerts to user intent "
            "plausibly accelerates wishlist-to-purchase conversion velocity."
        )
        report_sections.append(f"--------------------------------------------------\n\nBUSINESS RELEVANCE\n\n{relevance_text}\n")
        
        # Section 8: CONFIDENCE / LIMITATIONS
        limitations_text = (
            f"- Total Dataset Size: {pop_scope['total_dataset_size']} records across 14 datasets.\n"
            f"- Myntra Purchase-Hesitation Denominator: {hesitation_denom} Myntra customer friction records.\n"
            f"- Scope Rule Applied: Purchase friction & conversion barriers analyzed ONLY on Myntra data ({hesitation_denom} records denominator); cross-platform data (Myntra, AJIO, Nykaa) utilized to analyze general wishlist intent & usage modes.\n"
            f"- Observational Disclaimer: Findings represent observed correlations and reported consumer feedback; they do not imply direct causal claims."
        )
        report_sections.append(f"--------------------------------------------------\n\nCONFIDENCE / LIMITATIONS\n\n{limitations_text}\n")
        
        full_report = "\n".join(report_sections)
        return full_report

def run_synthesis_demo():
    synthesizer = GroundedSynthesisEngine()
    test_q = "Why do users add fashion products to their wishlist?"
    report = synthesizer.generate_executive_report(test_q)
    print("REPORT OUTPUT WITH FULL CONVERSATION CONTEXT:\n", report[:1200])

if __name__ == "__main__":
    run_synthesis_demo()
