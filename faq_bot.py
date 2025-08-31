import json
import difflib
import re

# Load FAQ data
with open("faq.json", "r", encoding="utf-8") as f:
    faq_data = json.load(f)

def normalize(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)   # keep only letters/numbers/spaces
    s = re.sub(r"\s+", " ", s).strip()  # collapse spaces
    return s

# very small stopword list to avoid matching on "what/do/you/..."
STOPWORDS = {
    "a","an","the","what","when","where","who","which","how","is","are","am",
    "i","you","we","they","do","does","did","your","my","our","of","for","to",
    "in","on","with","and","or"
}

def tokens(s: str):
    return [t for t in normalize(s).split() if t not in STOPWORDS]

questions = [item["question"] for item in faq_data]
norm_questions = [normalize(q) for q in questions]

def find_answer(user_q: str) -> str:
    uq_norm = normalize(user_q)

    # 1) Fuzzy string similarity against full question text
    best_idx = None
    best_ratio = 0.0
    for i, nq in enumerate(norm_questions):
        ratio = difflib.SequenceMatcher(None, uq_norm, nq).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_idx = i
    if best_ratio >= 0.60:   # threshold; tweak 0.55–0.70 if needed
        return faq_data[best_idx]["answer"]

    # 2) Token Jaccard overlap as fallback
    uq_tokens = set(tokens(user_q))
    best_idx = None
    best_score = 0.0
    for i, q in enumerate(questions):
        qt = set(tokens(q))
        if not qt:
            continue
        score = len(uq_tokens & qt) / len(uq_tokens | qt)
        if score > best_score:
            best_score = score
            best_idx = i
    if best_score >= 0.30 and best_idx is not None:
        return faq_data[best_idx]["answer"]

    return "Sorry, I couldn't find an answer to that."

print("FAQ Bot is running... (type 'exit' to quit)")
while True:
    try:
        user_q = input("Customer: ")
    except (EOFError, KeyboardInterrupt):
        break
    if user_q.strip().lower() in {"exit", "quit"}:
        break
    print("Bot:", find_answer(user_q))
