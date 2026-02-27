"""
Database — Supabase PostgreSQL koppeling voor case briefs opslag.

Aanroepen:
    from modules.database import (
        sla_case_brief_op, haal_case_briefs_op,
        haal_top_tags_op, login_gebruiker, registreer_gebruiker,
        uitloggen, haal_huidige_gebruiker_op
    )

    resultaat = sla_case_brief_op(case_brief_data)
    if resultaat["succes"]:
        print(f"Opgeslagen met ID: {resultaat['data']['id']}")

    resultaat = haal_case_briefs_op(zoekterm="kelderluik")

    resultaat = login_gebruiker("email@voorbeeld.nl", "wachtwoord123")
    if resultaat["succes"]:
        gebruiker = resultaat["data"]
"""

import os
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()


# ── Constanten ──────────────────────────────────────────────────────────────

TABEL = "case_briefs"


# ── Hulpfuncties ────────────────────────────────────────────────────────────

def haal_secret_op(sleutel: str) -> str:
    """Werkt lokaal via .env én op Streamlit Cloud via st.secrets."""
    try:
        return st.secrets[sleutel]       # Streamlit Cloud
    except Exception:
        # Fall back naar .env (KeyError, FileNotFoundError, AttributeError, etc.)
        return os.environ.get(sleutel, "")   # Lokaal


def _maak_supabase_client() -> Client:
    """Initialiseer Supabase client."""
    url = haal_secret_op("SUPABASE_URL")
    key = haal_secret_op("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError(
            "SUPABASE_URL en SUPABASE_KEY moeten ingevuld zijn in .env"
        )
    
    return create_client(url, key)


# ── Publieke Functies ────────────────────────────────────────────────────────

def sla_case_brief_op(case_brief: dict) -> dict:
    """
    Slaat een case brief op in Supabase (upsert op ECLI).

    Als dezelfde ECLI al bestaat, wordt het geüpdatet.
    Vereist een ingelogde gebruiker (RLS).

    Args:
        case_brief: Dict met volgende velden:
            - ecli (verplicht): ECLI-nummer
            - titel (verplicht): Titel van de zaak
            - feiten, partijen, rechtsvraag, overwegingen, dictum, belang: Case brief velden
            - wetsartikelen: List van wetsartikelen
            - eigen_tags: List van tags (optioneel)
            - eigen_notities: User notities (optioneel)

    Returns:
        {"succes": True, "data": opgeslagen_record} of
        {"succes": False, "fout": "begrijpelijke melding"}
    """
    # Validatie: verplichte velden
    if not case_brief.get("ecli"):
        return {"succes": False, "fout": "ECLI-nummer is verplicht."}

    if not case_brief.get("titel"):
        return {"succes": False, "fout": "Titel is verplicht."}

    try:
        client = _maak_auth_client()

        # Haal ingelogde gebruiker op (vereist voor RLS)
        try:
            user_response = client.auth.get_user()
            user_id = user_response.user.id if user_response and user_response.user else None
        except Exception:
            user_id = None

        if not user_id:
            return {
                "succes": False,
                "fout": "Je moet ingelogd zijn om uitspraken op te slaan. Log in via de zijbalk."
            }

        # Zet defaults voor optionele velden
        data_to_save = {
            "ecli": case_brief.get("ecli"),
            "titel": case_brief.get("titel"),
            "feiten": case_brief.get("feiten", ""),
            "partijen": case_brief.get("partijen", ""),
            "rechtsvraag": case_brief.get("rechtsvraag", ""),
            "overwegingen": case_brief.get("overwegingen", ""),
            "dictum": case_brief.get("dictum", ""),
            "belang": case_brief.get("belang", ""),
            "wetsartikelen": case_brief.get("wetsartikelen", []),
            "eigen_tags": case_brief.get("eigen_tags", []),
            "eigen_notities": case_brief.get("eigen_notities", ""),
            "user_id": user_id,
        }

        # Upsert: update als ECLI al bestaat, anders insert
        response = client.table(TABEL).upsert(
            data_to_save,
            on_conflict="ecli"
        ).execute()
        
        if not response.data or len(response.data) == 0:
            return {
                "succes": False,
                "fout": "Opslaan mislukt — geen response van database"
            }
        
        return {
            "succes": True,
            "data": response.data[0]
        }
    
    except Exception as e:
        error_msg = str(e)
        
        if "connection" in error_msg.lower():
            fout = "Kan niet verbinden met database. Controleer je internetverbinding."
        elif "auth" in error_msg.lower() or "key" in error_msg.lower():
            fout = "Database authenticatie fout. Controleer SUPABASE_KEY."
        else:
            fout = f"Database error: {error_msg}"
        
        return {"succes": False, "fout": fout}


