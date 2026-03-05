import re

def check_dialect_purity(text: str) -> dict:
    """
    Checks a given text for Chhattisgarhi dialect purity by identifying
    forbidden Hindi/Bhojpuri markers and counting positive CG markers.
    
    Returns a dictionary with:
    - 'is_pure': boolean
    - 'forbidden_words_found': list of strings
    - 'positive_markers_found': list of strings
    """
    if not text:
        return {"is_pure": True, "forbidden_words_found": [], "positive_markers_found": []}

    cg_markers = ['म', 'ले', 'बर', 'ला', 'मन', 'करथे', 'जाथे', 'मिलथे', 'होथे', 'आथे', 'खाथे', 'आइस', 'रहिस', 'बनाय गे', 'अऊ', 'घलो', 'अब्बड़', 'झन']
    bhojpuri_hindi_markers = ['एह', 'एकटा', 'जतय', 'जाइत', 'अछि', 'बनायल', 'लेल', 'सँ', 'बनेलनि', ' में ', ' से ', ' को ', ' के लिए ', 'द्वारा', 'पर']

    forbidden_found = []
    for m in bhojpuri_hindi_markers:
        marker = m.strip()
        # Use regex to find exact word matches to avoid substring firing (e.g. 'से' inside 'कइसे')
        # We need to account for Devanagari word boundaries
        if re.search(r'(?<![\u0900-\u097F])' + re.escape(marker) + r'(?![\u0900-\u097F])', text):
            forbidden_found.append(marker)

    positive_found = []
    words = text.split()
    for m in cg_markers:
        if m in words:
            positive_found.append(m)
            
    return {
        "is_pure": len(forbidden_found) == 0,
        "forbidden_words_found": forbidden_found,
        "positive_markers_found": positive_found
    }
