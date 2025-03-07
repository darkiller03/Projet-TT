import requests
from bs4 import BeautifulSoup
import json

# Domaine principal
base_url = "https://www.tunisietelecom.tn"

# URL des Offres Prépayées
prepaid_url = base_url + "/particulier/mobile/international-roaming"  # Changer le lien pour chaque sous-rubrique

# Liste des offres existantes
offers = [  # Changer les offres pour chaque sous-rubrique
    "linternational",
    "passroamingdata",
    "smartroaming"
]

# Liste pour stocker les résultats
results = []

# Scraper chaque offre prépayée
for offer in offers:
    full_url = f"{prepaid_url}/{offer}"
    print(f"🔍 Scraping : {full_url}")

    try:
        # Récupérer le contenu de la page
        page_response = requests.get(full_url, timeout=10)
        page_response.raise_for_status()  # Lève une erreur en cas de problème HTTP
        page_soup = BeautifulSoup(page_response.text, "html.parser")

        # Extraire le titre principal
        title = page_soup.find("h1")
        if not title:
            title = page_soup.find("title")

        # Extraire le contenu
        paragraphs = page_soup.find_all("main")
        page_content = "\n".join(p.text.strip() for p in paragraphs if p.text.strip())

        # Ajouter aux résultats
        results.append({
            "URL": full_url,
            "RUBRIQUE": "Mobile",
            "SOUS-RUBRIQUE": "International & Roaming", # Changer la sous-rubrique pour chaque sous-rubrique
            "Offre": title.get_text(strip=True) if title else offer.upper(),
            "Contenu": page_content if page_content else "Contenu non trouvé",
            "Tableau": "N/A"
        })

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur d'accès : {e}")
        results.append({
            "URL": full_url,
            "RUBRIQUE": "Mobile",
            "SOUS-RUBRIQUE": "International & Roaming", # Changer la sous-rubrique pour chaque sous-rubrique
            "Offre": offer.upper(),
            "Contenu": f"Erreur d'accès : {e}",
            "Tableau": "N/A"
        })

# Sauvegarder les résultats dans un fichier JSON
with open("offres.json", "w", encoding="utf-8") as json_file:
    json.dump(results, json_file, ensure_ascii=False, indent=4)

print("✅ Extraction terminée ! Résultats enregistrés dans 'offres.json'.")
