# Comprehensive Edge Case Reference: Myntra Consumer Discovery Engine

> **Document Purpose:** Guidelines for handling ambiguous, multi-dimensional, sarcastic, and context-dependent consumer conversations in the Myntra Wishlist-to-Purchase Discovery Engine.  
> **Target Path:** `docs/edge_case.md`  
> **Status:** Reference Specification & Edge-Case Catalog (No code modifications introduced in this step).

---

## 1. Classification Edge Cases

### Edge Case 1.1: Keyword Mention Without Actual Intent

**Example:**  
*"Everyone keeps saying Myntra has good discounts."*

**Risk:**  
Naive keyword matchers will detect `"discounts"` and `"Myntra"` and misclassify the post as active purchase or coupon intent.

**Incorrect interpretation:**  
`primary_intent = sale_discount` or `purchase_intent = true`

**Correct interpretation:**  
Third-person statement or general observation about platform reputation; no personal buying intent or active discount seeking.

**Recommended handling:**  
Evaluate subject pronouns (e.g., first-person *"I want..."* vs third-person *"Everyone says..."*). Require personal behavioral markers for active intent.

**Impact on discovery engine:**  
Affects Business Question #1 (Why users wishlist) and Question #8 (Wishlist as genuine purchase signal).

---

### Edge Case 1.2: Mention of Wishlist Without Active Wishlist Behavior

**Example:**  
*"Does Myntra have a wishlist feature on the web version?"*

**Risk:**  
The keyword `"wishlist"` triggers a wishlist intent label even though the user is asking a functional product question.

**Incorrect interpretation:**  
`user_behavior = wishlist` or `primary_intent = wishlist`

**Correct interpretation:**  
`user_behavior = product_research` / `platform_question`; the user is inquiring about app/web functionality.

**Recommended handling:**  
Distinguish between functional questions about the wishlist feature versus first-person wishlisting actions (*"I added this dress to my wishlist"*).

**Impact on discovery engine:**  
Affects Question #1 (Why users wishlist) and Question #8 (Wishlist intent validation).

---

### Edge Case 1.3: Purchase Intent vs. Completed Purchase

**Example 1:** *"I want to buy this dress."*  
**Example 2:** *"I bought this dress yesterday during the sale."*

**Risk:**  
Treating pre-purchase intent and post-purchase outcome as the same signal skews consideration vs post-purchase conversion data.

**Incorrect interpretation:**  
Treating both examples as `purchase_intent = true` or `user_behavior = purchase`.

**Correct interpretation:**  
Example 1 is pre-purchase consideration (`purchase_status = intended`/`postponed`). Example 2 is post-purchase completion (`purchase_status = completed`).

**Recommended handling:**  
Enforce strict tense and status classification (`purchase_intent` vs `purchase_completed`).

**Impact on discovery engine:**  
Affects Question #2 (What prevents purchase) and Question #7 (Role of factors in purchase decisions).

---

### Edge Case 1.4: Price Discussion vs. Price-Drop Intent

**Example 1:** *"The price of this kurta is ₹1,999."*  
**Example 2:** *"Added to wishlist and waiting for the price to drop below ₹1,500."*

**Risk:**  
Classifying every sentence mentioning price/rupees as a `price_drop` intent.

**Incorrect interpretation:**  
`primary_intent = price_drop` for both examples.

**Correct interpretation:**  
Example 1 is factual price reference. Example 2 is price-drop waiting behavior (`purchase_barrier = price`, `purchase_status = postponed`).

**Recommended handling:**  
Require conditional wait/hesitation phrasing (*"waiting for sale"*, *"too expensive for now"*, *"will buy if price drops"*) to assign price barrier/intent.

**Impact on discovery engine:**  
Affects Question #4 (Causes of postponed purchases) and Question #7 (Role of price).

---

### Edge Case 1.5: Sale/Discount Mention vs. Coupon Request

**Example 1:** *"Bought it during the EORS sale."*  
**Example 2:** *"Does anyone have a working 20% off coupon code for Myntra?"*

