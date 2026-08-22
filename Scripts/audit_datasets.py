import os
import sys
import glob
import pandas as pd
import json

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def run_data_audit():
    raw_dir = "Raw Data"
    processed_dir = "Processed Data"
    
    all_files = sorted(glob.glob(os.path.join(raw_dir, "*.csv")) + glob.glob(os.path.join(processed_dir, "*.csv")))
    
    audit_results = {
        "summary": {
            "total_files": len(all_files),
            "total_rows": 0,
        },
        "datasets": {}
    }
    
    print("==================================================")
    print("STARTING MULTI-DATASET QUALITY & LABEL AUDIT (PERFECTED)")
    print("==================================================\n")
    
    total_row_count = 0
    
    for file_path in all_files:
        basename = os.path.basename(file_path)
        folder = os.path.dirname(file_path)
        
        print(f"--- Analyzing [{folder}/{basename}] ---")
        
        try:
            # Check if dataset has explicit header or is headerless
            df_check = pd.read_csv(file_path, nrows=2)
            is_headerless = False
            
            # Check header content to see if pandas read a data row as header
            for col in df_check.columns:
                col_str = str(col)
                if "http" in col_str or "Google Play" in col_str or "App Store" in col_str or "635d5742" in col_str or "103afb18" in col_str or "a85e6753" in col_str:
                    is_headerless = True
                    break
                    
            if is_headerless:
                df = pd.read_csv(file_path, header=None)
                text_col_idx = 7 if df.shape[1] > 7 else (df.shape[1] - 3 if df.shape[1] >= 3 else 0)
                text_series = df.iloc[:, text_col_idx].fillna('').astype(str)
                primary_text_col = f"col_{text_col_idx}"
            else:
                df = pd.read_csv(file_path)
                if 'body' in df.columns or 'title' in df.columns:
                    title_s = df['title'].fillna('') if 'title' in df.columns else pd.Series(['']*len(df))
                    body_s = df['body'].fillna('') if 'body' in df.columns else pd.Series(['']*len(df))
                    context_s = df['post_context'].fillna('') if 'post_context' in df.columns else pd.Series(['']*len(df))
                    text_series = (title_s + " " + body_s + " " + context_s).str.strip()
                    primary_text_col = "title_plus_body"
                elif 'text' in df.columns:
                    text_series = df['text'].fillna('').astype(str)
                    primary_text_col = "text"
                elif 'comment' in df.columns:
                    text_series = df['comment'].fillna('').astype(str)
                    primary_text_col = "comment"
                else:
                    text_series = df.iloc[:, 0].fillna('').astype(str)
                    primary_text_col = df.columns[0]
                
            num_rows, num_cols = int(df.shape[0]), int(df.shape[1])
            total_row_count += num_rows
            
            non_null_count = int((text_series.str.strip().str.len() > 0).sum())
            null_count = int((text_series.str.strip().str.len() == 0).sum())
            dup_count = int(text_series.duplicated().sum()) if num_rows > 0 else 0
            
            char_lens = text_series.apply(len)
            word_counts = text_series.apply(lambda x: len(x.split()))
            
            file_stats = {
                "folder": folder,
                "file_name": basename,
                "rows": num_rows,
                "columns": num_cols,
                "is_headerless": is_headerless,
                "column_names": [str(c) for c in df.columns],
                "primary_text_column": primary_text_col,
                "valid_text_rows": non_null_count,
                "empty_text_rows": null_count,
                "duplicate_text_rows": dup_count,
                "duplicate_rate_pct": float(round((dup_count / num_rows * 100), 2)) if num_rows > 0 else 0.0,
                "avg_char_len": float(round(char_lens.mean(), 1)) if not char_lens.empty else 0.0,
                "median_word_count": int(word_counts.median()) if not word_counts.empty else 0,
                "min_word_count": int(word_counts.min()) if not word_counts.empty else 0,
                "max_word_count": int(word_counts.max()) if not word_counts.empty else 0
            }
            
            # Detailed label audit for labeled dataset
            if "labeled" in basename and 'primary_intent' in df.columns:
                intent_counts = df['primary_intent'].value_counts().to_dict()
                intent_shares = (df['primary_intent'].value_counts(normalize=True) * 100).round(2).to_dict()
                file_stats["labeled_intent_distribution"] = {
                    str(intent): {"count": int(count), "share_pct": float(intent_shares.get(intent, 0.0))}
                    for intent, count in intent_counts.items()
                }
                
                multi_signal_samples = []
                keywords_to_check = ['size', 'fit', 'review', 'price', 'wait', 'return', 'quality', 'bought', 'wishlist', 'discount', 'sale', 'coupons']
                for idx, row in df.iterrows():
                    txt = (str(row.get('title', '')) + " " + str(row.get('body', ''))).lower()
                    matched_kw = [kw for kw in keywords_to_check if kw in txt]
                    if len(matched_kw) >= 2:
                        multi_signal_samples.append({
                            "index": int(idx),
                            "primary_intent": str(row.get('primary_intent')),
                            "detected_keywords": matched_kw,
                            "text_snippet": txt[:140]
                        })
                file_stats["multi_signal_sample_count"] = len(multi_signal_samples)
                file_stats["sample_multi_signal_rows"] = multi_signal_samples[:10]
                
            audit_results["datasets"][basename] = file_stats
            print(f"   Rows: {num_rows} | Cols: {num_cols} | Valid Text: {non_null_count} | Dups: {dup_count} ({file_stats['duplicate_rate_pct']}%)")
            print(f"   Avg Char Len: {file_stats['avg_char_len']} | Median Words: {file_stats['median_word_count']}")
            if "labeled_intent_distribution" in file_stats:
                print("   Labeled Intents Breakdown:")
                for k, v in file_stats["labeled_intent_distribution"].items():
                    print(f"     - {k}: {v['count']} ({v['share_pct']}%)")
                print(f"   Multi-signal conversations detected: {file_stats['multi_signal_sample_count']} / {num_rows}")
            print()
            
        except Exception as e:
            print(f"   ERROR reading {file_path}: {e}\n")
            audit_results["datasets"][basename] = {"error": str(e)}
            
    audit_results["summary"]["total_rows"] = int(total_row_count)
    
    os.makedirs(processed_dir, exist_ok=True)
    report_path = os.path.join(processed_dir, "data_audit_results.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(audit_results, f, indent=2)
        
    print(f"==================================================")
    print(f"AUDIT COMPLETE: Processed {total_row_count} rows across {len(all_files)} files.")
    print(f"Saved audit findings to: {report_path}")
    print(f"==================================================")
    return audit_results

if __name__ == "__main__":
    run_data_audit()
