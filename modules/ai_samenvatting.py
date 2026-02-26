"""
AI Samenvatting — Analyseert uitspraken met Groq/Llama 3.3 70B.

Aanroepen:
    from modules.ai_samenvatting import genereer_case_brief, stel_vraag_over_uitspraak

    resultaat = genereer_case_brief(uitspraak_tekst, ecli)
    if resultaat["succes"]:
        case_brief = resultaat["data"]

    resultaat = stel_vraag_over_uitspraak(uitspraak_tekst, ecli, "Is er sprake van eigen schuld?")
    if resultaat["succes"]:
        antwoord = resultaat["data"]
"""

import os
import json
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

load_dotenv()


# ── Constanten ──────────────────────────────────────────────────────────────

MODEL = "llama-3.3-70b-versatile"
MAX_TOKENS = 1500
TEMPERATURE = 0.1


# ── Hulpfuncties ────────────────────────────────────────────────────────────

def haal_secret_op(sleutel: str) -> str:
    """Werkt lokaal via .env én op Streamlit Cloud via st.secrets."""
    try:
        return st.secrets[sleutel]       # Streamlit Cloud
    except Exception:
        # Fall back naar .env (KeyError, FileNotFoundError, AttributeError, etc.)
        return os.environ.get(sleutel, "")   # Lokaal


def _maak_groq_client() -> Groq:
    """Initialiseer Groq client met API-sleutel."""
    api_key = haal_secret_op("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY niet gevonden in .env of st.secrets")
    return Groq(api_key=api_key)


def _bouw_systeem_prompt() -> str:
    """
    Bouwt de systeem-prompt voor Case Brief generatie.
    Dit instruceert Llama hoe het moet antwoorden.
    """
    return """Je bent een expert in Nederlands recht en juridische analyse.
Je taak is om Nederlandse rechtsuitsspraken samen te vatten in een Case Brief.

Analyseer de gegeven uitspraak en extraheer ALTIJD een JSON met deze velden:
{
    "feiten": "Korte beschrijving van de feiten (1-2 alinea's)",
    "partijen": "Partijen in de zaak",
    "rechtsvraag": "De centrale juridische vraag",
    "overwegingen": "Belangrijkste overwegingen van de rechter",
    "dictum": "De uitspraak/beslissing zelf",
    "belang": "Waarom deze zaak juridisch relevant is",
    "wetsartikelen": ["BW artikel X", "BW artikel Y"]
}

VEREIST:
- Antwoord UITSLUITEND in JSON-formaat, niets anders
- Alle velden moeten in Nederlands zijn
- Zorg dat de JSON geldig is
- Wees bondig maar volledig"""


def _bouw_gebruiker_prompt(ecli: str, tekst: str) -> str:
    """
    Bouwt de gebruiker-prompt met de uitspraak.
    
    Args:
        ecli: ECLI-nummer
        tekst: Uitspraaktekst
    
    Returns:
        Prompt voor AI
    """
    return f"""Analyseer deze rechtsuitsraak en genereer een Case Brief:

ECLI: {ecli}

UITSPRAAK:
{tekst}"""


# ── Publieke Functies ────────────────────────────────────────────────────────

def genereer_case_brief(tekst: str, ecli: str) -> dict:
    """
    Genereert een case brief van een uitspraak via Groq/Llama AI.
    
    Stappen:
      1. Groq client initialisatie
      2. Systeem- en gebruiker-prompts bouwen
      3. API-aanroep naar Llama 3.3 70B
      4. JSON-response parsen
      5. Validatie van velden
    
    Args:
        tekst: Volledige uitspraaktekst
        ecli: ECLI-nummer voor referentie
    
    Returns:
        {"succes": True, "data": case_brief_dict} of
        {"succes": False, "fout": "begrijpelijke melding"}
    
    case_brief_dict bevat:
        - feiten, partijen, rechtsvraag, overwegingen, dictum, belang, wetsartikelen
    """
    # Validatie
    if not tekst or not tekst.strip():
        return {"succes": False, "fout": "Uitspraaktekst mag niet leeg zijn."}
    
    if not ecli or not ecli.strip():
        return {"succes": False, "fout": "ECLI-nummer mag niet leeg zijn."}
    
    try:
        # Groq client
        client = _maak_groq_client()
        
        # Prompts
        systeem_prompt = _bouw_systeem_prompt()
        gebruiker_prompt = _bouw_gebruiker_prompt(ecli, tekst)
        
        # API-aanroep
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": systeem_prompt},
                {"role": "user", "content": gebruiker_prompt}
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            response_format={"type": "json_object"}  # Forceer JSON-output
        )
        
        # Parse response
        response_text = completion.choices[0].message.content
        case_brief = json.loads(response_text)
        
        # Validatie: controleer of alle verplichte velden aanwezig zijn
        verplichte_velden = ["feiten", "partijen", "rechtsvraag", "overwegingen", 
                            "dictum", "belang", "wetsartikelen"]
        
        voor_missende = [v for v in verplichte_velden if v not in case_brief]
        if voor_missende:
            return {
                "succes": False,
                "fout": f"Case Brief mist velden: {', '.join(voor_missende)}"
            }
        
        return {"succes": True, "data": case_brief}
    
    except json.JSONDecodeError as e:
        return {
            "succes": False,
            "fout": f"AI gaf geen geldige JSON terug: {str(e)}"
        }
    except ValueError as e:
        # GROQ_API_KEY ontbreekt
        return {
            "succes": False,
            "fout": f"API-configuratie fout: {str(e)}"
        }
    except Exception as e:
        # Catch-all voor Groq API errors
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            fout = "GROQ_API_KEY is ongeldig. Controleer je .env-bestand."
        elif "429" in error_msg or "rate limit" in error_msg.lower():
            fout = "Groq rate limit bereikt. Probeer over enkele seconden opnieuw."
        elif "timeout" in error_msg.lower():
            fout = "AI-verwerking duurde te lang. Probeer opnieuw."
        else:
            fout = f"Groq API error: {error_msg}"
        
        return {"succes": False, "fout": fout}