def haal_case_briefs_op(
    zoekterm: str = "",
    tags_filter: list = None,
    limit: int = 50
) -> dict:
    """
    Haalt case briefs uit Supabase met optionele zoeken en filteren.
    
    Strategie:
      1. Als zoekterm: full-text search in titel, feiten, rechtsvraag
      2. Als tags_filter: filter op eigen_tags (contains)
      3. Combineer beide filters (AND logic)
    
    Args:
        zoekterm: Zoekstring (optioneel)
        tags_filter: List van tags om op te filteren (optioneel)
        limit: Max resultaten (default 50)
    
    Returns:
        {"succes": True, "data": [case_briefs]} of
        {"succes": False, "fout": "begrijpelijke melding"}
    """
    try:
        client = _maak_auth_client()

        # Start met basis query
        query = client.table(TABEL).select("*")
        
        # Filter 1: Zoekterm
        if zoekterm and zoekterm.strip():
            zoekterm = zoekterm.strip().lower()
            # Voer search uit op meerdere velden + tags
            # Supabase ondersteunt text_search maar we gebruiken ilike (case-insensitive like)
            or_filter = (
                f"eigen_tags.cs.{{{zoekterm}}},"
                f"titel.ilike.%{zoekterm}%,"
                f"feiten.ilike.%{zoekterm}%,"
                f"rechtsvraag.ilike.%{zoekterm}%,"
                f"overwegingen.ilike.%{zoekterm}%,"
                f"belang.ilike.%{zoekterm}%,"
                f"eigen_notities.ilike.%{zoekterm}%"
            )
            query = query.or_("".join(or_filter))
        
        # Filter 2: Tags
        if tags_filter and len(tags_filter) > 0:
            # Supabase GIN-index queries via contains
            for tag in tags_filter:
                query = query.contains("eigen_tags", [tag])
        
        # Limit en sorteer op meest recent
        response = query.order("bijgewerkt_op", desc=True).limit(limit).execute()
        
        if not response.data:
            return {
                "succes": True,
                "data": [],
                "bericht": "Geen case briefs gevonden."
            }
        
        return {
            "succes": True,
            "data": response.data
        }
    
    except Exception as e:
        error_msg = str(e)
        
        if "connection" in error_msg.lower():
            fout = "Kan niet verbinden met database."
        elif "auth" in error_msg.lower():
            fout = "Database authenticatie fout."
        else:
            fout = f"Database error: {error_msg}"
        
        return {"succes": False, "fout": fout}


def haal_case_brief_op_ecli(ecli: str) -> dict:
    """
    Haalt één case brief op via ECLI.
    
    Args:
        ecli: ECLI-nummer
    
    Returns:
        {"succes": True, "data": case_brief} of
        {"succes": False, "fout": "..."}
    """
    if not ecli:
        return {"succes": False, "fout": "ECLI-nummer is verplicht."}

    try:
        client = _maak_auth_client()
        response = (
            client.table(TABEL)
            .select("*")
            .eq("ecli", ecli)
            .limit(1)
            .execute()
        )

        if not response.data:
            return {"succes": False, "fout": "Geen case brief gevonden."}

        return {"succes": True, "data": response.data[0]}

    except Exception as e:
        return {"succes": False, "fout": f"Ophalen mislukt: {str(e)}"}


def haal_alle_tags_op() -> dict:
    """
    Haalt alle unieke tags uit de database (voor dropdown).
    
    Returns:
        {"succes": True, "data": ["tag1", "tag2", ...]} of
        {"succes": False, "fout": "..."}
    """
    try:
        client = _maak_auth_client()

        # Haal alle case briefs met tags
        response = client.table(TABEL).select("eigen_tags").execute()

        # Verzamel alle unieke tags
        alle_tags = set()
        for record in response.data:
            if record.get("eigen_tags"):
                alle_tags.update(record["eigen_tags"])
        
        return {
            "succes": True,
            "data": sorted(list(alle_tags))
        }
    
    except Exception as e:
        return {
            "succes": False,
            "fout": f"Kan tags niet ophalen: {str(e)}"
        }


def haal_top_tags_op(limit: int = 5) -> dict:
    """
    Haalt de meest gebruikte tags op (gesorteerd op frequentie).

    Args:
        limit: Aantal tags om terug te geven (default 5)

    Returns:
        {"succes": True, "data": ["tag1", "tag2", ...]} of
        {"succes": False, "fout": "..."}
    """
    try:
        client = _maak_auth_client()
        response = client.table(TABEL).select("eigen_tags").execute()

        # Tel frequentie van elke tag
        tag_teller: dict = {}
        for record in response.data:
            for tag in (record.get("eigen_tags") or []):
                tag_teller[tag] = tag_teller.get(tag, 0) + 1

        # Sorteer op frequentie (hoog naar laag) en neem top N
        gesorteerd = sorted(tag_teller.items(), key=lambda x: x[1], reverse=True)
        top_tags = [tag for tag, _ in gesorteerd[:limit]]

        return {"succes": True, "data": top_tags}

    except Exception as e:
        return {"succes": False, "fout": f"Kan top tags niet ophalen: {str(e)}"}


