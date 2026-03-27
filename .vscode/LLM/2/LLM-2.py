import os
import requests
import re


print ("hello")
if not os.path.exists("the-verdict.txt"):
    print("the-verdict.txt does not exist")
    url = (
        "https://raw.githubusercontent.com/rasbt/"
        "LLMs-from-scratch/main/ch02/01_main-chapter-code/"
        "the-verdict.txt"
    )
    file_path = "the-verdict.txt"
    
    print ("url:", url)
    print (file_path)

    response = requests.get(url, timeout=30)
    response.raise_for_status()
    with open(file_path, "wb") as f:
        f.write(response.content)
    
with open("the-verdict.txt", "r", encoding="utf-8") as f:
    raw_text = f.read()
    
print("Total number of character:", len(raw_text))
print(raw_text[:99])

# Split on punctuation, double hyphen, or whitespace.
# Parentheses in the regex keep separators in the output.
preprocessed = re.split(r'([,.:;?_!"()\']|--|\s)', raw_text)
# Remove empty/whitespace-only tokens and trim surrounding spaces.

preprocessed = [item.strip() for item in preprocessed if item.strip()]

# Print the final cleaned token list.
print(preprocessed[:30])