**Risk:**  
Merging promotional context (sales) with active deal-seeking behavior (coupon hunting).

**Incorrect interpretation:**  
Collapsing both into a single generic `sale_discount` label.

**Correct interpretation:**  
Example 1 is sale event context (`purchase_context = sale`). Example 2 is active deal-seeking (`information_need = coupon_code`).

**Recommended handling:**  
Separate event context from specific user information needs (coupons vs general sales).

**Impact on discovery engine:**  
Affects Question #6 (Information sought before purchase) and Question #10 (Unmet needs).

---

### Edge Case 1.6: Product Discovery vs. Specific Purchase Intent

**Example 1:** *"Can someone suggest good black dresses on Myntra under 2k?"*  
**Example 2:** *"I found the exact dress I want to buy on Myntra."*

**Risk:**  
Lumping broad recommendation-seeking together with item-specific purchase intent.

**Incorrect interpretation:**  
`primary_intent = purchase_intent` for both.

**Correct interpretation:**  
Example 1 is exploratory discovery (`purchase_stage = discovery`, `user_behavior = recommendation_seeking`). Example 2 is targeted intent (`purchase_stage = consideration`/`intent`).

**Recommended handling:**  
Differentiate open-ended discovery queries from targeted product intent.

**Impact on discovery engine:**  
Affects Question #5 (Comparing shortlisted products) and Question #9 (Behavior across user segments).

---

### Edge Case 1.7: Product Quality Concern vs. Customer Support Friction

**Example 1:** *"The fabric quality of this dress is thin and see-through."*  
**Example 2:** *"Myntra customer support hasn't responded to my ticket for 3 days."*

**Risk:**  
Combining product-level defect feedback with service/support friction.

**Incorrect interpretation:**  
Grouping both into `customer_service` or `product_quality`.

**Correct interpretation:**  
Example 1 is product-level quality barrier (`purchase_barrier = quality_uncertainty`). Example 2 is platform support friction (`purchase_barrier = customer_support_friction`).

**Recommended handling:**  
Maintain separate tags for product attributes (fabric, fit, quality) vs operational platform service (support, chat, agent).

**Impact on discovery engine:**  
Affects Question #7 (Role of quality) and Question #2 (Barriers to purchase).

---

### Edge Case 1.8: Order Delivery Tracking vs. Product Restock Availability

**Example 1:** *"When will my shipped order arrive in Bangalore?"*  
**Example 2:** *"When will size Medium for this dress be back in stock?"*

**Risk:**  
Confusing post-purchase logistics tracking with pre-purchase stock availability.

**Incorrect interpretation:**  
Flagging both as `delivery` or `availability`.

**Correct interpretation:**  
Example 1 is post-purchase order tracking (`purchase_stage = post_purchase`, `topic = delivery_tracking`). Example 2 is pre-purchase stock barrier (`purchase_stage = consideration`, `purchase_barrier = availability`).

**Recommended handling:**  
Scope stock availability questions to pre-purchase hesitation, and order tracking to post-purchase logistics.

**Impact on discovery engine:**  
Affects Question #2 (Barriers to purchase) and Question #7 (Role of availability).

---

### Edge Case 1.9: Distinguishing Cancellation, Return, Refund, and Exchange

**Example:**  
*"I canceled my order because the size was wrong, but now the refund is stuck and I want to exchange instead."*

**Risk:**  
Collapsing distinct post-purchase/cancellation actions into a single `cancellation_refund` label.

**Incorrect interpretation:**  
`primary_intent = cancellation_refund` (losing the sizing root cause and exchange friction).

**Correct interpretation:**  
Root barrier = `size_uncertainty`; Operational frictions = `cancellation`, `refund_delay`, `exchange_request`.

**Recommended handling:**  
Extract granular operational event tags (`action_type: cancel | return | refund | exchange`) while preserving the underlying product barrier (size/fit).

**Impact on discovery engine:**  
Affects Question #2 (Purchase barriers) and Question #10 (Unmet needs).

---

## 2. Multi-Intent Edge Cases

### Edge Case 2.1: Single Conversation Containing Multiple Behavioral Signals