def _maak_auth_client() -> Client:
    """
    Maakt een Supabase client met herstelde auth-sessie uit Streamlit session state.
    Gebruik dit voor geverifieerde database-operaties.
    """
    client = _maak_supabase_client()
    access_token = st.session_state.get("auth_access_token")
    refresh_token = st.session_state.get("auth_refresh_token", "")
    if access_token:
        try:
            client.auth.set_session(access_token, refresh_token)
        except Exception:
            pass  # Verlopen sessie — anoniem blijven
    return client


def login_gebruiker(email: str, wachtwoord: str) -> dict:
    """
    Logt een gebruiker in via Supabase Auth.

    Args:
        email: E-mailadres van de gebruiker
        wachtwoord: Wachtwoord van de gebruiker

    Returns:
        {"succes": True, "data": {"email": ..., "access_token": ..., "refresh_token": ...}} of
        {"succes": False, "fout": "..."}
    """
    try:
        client = _maak_supabase_client()
        response = client.auth.sign_in_with_password(
            {"email": email, "password": wachtwoord}
        )

        if not response.session:
            return {"succes": False, "fout": "Login mislukt. Controleer je e-mail en wachtwoord."}

        return {
            "succes": True,
            "data": {
                "email": response.user.email,
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token
            }
        }
    except Exception as e:
        error_msg = str(e)
        if "Invalid login credentials" in error_msg:
            fout = "Onjuist e-mailadres of wachtwoord."
        elif "Email not confirmed" in error_msg:
            fout = "E-mailadres nog niet bevestigd. Controleer je inbox."
        else:
            fout = f"Inloggen mislukt: {error_msg}"
        return {"succes": False, "fout": fout}


def registreer_gebruiker(email: str, wachtwoord: str) -> dict:
    """
    Registreert een nieuwe gebruiker via Supabase Auth.

    Args:
        email: E-mailadres van de nieuwe gebruiker
        wachtwoord: Wachtwoord (minimaal 6 tekens)

    Returns:
        {"succes": True, "data": {"bevestiging_vereist": bool}} of
        {"succes": False, "fout": "..."}
    """
    if len(wachtwoord) < 6:
        return {"succes": False, "fout": "Wachtwoord moet minimaal 6 tekens bevatten."}

    try:
        client = _maak_supabase_client()
        response = client.auth.sign_up(
            {"email": email, "password": wachtwoord}
        )
        bevestiging_vereist = response.session is None

        return {
            "succes": True,
            "data": {"bevestiging_vereist": bevestiging_vereist}
        }
    except Exception as e:
        error_msg = str(e)
        if "already registered" in error_msg or "already exists" in error_msg:
            fout = "Dit e-mailadres is al geregistreerd."
        else:
            fout = f"Registratie mislukt: {error_msg}"
        return {"succes": False, "fout": fout}


def uitloggen() -> dict:
    """
    Logt de huidige gebruiker uit via Supabase Auth.

    Returns:
        {"succes": True} of {"succes": False, "fout": "..."}
    """
    try:
        client = _maak_auth_client()
        client.auth.sign_out()
        return {"succes": True}
    except Exception as e:
        return {"succes": False, "fout": f"Uitloggen mislukt: {str(e)}"}


def haal_huidige_gebruiker_op() -> dict:
    """
    Haalt de huidige ingelogde gebruiker op uit de Supabase-sessie.

    Returns:
        {"succes": True, "data": {"email": "..."}} of {"succes": False, "fout": "..."}
    """
    try:
        client = _maak_auth_client()
        response = client.auth.get_user()
        if response and response.user:
            return {"succes": True, "data": {"email": response.user.email}}
        return {"succes": False, "fout": "Geen actieve sessie."}
    except Exception as e:
        return {"succes": False, "fout": f"Gebruiker ophalen mislukt: {str(e)}"}


def verwijder_case_brief(ecli: str) -> dict:
    """
    Verwijdert een case brief uit de database.

    Args:
        ecli: ECLI-nummer van de case brief

    Returns:
        {"succes": True, "data": deleted_record} of
        {"succes": False, "fout": "..."}
    """
    try:
        client = _maak_auth_client()

        response = client.table(TABEL).delete().eq("ecli", ecli).execute()
        
        return {
            "succes": True,
            "data": response.data
        }
    
    except Exception as e:
        return {
            "succes": False,
            "fout": f"Verwijderen mislukt: {str(e)}"
        }
