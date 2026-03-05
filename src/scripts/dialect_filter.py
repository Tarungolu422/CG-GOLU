import json
import os

# Extensive dictionary mapping from Bhojpuri/Maithili/Hindi to pure Chhattisgarhi
replacements = {
    "एह": "ए",
    "एतय": "इहाँ",
    "ओतय": "ओतका",
    "काहाँ": "कइँहा",
    "तोहर": "तोर",
    "हमनी": "हमन",
    "रउआ": "तें",
    "जाइत": "जाथे",
    "अछि": "हे",
    "गेल": "गे",
    "में": "म",
    "को": "ला",
    "और": "अऊ",
    "नहीं": "नइ",
    "लोग": "मन",
    "बनवाओल": "बनाय",
    "होइत": "होथे",
    "कहल": "कहे",
    "आवत": "आथे",
    "सँ": "ले",
    "जतय": "जिहाँ",
    "लेल": "बर",
    "कयल": "करे"
}

def correct_dialect(text):
    """Polishes text replacing standard/impure dialects with pure rural Chhattisgarhi."""
    for wrong, correct in replacements.items():
        text = text.replace(wrong, correct)
    return text

def process_dataset(input_file, output_file):
    print(f"Processing dataset from {input_file} to {output_file}...")
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return
        
    with open(input_file, "r", encoding="utf-8") as infile, \
         open(output_file, "w", encoding="utf-8") as outfile:
        
        count = 0
        for line in infile:
            if not line.strip():
                continue
            data = json.loads(line)
            data["output"] = correct_dialect(data["output"])
            outfile.write(json.dumps(data, ensure_ascii=False) + "\n")
            count += 1
            
    print(f"Successfully processed {count} lines into pure Chhattisgarhi.")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "..", "data")
    
    in_file = os.path.join(data_dir, "cg_raw.jsonl")
    out_file = os.path.join(data_dir, "cg_cleaned.jsonl")
    
    process_dataset(in_file, out_file)