**Example:**  
*"I love this dress on Myntra and added it to my wishlist, but I'm waiting for reviews because I'm unsure if size M will fit."*

**Risk:**  
Forcing the conversation into a single `primary_intent` (e.g. `wishlist` or `product_quality`), destroying the price, fit, and review signals.

**Incorrect interpretation:**  
`primary_intent = wishlist` (ignoring size uncertainty and review dependency).

**Correct interpretation:**  
- `user_behavior`: `["wishlist", "product_research", "purchase_postponed"]`
- `purchase_stage`: `"consideration"`
- `purchase_status`: `"postponed"`
- `purchase_barriers`: `["size_uncertainty", "lack_of_reviews"]`
- `information_needs`: `["reviews", "fit_information"]`
- `decision_factors`: `["size", "fit", "reviews"]`
- `opportunity_area`: `"better_size_guidance"`

**Recommended handling:**  
Store analytical extraction as a multi-dimensional array of tags rather than a single string label.

**Impact on discovery engine:**  
Affects all 10 Business Questions. This is a foundational system requirement.

---

## 3. Thread Context Edge Cases

### Edge Case 3.1: Comment Inheriting Context From Parent Post

**Example:**  
- **Parent Post:** *"Has anyone bought the roadster denim jacket on Myntra?"*  
- **Comment:** *"Yes, I got it last week. The material is thick but order one size up."*

**Risk:**  
Analyzing the comment in isolation misses the platform (`Myntra`) and product (`roadster denim jacket`).

**Incorrect interpretation:**  
Comment labeled as generic sizing advice with no brand or platform association.

**Correct interpretation:**  
The comment provides sizing advice (`purchase_barrier = size_fit_guidance`) specifically for Myntra / Roadster outerwear.

**Recommended handling:**  
Prepend parent post title or thread context (`post_context`) during comment processing and vector embedding.

**Impact on discovery engine:**  
Affects Question #6 (Information sought) and Question #7 (Role of size/fit).

---

### Edge Case 3.2: Topic Divergence Between Parent Thread and Comment

**Example:**  
- **Parent Post:** *"Myntra End of Reason Sale thread - share your wishlist items!"*  
- **Comment:** *"Myntra's refund process took 14 days to credit my bank last month, never buying again."*

**Risk:**  
Inheriting the parent post's `wishlist`/`sale` intent for a comment that is clearly expressing delivery/refund dissatisfaction.

**Incorrect interpretation:**  
`primary_intent = wishlist` or `sale_discount` for the comment.

**Correct interpretation:**  
The comment deviates to `cancellation_refund` friction (`purchase_status = abandoned`).

**Recommended handling:**  
Allow comment-level intent to override parent thread topic when strong conflicting sentiment/intent signals exist.

**Impact on discovery engine:**  
Affects Question #2 (Purchase barriers) and Question #8 (Wishlist intent validation).

---

## 4. Sarcasm / Humor / Figurative Language

### Edge Case 4.1: Sarcastic Sentiment in Delivery and Service Discussions

**Example:**  
*"Yeah, because waiting 3 weeks for Myntra to deliver my dress is exactly what I wanted for my birthday 😂"*

**Risk:**  
Literal keyword analyzer sees *"exactly what I wanted"* and assigns positive sentiment or successful delivery.

**Incorrect interpretation:**  
`sentiment = positive`, `delivery_satisfaction = high`.

**Correct interpretation:**  
Severe dissatisfaction with delivery delay (`purchase_barrier = delivery_delay`, `sentiment = negative_sarcasm`).

**Recommended handling:**  
Flag sarcastic markers (laughing emojis with long waiting times, anti-phrasal praise) as low-confidence or negative friction signals.

**Impact on discovery engine:**  
Affects Question #2 (Barriers to purchase) and Question #7 (Role of availability/delivery).

---

### Edge Case 4.2: Irony in Price and Discount Expressions

**Example:**  
*"Love paying full price for clothes that shrink in one wash 🙃"*

**Risk:**  
Keyword matching flags `"Love"` and `"full price"` as positive brand affinity.

