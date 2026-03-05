import os
import json
import csv
import re
import glob

def check_text(text: str, bhojpuri_hindi_markers: list) -> list:
    forbidden_found = []
    for m in bhojpuri_hindi_markers:
        marker = m.strip()
        if re.search(r'(?<![\u0900-\u097F])' + re.escape(marker) + r'(?![\u0900-\u097F])', text):
            forbidden_found.append(marker)
    return forbidden_found

def check_file(filepath: str, bhojpuri_hindi_markers: list):
    results = {"total": 0, "contains_negative": 0, "issues": []}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        if filepath.endswith('.csv'):
            reader = csv.reader(f)
            try:
                next(reader) # skip header
            except StopIteration:
                pass
            for line_num, row in enumerate(reader, 2):
                if not row: continue
                results["total"] += 1
                cg_word = row[0]
                found_negatives = check_text(cg_word, bhojpuri_hindi_markers)
                if found_negatives:
                    results["contains_negative"] += 1
                    results["issues"].append(f"Line {line_num} contains {found_negatives}: {cg_word}")
        else: # json or jsonl
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line: continue
                
                # Handle standard json format line
                if filepath.endswith('.json'):
                    text = line
                elif '{"instruction"' in line:
                    line = line[line.find('{'):]
                    try:
                        data = json.loads(line)
                        text = data.get("instruction", "") + " " + data.get("output", "")
                    except json.JSONDecodeError:
                        text = line
                else:
                    text = line

                results["total"] += 1
                found_negatives = check_text(text, bhojpuri_hindi_markers)
                if found_negatives:
                    results["contains_negative"] += 1
                    results["issues"].append(f"Line {line_num} contains {found_negatives}: {text[:150]}...")
                    
    return results

if __name__ == "__main__":
    print("\n🚀 Initiating comprehensive dialect check for ALL datasets...")
    bhojpuri_hindi_markers = ['एह', 'एकटा', 'जतय', 'जाइत', 'अछि', 'बनायल', 'लेल', 'सँ', 'बनेलनि', ' में ', ' से ', ' को ', ' के लिए ', 'द्वारा', 'पर']
    
    total_entries_corpus = 0
    total_contaminated_corpus = 0
    
    data_dir = os.path.dirname(os.path.abspath(__file__))
    files = []
    for ext in ["*.jsonl", "*.json", "*.csv"]:
        files.extend(glob.glob(os.path.join(data_dir, ext)))
        
    for filepath in files:
        # skip this python script itself and anything else that's not data
        filename = os.path.basename(filepath)
        if filename in ["schemes.json", "tourism.json"]: 
            # These are raw context data, not direct instruction sets, but we can check them too.
            pass
            
        print(f"--- Checking {filename} ---")
        res = check_file(filepath, bhojpuri_hindi_markers)
        print(f"Total valid entries: {res['total']}")
        print(f"Entries with negative markers: {res['contains_negative']}")
        if res['contains_negative'] > 0:
             print(f"  -> WARNING: {filename} holds {res['contains_negative']} contamination cases.")
        print("\n")
        
        total_entries_corpus += res['total']
        total_contaminated_corpus += res['contains_negative']

    purity = ((total_entries_corpus - total_contaminated_corpus) / total_entries_corpus) * 100 if total_entries_corpus > 0 else 0
    print("="*50)
    print("📊 CORPUS AGGREGATE RESULTS")
    print("="*50)
    print(f"Total Rows Evaluated: {total_entries_corpus}")
    print(f"Total Contaminated:   {total_contaminated_corpus}")
    print(f"Overall Corpus Purity: {purity:.2f}%\n")
