# Problem Statement: AI-Powered Fashion Consumer Discovery & Behavioral Insight Engine

I am building an AI-powered fashion consumer discovery and behavioral insight engine focused on Myntra's wishlist journey.

I am not a programmer, so you should create the code for me and explain each implementation step in simple terms. However, do NOT make architectural or dataset changes without explaining the reason first.

==================================================
1. CORE PROBLEM
==================================================

Myntra users add fashion products to their wishlist, but a wishlist does not necessarily mean that the user will eventually purchase the product.

We want to understand the gap between:

Wishlist → Consideration → Purchase

The goal is to discover WHY users wishlist products, what prevents them from purchasing, what information they need before purchasing, and what unmet needs or opportunities exist in the journey.

The engine must go beyond:
- sentiment analysis
- review summarization
- simple keyword counting
- generic chatbot responses

It should identify, quantify where possible, and compare potential opportunity areas that could influence the stated business metric.

PRIMARY BUSINESS METRIC:

Wishlist-to-purchase conversion / reducing friction between wishlist and purchase.

==================================================
2. BUSINESS QUESTIONS THE ENGINE MUST ANSWER
==================================================

The discovery engine should eventually be able to answer questions such as:

1. Why do users add fashion products to their wishlist?

2. What prevents wishlisted products from eventually being purchased?

3. What uncertainties remain after users have identified a product they like?

4. What causes users to postpone a purchase?

5. How do users compare multiple shortlisted products?

6. What information do users seek outside Myntra/AJIO before purchasing?

7. What role do the following factors play in purchase decisions?
   - fit
   - size
   - styling
   - price
   - reviews
   - occasion
   - quality
   - brand
   - social validation
   - availability

8. When is a wishlist a genuine purchase-intent signal versus simply a bookmarking mechanism?

9. How do these behaviors differ across user segments?

10. What unmet needs emerge consistently across user conversations?

==================================================
3. CORE ANALYTICAL PRINCIPLE
==================================================

Every major insight should follow this framework:

IDENTIFY
→ What behavior, problem, uncertainty, friction or need exists?

QUANTIFY
→ How frequently does it occur?
→ What percentage of relevant conversations does it represent?
→ Always show the denominator/context used for the percentage.

COMPARE
→ How does this opportunity compare with other opportunity areas?
→ Which problems appear more frequently or more strongly?

CONNECT TO BUSINESS METRIC
→ Could this behavior or friction plausibly affect wishlist-to-purchase conversion?
→ Clearly distinguish observed evidence from inferred business implications.

The engine should NOT claim that something causes conversion changes unless the data supports that conclusion.

Use language such as:
- "appears frequently"
- "is associated with"
- "may represent an opportunity"
- "is a potential purchase barrier"

instead of making unsupported causal claims.

==================================================
4. DATA SOURCES
==================================================

The first major source is Reddit conversations related to Myntra and fashion shopping.

The current project already contains:

Raw/cleaned Reddit data
and
a labeled Reddit dataset.

Current labeled dataset:
reddit_myntra_labeled.csv

Current labeling script:
Scripts/label_reddit_intents.py

The current dataset contains 634 labeled rows.

IMPORTANT:
Do NOT discard the existing labeled dataset.

IMPORTANT:
Do NOT modify the existing classifier merely to improve the appearance of the distribution.

The current intent labels include categories such as:

- wishlist
- purchase_intent
- price_drop
- sale_discount
- coupon
- product_discovery
- restock_availability
- cancellation_refund
- product_quality
- delivery
- customer_service
- other

These labels are a starting point, NOT the final analytical schema.

==================================================
5. IMPORTANT DISTINCTION
==================================================

The existing primary_intent classification is NOT sufficient for the final discovery engine.

A single conversation may contain multiple useful behavioral signals.

For example:

"I love this dress but I'm waiting for reviews because I'm unsure about the sizing."

This should not simply become:

primary_intent = wishlist

The analytical representation should ideally capture multiple dimensions such as:

behavior = wishlist
purchase_stage = consideration
purchase_status = postponed
barrier = size_uncertainty
information_need = reviews
decision_factor = size
potential_opportunity = better size/fit information

Therefore, design the system so that ONE conversation can contain MULTIPLE analytical signals.

Do not force all business meaning into a single primary_intent field.

==================================================
6. PROPOSED ANALYTICAL TAXONOMY
==================================================

Use the following as a starting framework, but inspect the existing data before finalizing it.

A. USER BEHAVIOR

Examples:

- wishlist
- purchase_intent
- purchase_completed
- purchase_postponed
- product_comparison
- recommendation_seeking
- product_research
- bookmarking

B. PURCHASE STAGE

Examples:

- discovery
- consideration
- shortlist
- purchase_intent
- post_purchase

C. PURCHASE BARRIERS

Examples:

- price
- size_uncertainty
- fit_uncertainty
- quality_uncertainty
- lack_of_reviews
- return_concern
- delivery_concern
- availability
- trust
- styling_uncertainty
- occasion_uncertainty

D. INFORMATION NEEDS

Examples:

- reviews
- size_information
- fit_information
- styling
- quality
- price_history
- discount_information
- availability
- alternatives
- social_validation
- product_comparison

E. DECISION FACTORS

Examples:

- price
- fit
- size
- style
- occasion
- quality
- reviews
- brand
- social_validation
- availability

F. PURCHASE OUTCOME / STATUS

Examples:

- purchased
- likely_to_purchase
- postponed
- abandoned
- uncertain

G. OPPORTUNITY AREA

Examples:

- better_size_guidance
- better_fit_information
- stronger_social_proof
- better_price_visibility
- better_product_comparison
- better_styling_guidance
- better_quality_information
- better_return_information

Do NOT assume these categories are correct simply because they are listed here.

