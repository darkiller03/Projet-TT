import json
import re

def clean_content(text):
    """Cleans extracted content by removing redundant newlines, extra spaces, and fixing spacing."""
    # Remove excessive newlines and whitespace
    text = re.sub(r'\n+', '\n', text).strip()

    # Remove repeated standalone words
    text = re.sub(r'(?m)^\s*(Divertissement|Services Divers)\s*$', '', text)  # Remove Internet Mobile" and change it with the SOUS-RUBRIQUE you want

    # Remove excessive spaces before punctuation
    text = re.sub(r'\s+([.,:;!?])', r'\1', text)

    # Normalize spaces in each line
    text = "\n".join(line.strip() for line in text.split("\n") if line.strip())

    return text

# Load the JSON file
with open("test.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Apply cleaning to each offer's "Contenu"
for offer in data:
    if "Contenu" in offer:
        offer["Contenu"] = clean_content(offer["Contenu"])

# Save the cleaned JSON back
with open("offres_cleaned.json", "w", encoding="utf-8") as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

print("✅ Cleaning complete! Saved as 'offres_cleaned.json'")