**Incorrect interpretation:**  
`price_satisfaction = positive`, `quality = acceptable`.

**Correct interpretation:**  
Price dissatisfaction combined with quality complaint (`purchase_barrier = price_value_ratio`, `quality_uncertainty`).

**Recommended handling:**  
Analyze inverse emoji context (`🙃`, `🤡`) and contrastive clauses (*"love paying... for clothes that shrink"*).

**Impact on discovery engine:**  
Affects Question #7 (Role of price & quality) and Question #10 (Unmet needs).

---

## 5. Negation Edge Cases

### Edge Case 5.1: Negated Intent Keywords

**Example 1:** *"I don't want to buy this even if it goes on sale."*  
**Example 2:** *"I wouldn't wishlist this item."*  
**Example 3:** *"Had no issues with Myntra delivery."*  
**Example 4:** *"I am not waiting for a discount."*

**Risk:**  
Detecting target keywords (`buy`, `wishlist`, `delivery`, `discount`) and assigning intent regardless of the negative modifier.

**Incorrect interpretation:**  
Flagging Example 1 as `purchase_intent`, Example 2 as `wishlist`, Example 3 as `delivery_issue`, Example 4 as `price_drop`.

**Correct interpretation:**  
- Ex. 1: Explicit rejection (`purchase_intent = false`).
- Ex. 2: Negative wishlist affinity (`wishlist = false`).
- Ex. 3: Positive delivery experience (`delivery_friction = false`).
- Ex. 4: Price insensitive (`price_wait = false`).

**Recommended handling:**  
Implement dependency parsing or negation window detection (checking 3-5 words preceding intent keywords for `don't`, `not`, `no`, `never`, `wouldn't`).

**Impact on discovery engine:**  
Affects Question #1 (Why wishlist), Question #4 (Postponement), and Question #8 (Wishlist intent signal).

---

## 6. Hypothetical / General Research Questions

### Edge Case 6.1: General Questions vs. First-Person Behavioral Intent

**Example 1:** *"Why do people wishlist clothes on Myntra and never buy them?"*  
**Example 2:** *"Does Myntra normally have sales in August?"*  
**Example 3:** *"Would you buy a dress without size reviews?"*

**Risk:**  
Treating a meta-question about shopping habits as a user's personal active shopping behavior.

**Incorrect interpretation:**  
Classifying Example 1 as a personal wishlist behavior record for the poster.

**Correct interpretation:**  
`user_behavior = meta_discussion` / `community_question`. The post discusses community behavior, not the author's current active transaction.

**Recommended handling:**  
Tag general research / meta-questions with `discussion_type = general_question` to prevent skewing first-person behavioral metrics.

**Impact on discovery engine:**  
Affects Question #8 (Wishlist intent validation) and Question #9 (User segmentation).

---

## 7. Comparison Edge Cases

### Edge Case 7.1: Multi-Platform Product Comparison

**Example:**  
*"Should I buy this Mango dress on Myntra for ₹2,400 or get it on AJIO where it's ₹2,100 but returns are slow?"*

**Risk:**  
Classifier picks one platform or treats it purely as an AJIO or Myntra post, ignoring the cross-platform trade-off.

**Incorrect interpretation:**  
`primary_intent = price_drop` (Myntra only).

**Correct interpretation:**  
- `user_behavior`: `["product_comparison", "platform_tradeoff"]`
- `compared_platforms`: `["Myntra", "AJIO"]`
- `tradeoff_factors`: `{"Myntra": "higher_price_better_service", "AJIO": "lower_price_slower_returns"}`
- `purchase_stage`: `"shortlist"`

**Recommended handling:**  
Extract structured comparison objects (`compared_entities`, `decision_tradeoffs`).

**Impact on discovery engine:**  
Affects Question #5 (How users compare shortlisted products) and Question #6 (External info sought).

---

## 8. Brand / Platform Mention Edge Cases

### Edge Case 8.1: Standalone Brand Mention Without Shopping Intent

**Example:**  
*"Zara jackets have better fitting than most Indian brands."*

