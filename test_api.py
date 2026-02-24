"""
Test script om Rechtspraak.nl API te diagnosticeren
"""
import requests
from urllib.parse import quote

# Test verschillende endpoints
endpoints = [
    # Format 1: Direct uitspraak
    "https://data.rechtspraak.nl/uitspraken/uitspraak/ECLI:NL:HR:2019:128",
    # Format 2: XML endpoint
    "https://data.rechtspraak.nl/uitspraken/xml?ecli=ECLI:NL:HR:2019:128",
    # Format 3: Search API
    "https://data.rechtspraak.nl/uitspraken/structured-search?q=ECLI:NL:HR:2019:128",
    # Format 4: Content endpoint
    "https://data.rechtspraak.nl/uitspraken/content?id=ECLI:NL:HR:2019:128",
    # Format 5: OData
    "https://data.rechtspraak.nl/v1/uitspraken?$filter=ecli eq 'ECLI:NL:HR:2019:128'",
]

print("Testen Rechtspraak.nl API endpoints...\n")

for i, url in enumerate(endpoints, 1):
    print(f"[{i}] GET {url}")
    try:
        response = requests.get(url, timeout=5)
        print(f"    Status: {response.status_code}")
        print(f"    Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        if response.status_code == 200:
            # Print first 300 chars
            content_preview = response.text[:300] if response.text else "(leeg)"
            print(f"    Content preview: {content_preview}...")
        print()
    except Exception as e:
        print(f"    Error: {str(e)}\n")

# Ook testen met search API
print("\n" + "="*60)
print("Testen search API:")
print("="*60 + "\n")

search_url = "https://data.rechtspraak.nl/uitspraken/structured-search"
params = {
    "q": "BW",  # Simpel zoekterm
    "max": 5
}

print(f"GET {search_url}")
print(f"Params: {params}\n")

try:
    response = requests.get(search_url, params=params, timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
    if response.status_code == 200:
        content_preview = response.text[:500]
        print(f"Content preview:\n{content_preview}...")
except Exception as e:
    print(f"Error: {str(e)}")
