"""
ECLI Fetcher — Haalt uitspraken op van Rechtspraak.nl Open Data API.

Aanroepen:
    from modules.ecli_fetcher import haal_uitspraak_op
    
    resultaat = haal_uitspraak_op("ECLI:NL:HR:2023:1234")
    if resultaat["succes"]:
        tekst = resultaat["data"]
"""

import os
import requests
import xml.etree.ElementTree as ET
import streamlit as st
from urllib.parse import quote
from dotenv import load_dotenv

load_dotenv()


# ── Constanten ──────────────────────────────────────────────────────────────

# Rechtspraak.nl Open Data API - werkt!
CONTENT_URL = "https://data.rechtspraak.nl/uitspraken/content"

TIMEOUT_SECONDEN = 15
MAX_TEKENS = 12000

# XML namespaces voor Rechtspraak.nl
NAMESPACES = {
    'atom':    'http://www.w3.org/2005/Atom',
    'rs':      'http://www.rechtspraak.nl/schema/rechtspraak-1.0',
    'dc':      'http://purl.org/dc/elements/1.1/',
    'dcterms': 'http://purl.org/dc/terms/'
}


# ── Hulpfuncties ────────────────────────────────────────────────────────────

def haal_secret_op(sleutel: str) -> str:
    """Werkt lokaal via .env én op Streamlit Cloud via st.secrets."""
    try:
        return st.secrets[sleutel]       # Streamlit Cloud
    except Exception:
        # Fall back naar .env (KeyError, FileNotFoundError, AttributeError, etc.)
        return os.environ.get(sleutel, "")   # Lokaal


def _bereid_tekst_voor(tekst: str, max_tekens: int = MAX_TEKENS) -> str:
    """
    Kapt lange teksten af met intelligentie — zoekt naar puntgrens.
    
    Args:
        tekst: Originele tekst
        max_tekens: Maximum aantal tekens
    
    Returns:
        Afgekapte tekst (of origineel als korter dan max)
    """
    if len(tekst) <= max_tekens:
        return tekst
    
    afgekapt = tekst[:max_tekens]
    laatste_punt = afgekapt.rfind('.')
    
    # Snijd af op laatse punt als het niet te dicht bij het begin ligt
    if laatste_punt > max_tekens * 0.8:
        afgekapt = afgekapt[:laatste_punt + 1]
    
    return afgekapt + "\n\n[Tekst afgekort wegens lengte.]"


def _extract_text_from_xml(root: ET.Element) -> str:
    """
    Extracted tekst uit XML-element (inclusief alle child-elementen).
    
    Args:
        root: ET.Element om tekst uit te halen
    
    Returns:
        Gecombineerde tekstwaarde
    """
    text_parts = []
    
    if root.text and root.text.strip():
        text_parts.append(root.text.strip())
    
    for child in root:
        text_parts.append(_extract_text_from_xml(child))
        if child.tail and child.tail.strip():
            text_parts.append(child.tail.strip())
    
    return '\n'.join(filter(None, text_parts))


# ── Publieke Functies ────────────────────────────────────────────────────────

def haal_uitspraak_op(ecli: str) -> dict:
    """
    Haalt een uitspraaktekst op van Rechtspraak.nl via ECLI-nummer.
    
    Stappen:
      1. Valideert ECLI-format
      2. HTTP-request naar Rechtspraak.nl API
      3. Parse XML-response
      4. Extract uitspraaktekst
      5. Kapt af op MAX_TEKENS
    
    Args:
        ecli: ECLI-nummer bijv. "ECLI:NL:HR:2023:1234"
    
    Returns:
        {"succes": True, "data": uitspraak_tekst} of
        {"succes": False, "fout": "begrijpelijke melding"}
    """
    # Validatie: ECLI mag niet leeg zijn
    if not ecli or not ecli.strip():
        return {"succes": False, "fout": "Voer eerst een ECLI-nummer in."}
    
    ecli = ecli.strip()
    
    # Validatie: ECLI moet met "ECLI:" beginnen
    if not ecli.startswith("ECLI:"):
        return {"succes": False, "fout": "ECLI-nummer moet met 'ECLI:' beginnen."}
    
    try:
        # HTTP-request naar API — werkend endpoint
        url = f"{CONTENT_URL}?id={quote(ecli, safe='')}"
        
        response = requests.get(url, timeout=TIMEOUT_SECONDEN)
        
        if response.status_code == 404:
            return {
                "succes": False,
                "fout": f"ECLI '{ecli}' niet gevonden. "
                        f"Probeer een ander ECLI-nummer van rechtspraak.nl"
            }
        
        if response.status_code != 200:
            return {
                "succes": False,
                "fout": f"Rechtspraak.nl API error (status {response.status_code})"
            }
        
        # Parse XML
        root = ET.fromstring(response.content)
        
        # Het XML-format is: <open-rechtspraak><entry><content><rs:uitspraak>...</rs:uitspraak></content></entry></open-rechtspraak>
        # Zoek <rs:uitspraak> element in de hele boom
        uitspraak_elem = root.find('.//rs:uitspraak', NAMESPACES)
        
        if uitspraak_elem is None:
            # Fallback: probeer naar alle tekst in het XML
            tekst = _extract_text_from_xml(root)
        else:
            # Extract tekst uit uitspraak-element
            tekst = _extract_text_from_xml(uitspraak_elem)
        
        if not tekst or not tekst.strip():
            return {
                "succes": False,
                "fout": "Uitspraaktekst kon niet worden geëxtraheerd."
            }
        
        # Bereid tekst voor (afkapping)
        tekst = _bereid_tekst_voor(tekst.strip())
        
        return {"succes": True, "data": tekst}
    
    except requests.exceptions.Timeout:
        return {
            "succes": False,
            "fout": "De verbinding met Rechtspraak.nl duurde te lang. Probeer opnieuw."
        }
    except requests.exceptions.ConnectionError:
        return {
            "succes": False,
            "fout": "Kan niet verbinden met Rechtspraak.nl. Controleer je internetverbinding."
        }
    except ET.ParseError as e:
        return {
            "succes": False,
            "fout": f"XML-parse fout: {str(e)}"
        }
    except Exception as e:
        return {
            "succes": False,
            "fout": f"Er ging iets mis: {str(e)}"
        }
