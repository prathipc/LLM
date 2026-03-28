# LLM — Chapter 2 exercises

Small Python scripts based on *[LLMs from Scratch](https://github.com/rasbt/LLMs-from-scratch)* (Sebastian Raschka), Chapter 2: working with text data, simple tokenization, and a character/word-level vocabulary.

## Programs

### [`LLM-2.py`](.vscode/LLM/2/LLM-2.py)

- Downloads **`the-verdict.txt`** from the official course repo if it is missing (saved in the **current working directory** when you run the script).
- Loads the full text, prints length and a short preview.
- Tokenizes with a regex split on punctuation, `--`, and whitespace (separators are kept in the split output).
- Builds **sorted unique tokens**, prints vocabulary size and samples, then builds **`vocab`**: each token → integer ID.
- Prints the first 100 `(token, id)` pairs.

**Run** (from any directory; note where `the-verdict.txt` will appear):

```bash
pip install requests
python .vscode/LLM/2/LLM-2.py
```

### [`LLM-2.1.py`](.vscode/LLM/2/LLM-2.1.py)

- Downloads **`the-verdict.txt`** next to the script if missing (path-safe via `Path(__file__)`).
- Builds the same **`vocab`** from the corpus.
- Defines **`SimpleTokenizerV1`**: **`encode(text)`** → list of IDs, **`decode(ids)`** → string (with basic punctuation spacing cleanup).
- Demo: encodes and decodes a short sample sentence from the chapter.

**Run**:

```bash
pip install requests
python .vscode/LLM/2/LLM-2.1.py
```

## Requirements

- Python 3.8+ recommended (3.9+ if you use modern built-in type hints elsewhere).
- **`requests`** for downloading the sample text.

## Data file

`the-verdict.txt` is fetched at runtime and is listed in **`.gitignore`** so it is not committed. Both scripts can recreate it from the same upstream URL.

## License / attribution

Course text data and ideas follow the upstream project: [rasbt/LLMs-from-scratch](https://github.com/rasbt/LLMs-from-scratch).