Validate them against the actual conversations.

==================================================
7. RAG / RETRIEVAL REQUIREMENT
==================================================

The final discovery engine should use a retrieval-based architecture.

The system should retrieve relevant conversation evidence before generating an insight.

For example, if the user asks:

"Why do users wishlist products but not purchase them?"

The system should:

1. Understand the question.
2. Identify relevant analytical dimensions.
3. Retrieve relevant wishlist/purchase-hesitation conversations.
4. Group evidence by barriers/reasons.
5. Quantify the groups where possible.
6. Compare the groups.
7. Retrieve representative supporting conversations.
8. Generate a concise business insight.
9. Clearly distinguish evidence from interpretation.

The LLM must NOT simply invent an answer based on general knowledge.

Every important insight should be grounded in retrieved evidence from the dataset.

==================================================
8. QUANTIFICATION REQUIREMENT
==================================================

The engine must prioritize measurable insights.

For example, instead of:

"Users are concerned about price."

Prefer:

"Among 180 conversations identified as purchase-hesitation conversations, price-related concerns appeared in 49 conversations (27.2%)."

Then compare:

Price: 27.2%
Size/fit: 31.1%
Quality: 18.3%
Returns: 11.7%

IMPORTANT:

Always show:
- numerator
- denominator
- percentage

Do not calculate percentages using the entire dataset unless the entire dataset is actually the correct denominator.

Clearly state the population being analyzed.

==================================================
9. OPPORTUNITY DISCOVERY
==================================================

The engine should identify potential opportunity areas.

For example:

Opportunity:
SIZE/FIT CONFIDENCE

Evidence:
31% of relevant purchase-hesitation conversations mention size/fit uncertainty.

Observed behavior:
Users like the product but hesitate because they do not know whether it will fit.

Potential business implication:
Improving size/fit confidence may reduce purchase friction.

Supporting evidence:
Show representative conversations.

The system should NOT say:

"Improving size guidance will increase conversion by 31%."

That would be an unsupported causal claim.

==================================================
10. COMPARISON
==================================================

The engine must support comparisons such as:

- price vs size vs quality as purchase barriers
- wishlist users vs purchase-intent users
- different product categories
- different user segments
- different stages of the purchase journey
- different opportunity areas

Example output:

Opportunity | Mentions | Share | Potential relevance
-------------------------------------------------------
Size/Fit    | 140      | 31%   | High
Price       | 115      | 25%   | High
Quality     | 82       | 18%   | Medium
Returns     | 51       | 11%   | Medium

The ranking should be based on evidence, not arbitrary assumptions.

==================================================
11. USER SEGMENTATION
==================================================

Eventually, the engine should support comparisons across meaningful segments.

Potential segments may include:

- high purchase-intent users
- wishlist-heavy users
- price-sensitive users
- quality-conscious users
- comparison-oriented users
- research-heavy users

Do NOT create arbitrary demographic segments unless demographic data actually exists.

Prefer behavior-based segmentation.

==================================================
12. OUTPUT FORMAT
==================================================

The discovery engine should be capable of producing answers structured like:

QUESTION

"What prevents wishlisted products from being purchased?"

--------------------------------------------------

EXECUTIVE INSIGHT

The strongest observed barriers are size/fit uncertainty, price sensitivity and lack of product confidence.

--------------------------------------------------

QUANTIFIED FINDINGS

1. Size/Fit uncertainty
   140 / 450 relevant conversations
   31.1%

2. Price
   115 / 450
   25.6%

3. Quality uncertainty
   82 / 450
   18.2%

--------------------------------------------------

COMPARISON

Size/fit appears more frequently than price and quality concerns.

--------------------------------------------------

EVIDENCE

Show representative retrieved conversations.

--------------------------------------------------

POTENTIAL OPPORTUNITIES

1. Improve size/fit confidence
2. Improve price visibility
3. Improve product-quality/social-proof information

--------------------------------------------------

BUSINESS RELEVANCE

Explain how these opportunities could potentially reduce friction in the wishlist-to-purchase journey.

--------------------------------------------------

CONFIDENCE / LIMITATIONS

Clearly state:
- dataset size
- number of relevant conversations
- evidence coverage
- limitations
- whether the finding is correlational or merely observational

==================================================
13. IMPORTANT TECHNICAL PRINCIPLES
==================================================

Build this as a modular system.

Separate:

1. Data ingestion
2. Data cleaning
3. Labeling / classification
4. Behavioral signal extraction
5. Metadata generation
6. Embedding generation
7. Vector/semantic retrieval
8. Quantitative analysis
9. Evidence retrieval
10. LLM synthesis
11. Opportunity scoring
12. User interface

Do not tightly couple everything into one script.

==================================================
14. CURRENT PROJECT STAGE
==================================================

We are currently in the DATA VALIDATION / LABEL-QUALITY stage.

Do NOT jump directly into building the final RAG UI.

First:

1. Audit the existing 634-row labeled dataset.
2. Identify incorrect/questionable labels.
3. Determine whether the current labels can support the business questions.
4. Identify which additional behavioral dimensions need to be extracted.
5. Propose the final analytical schema.
6. Only after approval should we implement the next pipeline stage.

==================================================
15. NON-NEGOTIABLE RULE
==================================================

The objective is NOT to build a generic AI chatbot.

The objective is to build an evidence-grounded discovery engine that can:

IDENTIFY
→ QUANTIFY
→ COMPARE
→ EXPLAIN
→ SURFACE OPPORTUNITIES

around the Myntra wishlist-to-purchase journey.

Every technical decision should support that objective.

Before writing or modifying code, explain:
1. What you are changing.
2. Why it is necessary.
3. What business question it enables us to answer.
4. What output we should expect.

For now, perform ONLY the next required step and do not make speculative changes.