**Risk:**  
Associating Zara mention with Myntra purchase intent or misattributing brand preference.

**Incorrect interpretation:**  
Classifying as `Myntra_purchase_intent` or `product_discovery`.

**Correct interpretation:**  
General brand style opinion (`brand_mention = Zara`, `topic = fit_comparison`); no active Myntra purchase stage.

**Recommended handling:**  
Require explicit platform connection (e.g. *"Zara on Myntra"*) before linking brand discussions to Myntra discovery insights.

**Impact on discovery engine:**  
Affects Question #7 (Role of brand) and Question #9 (User segmentation).

---

## 9. Purchase Journey Edge Cases

### Edge Case 9.1: Ambiguous Purchase Journey Stage Transitions

**Example 1:** *"I've added this jacket to my wishlist until payday next week."*  
**Example 2:** *"I bought it after waiting 2 months for the price to drop."*

**Risk:**  
Failing to capture the temporal progression of user state (e.g. Wishlist → Postponed → Purchased).

**Incorrect interpretation:**  
Labeling Ex. 1 simply as `wishlist` and Ex. 2 simply as `purchase_completed`.

**Correct interpretation:**  
- Ex. 1: `wishlist` + `postponed` (trigger: liquidity/payday).
- Ex. 2: `wishlist_converted` (transition from price hesitation to purchase completion).

**Recommended handling:**  
Track both `current_stage` and `journey_transition` (e.g., `wishlist_to_postponed`, `postponed_to_purchased`).

**Impact on discovery engine:**  
Affects Question #4 (Postponement causes) and Question #8 (Wishlist signal strength).

---

## 10. Wishlist-Specific Edge Cases

### Edge Case 10.1: Wishlist as Bookmarking vs. Genuine Purchase Intent

**Example 1:** *"I add 100 items I like to my wishlist every week just to save pretty pictures."*  
**Example 2:** *"I put this dress on my wishlist and checked the price every morning until I bought it."*

**Risk:**  
Treating all wishlist additions as equal high-intent buying signals.

**Incorrect interpretation:**  
Assuming both users have equal purchase conversion likelihood.

**Correct interpretation:**  
- Ex. 1: `wishlist_type = casual_bookmarking` (low purchase intent).
- Ex. 2: `wishlist_type = active_consideration` (high purchase intent, price monitoring).

**Recommended handling:**  
Differentiate `wishlist_intent_level` (`casual_bookmarking` vs `active_consideration` vs `hesitation_holding`).

**Impact on discovery engine:**  
Affects Question #1 (Why wishlist), Question #8 (Wishlist as intent vs bookmarking), and Question #9 (User segmentation).

---

### Edge Case 10.2: Wishlist Caused by Size/Fit Uncertainty

**Example:**  
*"Added to my wishlist because I'm between size S and M and don't want the hassle of returning it."*

**Risk:**  
Missing the fit root cause and labeling the post solely as `wishlist`.

**Incorrect interpretation:**  
`primary_intent = wishlist`

**Correct interpretation:**  
- `user_behavior`: `"wishlist"`
- `purchase_status`: `"postponed"`
- `purchase_barrier`: `"size_fit_uncertainty"`
- `return_friction_concern`: `true`

**Recommended handling:**  
Link wishlist retention directly to explicit barrier categories (size uncertainty, return fear).

**Impact on discovery engine:**  
Affects Question #2 (Purchase barriers), Question #3 (Uncertainties after shortlisting), and Question #7 (Role of size/fit).

---

## 11. Purchase Barrier Edge Cases

### Edge Case 11.1: Multiple Overlapping Purchase Barriers

**Example:**  
*"I love this top on Myntra but there are zero reviews, the size chart looks wrong, and ₹1,800 is too high for polyester."*

**Risk:**  
Selecting one barrier (e.g. price) and ignoring size chart inaccuracy and lack of social proof.

**Incorrect interpretation:**  
`purchase_barrier = price` (losing size and review barriers).

**Correct interpretation:**  
`purchase_barriers = ["price_value_mismatch", "lack_of_reviews", "size_chart_inaccuracy"]`

