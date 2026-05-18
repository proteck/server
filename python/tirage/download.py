import os
import requests
from bs4 import BeautifulSoup
import pdfplumber
import csv
import re
import time

BASE_URL = "https://www.tirage.ch"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
OUTPUT_DIR = "resultats"
CSV_FILE = os.path.join(OUTPUT_DIR, "tous_les_resultats.csv")

def download_file(url, path):
    try:
        response = requests.get(url, headers=HEADERS, stream=True, timeout=30)
        if response.status_code == 200:
            with open(path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        else:
            print(f"    Failed to download {url}: Status {response.status_code}")
    except Exception as e:
        print(f"    Error downloading {url}: {e}")
    return False

def clean_text(text):
    if text is None:
        return ""
    return re.sub(r'\s+', ' ', str(text)).strip()

def parse_pdf(pdf_path, year, category):
    data = []
    is_group = "groupe" in category.lower() or "resume" in category.lower()
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                
                lines = text.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line or any(x in line for x in ["Page", "Samedi", "TIRAGE", "mercredi", "Classement", "Nom &", "Rang", "Filiation"]):
                        continue
                    
                    # Generic structure: [Classement] [Nom/Info] [HC?] [Resultat] [Details...]
                    # We try to identify the Rank (start) and Result (end or middle)
                    
                    parts = re.split(r'\s+', line)
                    if len(parts) < 2:
                        continue

                    classement = "N/A"
                    resultat = "N/A"
                    nom_prenom = ""
                    tires = ""
                    hc = "Non"

                    # Check if first part is a number (Classement)
                    if parts[0].isdigit():
                        classement = parts[0]
                        remaining = parts[1:]
                    else:
                        remaining = parts

                    # Check for HC
                    for i, p in enumerate(remaining):
                        if "HC" in p.upper():
                            hc = "Oui"
                            # We keep it in the string for now or remove it?
                            # Let's just mark it.

                    if is_group:
                        # Groups often have: Rank Name Total Details...
                        # Example: 1 Les Carabiniers 279 97 94 88 ...
                        if len(remaining) >= 2:
                            # Try to find the total score (first large number after name)
                            # This is tricky. Let's assume the first number after the name is the result.
                            name_parts = []
                            score_idx = -1
                            for i, p in enumerate(remaining):
                                if p.isdigit() and int(p) > 20: # Heuristic: score is likely > 20
                                    score_idx = i
                                    break
                                name_parts.append(p)
                            
                            nom_prenom = " ".join(name_parts)
                            if score_idx != -1:
                                resultat = remaining[score_idx]
                                tires = " ".join(remaining[score_idx+1:])
                    else:
                        # Individual: Rank Info HC? Result
                        # Example: 1 Roi du Tir SCHWEIZER Dominique Romeo 95
                        if len(remaining) >= 2:
                            # Result is usually the last number
                            if remaining[-1].isdigit():
                                resultat = remaining[-1]
                                name_info = " ".join(remaining[:-1])
                            else:
                                # Sometimes there's a date or something at the end? 
                                # Let's look for the last digit part
                                found = False
                                for i in range(len(remaining)-1, -1, -1):
                                    if remaining[i].isdigit():
                                        resultat = remaining[i]
                                        name_info = " ".join(remaining[:i])
                                        tires = " ".join(remaining[i+1:])
                                        found = True
                                        break
                                if not found:
                                    name_info = " ".join(remaining)
                            
                            # Clean name_info from common prefixes
                            nom_prenom = re.sub(r'^(Roi du Tir|[\d\.]+\s+Couronne)\s+', '', name_info, flags=re.IGNORECASE).strip()

                    data.append([year, category, nom_prenom, resultat, tires, hc, classement])
                    
    except Exception as e:
        print(f"    Error parsing {pdf_path}: {e}")
    return data

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    years = list(range(2003, 2020)) + list(range(2021, 2026))
    all_data = []

    for year in years:
        print(f"Processing year {year}...")
        year_dir = os.path.join(OUTPUT_DIR, str(year))
        if not os.path.exists(year_dir):
            os.makedirs(year_dir)

        urls_to_try = [
            f"{BASE_URL}/resultats-{year}/",
            f"{BASE_URL}/resultat-{year}/",
        ]
        if year == 2022:
            urls_to_try.append(f"{BASE_URL}/about-me/")
        
        soup = None
        current_url = ""
        for url in urls_to_try:
            try:
                response = requests.get(url, headers=HEADERS, timeout=30)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    current_url = url
                    print(f"  Found year {year} at {url}")
                    break
            except Exception as e:
                print(f"  Error checking {url}: {e}")
        
        if not soup:
            print(f"  Year {year} not found after trying {urls_to_try}")
            continue

        links = soup.find_all('a', href=re.compile(r'\.pdf$', re.IGNORECASE))
        
        if not links:
            print(f"  No PDF links found for year {year}")
        
        for link in links:
            pdf_url = link.get('href')
            if not pdf_url.startswith('http'):
                if pdf_url.startswith('/'):
                    pdf_url = BASE_URL + pdf_url
                else:
                    pdf_url = current_url + pdf_url
            
            link_text = clean_text(link.get_text())
            category = link_text
            if not category or category.lower() == "voir" or "pdf" in category.lower():
                prev = link.find_previous(['h1', 'h2', 'h3', 'h4', 'strong', 'p'])
                if prev:
                    category = clean_text(prev.get_text())
            
            if not category or len(category) < 3:
                category = "Classement"

            safe_category = re.sub(r'[\\/*?:"<>|]', "_", category)
            safe_category = safe_category[:50]
            filename = f"{year} - {safe_category}.pdf"
            pdf_path = os.path.join(year_dir, filename)

            if os.path.exists(pdf_path):
                print(f"  Skipping {filename} (already exists)")
            else:
                print(f"  Downloading {filename}...")
                download_file(pdf_url, pdf_path)
            
            if os.path.exists(pdf_path):
                print(f"  Parsing {filename}...")
                pdf_data = parse_pdf(pdf_path, year, category)
                all_data.extend(pdf_data)
            
            time.sleep(0.3)

    if all_data:
        print(f"Saving {len(all_data)} rows to {CSV_FILE}...")
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            header = ["Année", "Type de tir", "Nom et prénom", "Résultat", "Tires", "Hors concours", "Classement"]
            writer.writerow(header)
            writer.writerows(all_data)
    else:
        print("No data collected.")

    print(f"Finished! Results in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
