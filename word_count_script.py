import json
import re

filepath = "main.ipynb"

with open(filepath, "r", encoding="utf-8") as f:
    data = json.load(f)

word_count = 0

for cell in data["cells"]:
    if cell["cell_type"] == "markdown":
        content = cell["source"]
        for line in content:
            temp = [word for word in line.split() if "#" not in word] # we might need to filter for more markdown keywords here
            word_count = word_count + len(temp)

if word_count > 2500:
    print("TOO MANY WORDS! Please reduce the number of words to less than 2500.")
print(f"Liczba słów: {word_count}")