**Recommended handling:**  
Support multiple concurrent tags in `purchase_barriers` list.

**Impact on discovery engine:**  
Affects Question #2 (Barriers to purchase), Question #3 (Uncertainties), and Question #10 (Unmet needs).

---

## 12. Information Need Edge Cases

### Edge Case 12.1: Information Need vs. Evaluated Review Evidence

**Example 1:** *"Does anyone know if this Myntra brand runs true to size? Need fit reviews."*  
**Example 2:** *"The reviews on Myntra say the fabric bleeds color after one wash."*

**Risk:**  
Confusing a request for information with extracted product feedback evidence.

**Incorrect interpretation:**  
Labeling both as `information_need = reviews`.

**Correct interpretation:**  
- Ex. 1: `information_need = fit_reviews` (User seeking info).
- Ex. 2: `observed_evidence = quality_issue` (User quoting review findings).

**Recommended handling:**  
Separate `information_seeking` tags from `reported_evidence` tags.

**Impact on discovery engine:**  
Affects Question #6 (Information sought outside platform) and Question #7 (Role of reviews/quality).

---

## 13. Quantification Edge Cases

### Edge Case 13.1: Incorrect Denominator Selection in Percentage Metrics

**Example Claim:**  
*"31% of users have size concerns."*

**Risk:**  
Calculating percentage using the entire 5,700-row dataset (including general app reviews and shipping complaints) instead of the relevant subset of purchase-hesitation conversations.

**Incorrect interpretation:**  
$$31\% = \frac{\text{Size Concern Posts}}{\text{Total All Dataset Rows (5,706)}}$$

**Correct interpretation:**  
$$31.1\% = \frac{\text{Size Concern Posts (140)}}{\text{Purchase-Hesitation Conversations (450)}}$$

**Recommended handling:**  
Enforce strict population denominator reporting:  
$$\text{Share (\%)} = \left( \frac{\text{Numerator}}{\text{Explicit Sub-Population Denominator}} \right) \times 100$$

**Impact on discovery engine:**  
Affects Core Analytical Principle (IDENTIFY → QUANTIFY → COMPARE) and executive findings accuracy.

---

## 14. Low-Confidence / Ambiguous Data

### Edge Case 14.1: Short, Emoji-Only, or Low-Context Feedback

**Example 1:** *"Great."*  
**Example 2:** *"🔥😍"*  
**Example 3:** *"https://myntra.com/p/12345"*  
**Example 4:** *"[deleted]"*

**Risk:**  
Forcing empty or ultra-short comments into substantive intent categories or generating hallucinated RAG insights.

**Incorrect interpretation:**  
Assigning `purchase_intent` to "Great." or "🔥😍".

**Correct interpretation:**  
Low-signal records (`is_relevant = false`, `confidence = low`).

**Recommended handling:**  
Filter out records with word count < 3 or set `confidence_score < 0.4` before analytics and RAG ingestion.

**Impact on discovery engine:**  
Affects RAG retrieval quality and quantitative distribution accuracy.

---

## 15. RAG / Retrieval Edge Cases

### Edge Case 15.1: Contextually Incorrect Semantic Vector Retrieval

**Example Query:**  
*"Why do users postpone buying wishlisted dresses on Myntra?"*

**Retrieved Result (Incorrect):**  
*"Myntra delivery agent was late by 2 days for my shoes order."* (Retrieved due to generic semantic similarity with "Myntra" and "delay").

**Risk:**  
RAG retrieves post-purchase logistics issues when answering pre-purchase wishlist consideration questions.

**Incorrect interpretation:**  
LLM incorporates delivery delay into wishlist postponement reasons.

**Correct interpretation:**  
RAG must enforce metadata filtering (`purchase_stage = consideration`, `purchase_status = postponed`) alongside vector similarity.

**Recommended handling:**  
Implement Hybrid Retrieval (Vector Similarity + Metadata Filtering on stage, barriers, and platform).

**Impact on discovery engine:**  
Affects RAG answer validity and executive recommendations.

