import requests
from bs4 import BeautifulSoup
import json

# Domaine principal
base_url = "https://www.tunisietelecom.tn"

# URL des Offres Prépayées
prepaid_url = base_url + "/particulier/divertissement/services-divers" # Changer le lien pour chaque sous-rubrique

# Liste des offres existantes
offers = [
    # Changer les offres pour chaque sous-rubrique
     "larecettebytt",
  "udaily",
  "clubprivilegesbytt",
  "yahalawabytt",
  "tthealthy",
  "tapinfo",
  "smsjob",
  "quizperso"
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

        # Chercher toutes les sections contenant des tableaux
        tables_data = {}
        tables = page_soup.find_all("table")

        if tables:
            for idx, table in enumerate(tables, start=1):
                rows = []
                headers = [th.text.strip() for th in table.find_all("th")]

                # Récupérer les données des lignes du tableau
                for row in table.find_all("tr")[1:]:  # Ignorer l'en-tête
                    values = [td.text.strip() for td in row.find_all("td")]
                    if values:
                        rows.append(dict(zip(headers, values)))

                tables_data[f"Tableau_{idx}"] = rows

        # Ajouter aux résultats
        results.append({
            "URL": full_url,
            "RUBRIQUE": "Divertissement", # Changer la rubrique pour chaque rubrique
            "SOUS-RUBRIQUE": "Services Divers", # Changer la sous-rubrique pour chaque sous-rubrique
            "Offre": title.get_text(strip=True) if title else offer.upper(),
            "Contenu": page_content if page_content else "Contenu non trouvé",
            "Tableau": tables_data if tables_data else "N/A"
        })

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur d'accès : {e}")
        results.append({
            "URL": full_url,
            "RUBRIQUE": "Divertissement", # Changer la rubrique pour chaque rubrique
            "SOUS-RUBRIQUE": "Services Divers", # Changer la sous-rubrique pour chaque sous-rubrique
            "Offre": offer.upper(),
            "Contenu": f"Erreur d'accès : {e}",
            "Tableau": "N/A"
        })

# Sauvegarder les résultats dans un fichier JSON
with open("test.json", "w", encoding="utf-8") as json_file:
    json.dump(results, json_file, ensure_ascii=False, indent=4)

print("✅ Extraction terminée ! Résultats enregistrés dans 'test.json'.")
