import json
import os

def clean_dataset(file_path, output_path):
    cleaned = []
    dropped = 0
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            data = json.loads(line)
            text = data.get("output", "")
            
            # Remove English contamination (simple word matching)
            # Splitting text to match whole words and avoid false positives
            words = set(text.lower().split())
            if any(eng_word in words for eng_word in ["the", "is", "are", "and", "to", "in", "for", "of"]):
                dropped += 1
                continue
                
            # Ensure Chhattisgarhi markers
            if any(marker in text for marker in ["मिलथे", "होथे", "मन", "ला", "आथे", "जाथे", "करथे"]):
                cleaned.append(data)
            else:
                dropped += 1
                
    with open(output_path, "w", encoding="utf-8") as f:
        for item in cleaned:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
            
    print(f"✅ Cleaned dataset saved to {output_path}. Retained: {len(cleaned)}, Dropped: {dropped}")
    return cleaned

def generate_template_questions(schemes_file, output_path):
    # Try reading from schemes.json if it exists
    schemes = []
    if os.path.exists(schemes_file):
        try:
            with open(schemes_file, "r", encoding="utf-8") as f:
                schemes_data = json.load(f)
                if isinstance(schemes_data, dict):
                    # In case format is {"scheme_name": {...}}
                    schemes = list(schemes_data.keys())
                elif isinstance(schemes_data, list) and isinstance(schemes_data[0], dict):
                    # In case format is [{"name": "scheme_name"}, ...]
                    schemes = [s.get("name") for s in schemes_data if "name" in s]
        except Exception as e:
            print(f"Warning: Could not parse {schemes_file}: {e}")
    
    # Fallback to hardcoded list if empty
    if not schemes:
        schemes = [
            "राजीव गांधी किसान न्याय योजना",
            "प्रधानमंत्री किसान सम्मान निधि",
            "धान खरीदी योजना",
            "गोधन न्याय योजना",
            "महतारी वंदन योजना",
            "कृषक जीवन ज्योति योजना",
            "सौर सुजला योजना"
        ]

    # Smart templates based on variations
    questions = [
        "के लाभ का हे?",
        "म आवेदन कइसे करन?",
        "बर पात्रता का हे?",
        "के पैसा कब मिलथे?",
        "ला कइसे चालू करवावन?",
        "के सूची म नाम कइसे देखन?",
        "बर का का कागद लगथे?"
    ]

    generated_prompts = []
    for scheme in schemes:
        for q in questions:
            # Combine scheme name with the variation question
            generated_prompts.append(f"{scheme} {q}")
            
    with open(output_path, "w", encoding="utf-8") as f:
        for prompt in generated_prompts:
            f.write(prompt + "\n")
            
    print(f"✅ Generated {len(generated_prompts)} prompts across {len(schemes)} schemes.")
    print(f"✅ Saved to {output_path}")
    return generated_prompts

if __name__ == "__main__":
    # Base path logic assuming script is run from data/ or root
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Step 3: Clean Dataset
    input_jsonl = os.path.join(base_dir, "cg_instruction_dataset.jsonl")
    output_jsonl = os.path.join(base_dir, "cg_instruction_cleaned.jsonl")
    
    if os.path.exists(input_jsonl):
        print("--- STEP 3: Running Quality Filter ---")
        clean_dataset(input_jsonl, output_jsonl)
    else:
        print(f"File not found: {input_jsonl}. Skipping Step 3.")
    
    # Step 4: Generate Variants
    schemes_json = os.path.join(base_dir, "schemes.json")
    output_prompts = os.path.join(base_dir, "generated_scheme_prompts.txt")
    
    print("\n--- STEP 4: Running Template Multiplication ---")
    generate_template_questions(schemes_json, output_prompts)
    
    print("\n🚀 Next step: Feed the generated prompts to the LLM or your generation pipeline to get pure Chhattisgarhi responses!")