---

## 16. Contradictory Evidence Edge Cases

### Edge Case 16.1: Conflicting User Feedback on Platform Policies

**Example 1:** *"Myntra's return pickup was super smooth and instant!"*  
**Example 2:** *"Myntra return policy is awful, they rejected my pickup twice!"*

**Risk:**  
Synthesizing a single one-sided conclusion (e.g. *"Myntra returns are bad"*).

**Incorrect interpretation:**  
LLM presents one side as absolute truth.

**Correct interpretation:**  
The engine presents balanced, quantified evidence:  
*"User sentiment on returns is mixed: 62% report smooth pickups while 38% report rejection/delay friction (Denominator: 120 return-related conversations)."*

**Recommended handling:**  
Require RAG synthesizer to detect opposing sentiment clusters and report both perspectives with counts.

**Impact on discovery engine:**  
Affects Question #10 (Unmet needs) and Executive Confidence statements.

---

## 17. Causality Warning

### Edge Case 17.1: Inferring Conversion Causality From Frequency Alone

**Example Observation:**  
*"Size/fit uncertainty appears in 31% of hesitation conversations."*

**Prohibited Causal Assertion:**  
*"Solving size guidance will increase overall Myntra conversion by 31%."*

**Approved Observational Assertion:**  
*"Size/fit uncertainty is associated with 31% of purchase-hesitation conversations and represents a high-priority potential opportunity area."*

**Recommended handling:**  
Strictly enforce observational language rules (`"is associated with"`, `"appears frequently"`, `"represents a potential opportunity"`).

**Impact on discovery engine:**  
Protects strategic credibility and prevents false business claims.

---

## 18. Opportunity Discovery Edge Cases

### Edge Case 18.1: Ranking Opportunities Purely by Frequency Without Severity

**Example:**  
- Issue A: Minor UI button color feedback (mentioned 100 times, low purchase friction).  
- Issue B: Size chart inconsistency causing 80% return rate (mentioned 70 times, severe purchase friction).

**Risk:**  
Ranking Issue A above Issue B simply because 100 > 70.

**Incorrect interpretation:**  
Ranking UI button color as Priority #1 Opportunity.

**Correct interpretation:**  
Weight opportunity scoring by both Frequency and Business Friction Impact:  
$$\text{Opportunity Score} = \text{Frequency} \times \text{Friction Severity Weight}$$

**Recommended handling:**  
Incorporate friction severity weights into the Opportunity Matrix scoring module (Module 11).

**Impact on discovery engine:**  
Affects Opportunity Matrix ranking and strategic product prioritization.

---

## 19. User Segmentation Edge Cases

### Edge Case 19.1: Inventing Ungrounded Demographic Attributes

**Example:**  
*"I need a budget outfit for college."*

**Risk:**  
Inferring exact demographic attributes (e.g. `"age = 19"`, `"female"`, `"income < 20k"`) without explicit data.

**Incorrect interpretation:**  
Assigning unverified demographic profile tags.

**Correct interpretation:**  
`user_segment = price_sensitive` / `college_occasion`. (Behavior-based and occasion-based tagging).

**Recommended handling:**  
Restrict segmentation strictly to observable user behaviors (`price_sensitive`, `fit_hesitant`, `research_heavy`) and explicit occasion tags.

**Impact on discovery engine:**  
Affects Question #9 (Differences across user segments).

---

## 20. Data Quality & Formatting Edge Cases

### Edge Case 20.1: Handling Hinglish, Slang, Abbreviations, and Headerless CSVs

**Example 1:** *"VFM product, kapda ekdum badiya hai but sizing issue hai."* (Hinglish: Value For Money, fabric is great but sizing issue).  
**Example 2:** *"Headerless row in `myntra_playstore.csv` read as column names."*

**Risk:**  
- Standard English NLP missing Hinglish terms (`VFM`, `kapda`, `badiya`).  
- Headerless CSVs dropping valid review rows or assigning UUIDs as column names.

**Incorrect interpretation:**  
Failing to extract quality (`badiya`) and size (`sizing issue`) from Hinglish text.

