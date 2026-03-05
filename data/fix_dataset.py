import json
import re
import os

def fix_cg_text(text: str) -> str:
    """Replaces common Hindi markers with CG markers using word boundaries."""
    
    # 1. 'के लिए' -> 'बर'
    text = re.sub(r'(?<![\u0900-\u097F])के लिए(?![\u0900-\u097F])', 'बर', text)
    
    # 2. 'में' -> 'म' (e.g. बैंक में -> बैंक म)
    text = re.sub(r'(?<![\u0900-\u097F])में(?![\u0900-\u097F])', 'म', text)
    
    # 3. 'से' -> 'ले' (e.g. गांव से -> गांव ले)
    text = re.sub(r'(?<![\u0900-\u097F])से(?![\u0900-\u097F])', 'ले', text)
    
    # 4. 'को' -> 'ला' (e.g. किसान को -> किसान ला)
    text = re.sub(r'(?<![\u0900-\u097F])को(?![\u0900-\u097F])', 'ला', text)
    
    # 5. 'द्वारा' -> 'ले' or 'डहर ले' (using 'ले' as a general replacement for 'by')
    text = re.sub(r'(?<![\u0900-\u097F])द्वारा(?![\u0900-\u097F])', 'ले', text)
    
    # 6. 'पर' -> 'म' (on -> in/on in CG)
    text = re.sub(r'(?<![\u0900-\u097F])पर(?![\u0900-\u097F])', 'म', text)
    
    return text

def fix_dataset(filepath: str):
    print(f"Applying fixes to {filepath}...")
    
    fixed_lines = []
    changes_made = 0
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            original = line.strip()
            if not original:
                continue
            
            try:
                data = json.loads(original)
                
                # Apply fixes to the text fields
                old_inst = data.get("instruction", "")
                old_out = data.get("output", "")
                
                new_inst = fix_cg_text(old_inst)
                new_out = fix_cg_text(old_out)
                
                if old_inst != new_inst or old_out != new_out:
                    changes_made += 1
                    
                data["instruction"] = new_inst
                data["output"] = new_out
                
                fixed_lines.append(json.dumps(data, ensure_ascii=False))
                
            except json.JSONDecodeError:
                # If it's not JSON, just do raw string replacement
                new_line = fix_cg_text(original)
                if new_line != original:
                    changes_made += 1
                fixed_lines.append(new_line)
                
    # Overwrite the file with the cleaned version
    with open(filepath, 'w', encoding='utf-8') as f:
        for line in fixed_lines:
            f.write(line + '\n')
            
    print(f"Done! Cleaned up {changes_made} entries.")

if __name__ == "__main__":
    target_file = r"d:\Chhattisgarhi chatbot\data\cg_government_schemes_1000_qa_dataset.jsonl"
    fix_dataset(target_file)
    print("\nRe-running validation to confirm purity...\n")
    os.system(f'python "{os.path.join(os.path.dirname(target_file), "validate_datasets.py")}"')
