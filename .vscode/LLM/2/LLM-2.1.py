# LLM-2.1.py

import re
import requests
from pathlib import Path
from typing import Dict

SCRIPT_DIR = Path(__file__).resolve().parent
VERDICT_PATH = SCRIPT_DIR / "the-verdict.txt"


def ensure_verdict_file() -> None:
    if VERDICT_PATH.exists():
        return
    url = (
        "https://raw.githubusercontent.com/rasbt/"
        "LLMs-from-scratch/main/ch02/01_main-chapter-code/"
        "the-verdict.txt"
    )
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    VERDICT_PATH.write_bytes(response.content)


def build_vocab() -> Dict[str, int]:
    ensure_verdict_file()
    raw_text = VERDICT_PATH.read_text(encoding="utf-8")
    preprocessed = re.split(r'([,.:;?_!"()\']|--|\s)', raw_text)
    preprocessed = [item.strip() for item in preprocessed if item.strip()]
    all_words = sorted(set(preprocessed))
    return {token: i for i, token in enumerate(all_words)}


class SimpleTokenizerV1:
    def __init__(self, vocab):
        self.str_to_int = vocab
        self.int_to_str = {i: s for s, i in vocab.items()}

    def encode(self, text):
        preprocessed = re.split(r'([,.:;?_!"()\']|--|\s)', text)

        preprocessed = [
            item.strip() for item in preprocessed if item.strip()
        ]
        ids = [self.str_to_int[s] for s in preprocessed]
        return ids

    def decode(self, ids):
        text = " ".join([self.int_to_str[i] for i in ids])
        # Replace spaces before the specified punctuations
        text = re.sub(r'\s+([,.?!"()\'])', r"\1", text)
        return text


vocab = build_vocab()
tokenizer = SimpleTokenizerV1(vocab)
text = """"It's the last he painted, you know," 
           Mrs. Gisburn said with pardonable pride."""
ids = tokenizer.encode(text)
print(ids)
decoded = tokenizer.decode(ids)
print(decoded)