**Correct interpretation:**  
Hinglish text mapped to: `value = positive`, `fabric_quality = high`, `size_barrier = true`. CSV loaded with `header=None`.

**Recommended handling:**  
- Include Hinglish & Indian e-commerce slang dictionary in token preprocessing (`VFM` -> Value for Money, `kapda` -> fabric).  
- Standardize CSV ingestion to inspect and enforce header formats.

**Impact on discovery engine:**  
Affects multi-channel ingestion stability and sentiment extraction accuracy.

---

# Edge Case Priorities

Below is the prioritized classification of all 20 documented edge cases, categorized by their potential to distort business discovery insights.

### P0 — Critical (Must-Be-Handled in Core Engine Design)
*These edge cases directly affect the core business metric or can severely distort strategic recommendations.*

1. **Edge Case 2.1 (Multi-Intent Signals):** Single-label classification destroys multi-dimensional friction signals. Mandatory for all downstream analytical modules.
2. **Edge Case 13.1 (Denominator Selection):** Incorrect denominators produce false percentage statistics that deceive product leadership.
3. **Edge Case 15.1 (RAG Vector Context Misalignment):** Unfiltered vector retrieval brings post-purchase delivery complaints into pre-purchase wishlist questions.
4. **Edge Case 17.1 (Causality Claim Overreach):** Making unsupported causal claims (*"will boost conversion by 31%"*) destroys strategic credibility.
5. **Edge Case 5.1 (Negation Handling):** Misinterpreting negated intent (*"don't want to buy"*) directly inverts behavioral signals.

---

### P1 — Important (Significantly Affects Accuracy & Signal Quality)
*These edge cases prevent misclassification and improve cross-channel insight reliability.*

6. **Edge Case 1.1 & 1.2 (Keyword Without Intent & Wishlist Feature Inquiry):** Prevents non-behavioral mentions from skewing wishlist metrics.
7. **Edge Case 1.3 (Purchase Intent vs Completed Purchase):** Distinguishes pre-purchase consideration from post-purchase reviews.
8. **Edge Case 1.4 (Price Discussion vs Price-Drop Wait):** Separates factual price mentions from active postponement friction.
9. **Edge Case 3.1 & 3.2 (Thread Context & Topic Divergence):** Ensures Reddit comments retain product context without inheriting wrong thread topics.
10. **Edge Case 7.1 (Cross-Platform Comparisons):** Enables structured comparison between Myntra and competitors (AJIO, Nykaa).
11. **Edge Case 10.1 & 10.2 (Wishlist Intent Levels & Size-Driven Wishlisting):** Distinguishes casual bookmarking from high-intent wishlist holding.
12. **Edge Case 11.1 (Multiple Overlapping Barriers):** Ensures all concurrent purchase friction factors (fit + price + reviews) are captured.
13. **Edge Case 18.1 (Opportunity Scoring Weighting):** Prevents high-frequency minor feedback from outranking critical conversion friction.

---

### P2 — Nice to Handle (Enhances Robustness & Edge Handling)
*These edge cases refine edge-case robustness, noise filtering, and edge-case display.*

14. **Edge Case 1.5 (Sale vs Coupon Request):** Refines promotional deal-seeking categorization.
15. **Edge Case 1.6 (Discovery vs Targeted Intent):** Distinguishes open exploration from specific product evaluation.
16. **Edge Case 1.7 & 1.8 (Quality vs Support & Delivery vs Restock):** Fine-tunes operational issue breakdown.
17. **Edge Case 4.1 & 4.2 (Sarcasm & Irony Detection):** Identifies sarcastic delivery/pricing sentiment.
18. **Edge Case 6.1 (General Research Questions):** Filters meta-questions from first-person behavior.
19. **Edge Case 14.1 (Low-Confidence / Short Text Filtering):** Filters out single-word/emoji noise.
20. **Edge Case 16.1 & 19.1 & 20.1 (Contradictory Evidence, Segmentation & Hinglish Preprocessing):** Handles mixed sentiment, behavior-only segments, and Indian regional slang.
