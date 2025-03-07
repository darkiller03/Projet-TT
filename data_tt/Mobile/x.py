import json

# Load the JSON file
with open("test.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Print the 'Contenu' of the first offer
print(data[2]["Contenu"])