def stel_vraag_over_uitspraak(tekst: str, ecli: str, vraag: str) -> dict:
    """
    Beantwoordt een ja/nee-vraag over een uitspraak.

    Args:
        tekst: Volledige uitspraaktekst
        ecli: ECLI-nummer voor referentie
        vraag: De ja/nee-vraag van de gebruiker

    Returns:
        {"succes": True, "data": {
            "antwoord": "Ja" of "Nee",
            "rechtsoverweging_nr": "r.o. 4.3",
            "citaat": "exact citaat uit uitspraak",
            "toelichting": "korte juridische toelichting"
        }} of
        {"succes": False, "fout": "begrijpelijke melding"}
    """
    if not tekst or not tekst.strip():
        return {"succes": False, "fout": "Uitspraaktekst is leeg."}
    if not vraag or not vraag.strip():
        return {"succes": False, "fout": "Voer een vraag in."}

    try:
        client = _maak_groq_client()

        systeem_prompt = """Je bent een juridische assistent gespecialiseerd in Nederlands recht.
Beantwoord de ja/nee-vraag over de gegeven uitspraak op basis van de tekst.

Geef ALTIJD een JSON terug met exact deze velden:
{
    "antwoord": "Ja" of "Nee",
    "rechtsoverweging_nr": "bijv. r.o. 4.3 of overweging 5.2 (leeg als niet van toepassing)",
    "citaat": "letterlijk citaat uit de uitspraak dat het antwoord onderbouwt",
    "toelichting": "korte juridische toelichting (1-2 zinnen) waarom ja of nee"
}

VEREIST:
- Antwoord UITSLUITEND in JSON-formaat, niets anders
- Alle velden in het Nederlands
- Citaat is een letterlijk citaat uit de uitspraak, geen parafrase
- Als het antwoord niet in de uitspraak te vinden is, zeg dan Nee met toelichting"""

        gebruiker_prompt = f"""Uitspraak (ECLI: {ecli}):
{tekst[:8000]}

Vraag: {vraag.strip()}"""

        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": systeem_prompt},
                {"role": "user", "content": gebruiker_prompt}
            ],
            temperature=0.1,
            max_tokens=600,
            response_format={"type": "json_object"}
        )

        response_text = completion.choices[0].message.content
        resultaat = json.loads(response_text)

        verplichte = ["antwoord", "rechtsoverweging_nr", "citaat", "toelichting"]
        missend = [v for v in verplichte if v not in resultaat]
        if missend:
            return {
                "succes": False,
                "fout": f"Antwoord mist velden: {', '.join(missend)}"
            }

        return {"succes": True, "data": resultaat}

    except json.JSONDecodeError:
        return {"succes": False, "fout": "AI gaf geen geldig antwoord terug."}
    except ValueError as e:
        return {"succes": False, "fout": f"API-configuratie fout: {str(e)}"}
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            fout = "GROQ_API_KEY is ongeldig. Controleer je .env-bestand."
        elif "429" in error_msg or "rate limit" in error_msg.lower():
            fout = "Groq rate limit bereikt. Probeer over enkele seconden opnieuw."
        elif "timeout" in error_msg.lower():
            fout = "AI-verwerking duurde te lang. Probeer opnieuw."
        else:
            fout = f"Groq API error: {error_msg}"
        return {"succes": False, "fout": fout}
