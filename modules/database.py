"""
Database — Supabase PostgreSQL koppeling voor case briefs opslag.

Aanroepen:
    from modules.database import sla_case_brief_op, haal_case_briefs_op
    
    resultaat = sla_case_brief_op(case_brief_data)
    if resultaat["succes"]:
        print(f"Opgeslagen met ID: {resultaat['data']['id']}")
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
    except (KeyError, AttributeError):
        return os.environ.get(sleutel)   # Lokaal


def _maak_supabase_client() -> Client:
    """Initialiseer Supabase client."""
    return create_client(
        haal_secret_op("SUPABASE_URL"),
        haal_secret_op("SUPABASE_KEY")
    )


# ── Publieke Functies ────────────────────────────────────────────────────────

def sla_case_brief_op(case_brief: dict) -> dict:
    """
    Slaat een case brief op in Supabase (upsert op ECLI).
    
    Args:
        case_brief: Dict met velden uit database schema
    
    Returns:
        {"succes": True, "data": opgeslagen_record} of
        {"succes": False, "fout": "begrijpelijke melding"}
    """
    # TODO: Implementatie in Fase 3
    return {"succes": False, "fout": "Nog niet geïmplementeerd."}


def haal_case_briefs_op(filter_: dict = None) -> dict:
    """
    Haalt case briefs uit Supabase met optionele filters.
    
    Args:
        filter_: Optional dict met zoekvoorwaarden
    
    Returns:
        {"succes": True, "data": [case_briefs]} of
        {"succes": False, "fout": "begrijpelijke melding"}
    """
    # TODO: Implementatie in Fase 3
    return {"succes": False, "fout": "Nog niet geïmplementeerd."}
