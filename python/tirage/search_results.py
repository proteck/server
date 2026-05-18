import csv
import os
from tabulate import tabulate
from collections import defaultdict

CSV_FILE = "resultats/tous_les_resultats.csv"

def search_person(name):
    if not os.path.exists(CSV_FILE):
        print(f"Erreur : Le fichier {CSV_FILE} n'existe pas. Veuillez d'abord lancer le script de scraping.")
        return

    results_by_type = defaultdict(list)
    search_name = name.lower()

    with open(CSV_FILE, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if search_name in row['Nom et prénom'].lower():
                shoot_type = row['Type de tir']
                # On garde les colonnes pertinentes pour l'affichage
                results_by_type[shoot_type].append([
                    row['Année'],
                    row['Classement'],
                    row['Nom et prénom'],
                    row['Résultat'],
                    row['Tires'],
                    row['Hors concours']
                ])

    if not results_by_type:
        print(f"\nAucun résultat trouvé pour '{name}'.")
        return

    print(f"\nRésultats trouvés pour '{name}' :\n")
    
    headers = ["Année", "Rang", "Nom et Prénom", "Score", "Détails/Tires", "HC"]
    
    # Affichage par type de tir
    for shoot_type, rows in sorted(results_by_type.items()):
        print(f"=== {shoot_type} ===")
        # Tri par année décroissante
        rows.sort(key=lambda x: x[0], reverse=True)
        print(tabulate(rows, headers=headers, tablefmt="grid"))
        print("\n")

if __name__ == "__main__":
    print("--- Recherche de scores Tirage Payerne ---")
    nom = input("Entrez le nom de la personne à rechercher : ").strip()
    if nom:
        search_person(nom)
    else:
        print("Nom invalide.")
