import os
import sys
import pandas as pd

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def clean_additional_reddit_data():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_dir = os.path.join(project_root, "Raw Data")
    
    input_file = os.path.join(project_root, "Reddit-Myntra-additional-data.csv")
    existing_cleaned_file = os.path.join(raw_dir, "reddit_myntra_cleaned.csv")
    output_file = os.path.join(raw_dir, "reddit_myntra_additional_cleaned.csv")

    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input additional dataset not found at {input_file}")

    print("==================================================")
    print("STARTING REDDIT ADDITIONAL DATA CLEANING & NORMALIZATION")
    print("==================================================")
    
    df_new = pd.read_csv(input_file)
    print(f"Loaded {len(df_new)} rows from {os.path.basename(input_file)}")

    # Load existing IDs for deduplication
    existing_ids = set()
    if os.path.exists(existing_cleaned_file):
        df_exist = pd.read_csv(existing_cleaned_file)
        existing_ids = set(df_exist['id'].dropna().astype(str))
        print(f"Loaded {len(existing_ids)} existing record IDs for deduplication.")

    # Deduplicate by ID
    df_unique = df_new[~df_new['id'].astype(str).isin(existing_ids)].copy()
    print(f"Unique new records after ID deduplication: {len(df_unique)}")

    # Build post lookup map for post_context
    posts_dict = df_new[df_new['dataType'] == 'post'].set_index('id')
    post_context_map = {}
    for pid, post_row in posts_dict.iterrows():
        t = str(post_row.get('title') or '').strip()
        b = str(post_row.get('body') or '').strip()
        context_str = f"{t} {b}".strip()
        post_context_map[pid] = context_str

    target_columns = [
        'dataType', 'subredditName', 'postId', 'id', 'parentId',
        'createdAt', 'score', 'upVotes', 'title', 'body',
        'post_context', 'candidate_intents', 'contentUrl'
    ]

    cleaned_records = []
    for idx, row in df_unique.iterrows():
        d_type = str(row.get('dataType') or 'comment').strip()
        sub_name = str(row.get('communityName') or '').strip()
        post_id = str(row.get('postId') or '').strip() if pd.notnull(row.get('postId')) else ""
        rec_id = str(row.get('id') or '').strip()
        parent_id = str(row.get('parentId') or '').strip() if pd.notnull(row.get('parentId')) else ""
        
        c_date = str(row.get('commentCreatedAt') if d_type == 'comment' else row.get('createdAt'))
        if c_date == 'nan' or not c_date:
            c_date = str(row.get('createdAt') or '')

        score_val = row.get('score') if pd.notnull(row.get('score')) else 0
        upvotes_val = row.get('upVotes') if d_type == 'post' else row.get('commentUpVotes')
        if pd.isnull(upvotes_val):
            upvotes_val = score_val

        title_val = str(row.get('title') or '') if pd.notnull(row.get('title')) else ""
        body_val = str(row.get('body') or '') if pd.notnull(row.get('body')) else ""

        # Compute post_context
        if d_type == 'comment':
            p_context = post_context_map.get(post_id, title_val)
        else:
            p_context = f"{title_val} {body_val}".strip()

        content_url = str(row.get('contentUrl') or '') if pd.notnull(row.get('contentUrl')) else ""

        # Candidate intents heuristic
        combined_txt = f"{title_val} {body_val} {p_context}".lower()
        matched_cand = []
        if 'wishlist' in combined_txt: matched_cand.append('wishlist')
        if 'price' in combined_txt or 'discount' in combined_txt: matched_cand.append('price_drop')
        if 'sale' in combined_txt or 'eors' in combined_txt: matched_cand.append('sale_discount')
        if 'coupon' in combined_txt or 'myncash' in combined_txt: matched_cand.append('coupon')
        if 'size' in combined_txt or 'fit' in combined_txt: matched_cand.append('product_quality')
        if 'return' in combined_txt or 'refund' in combined_txt: matched_cand.append('cancellation_refund')
        if 'delivery' in combined_txt or 'ekart' in combined_txt: matched_cand.append('delivery')
        candidate_intents = ", ".join(matched_cand)

        cleaned_records.append({
            'dataType': d_type,
            'subredditName': sub_name,
            'postId': post_id,
            'id': rec_id,
            'parentId': parent_id,
            'createdAt': c_date,
            'score': score_val,
            'upVotes': upvotes_val,
            'title': title_val,
            'body': body_val,
            'post_context': p_context,
            'candidate_intents': candidate_intents,
            'contentUrl': content_url
        })

    df_cleaned = pd.DataFrame(cleaned_records, columns=target_columns)
    df_cleaned.to_csv(output_file, index=False, encoding='utf-8')

    print(f"[✓] Successfully cleaned {len(df_cleaned)} records.")
    print(f"[✓] Saved cleaned dataset to: {output_file}")
    print("==================================================")
    return output_file

if __name__ == "__main__":
    clean_additional_reddit_data()
