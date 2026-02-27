import os
import re
from datetime import datetime
from uuid import uuid4
from urllib.parse import quote
import streamlit as st
from dotenv import load_dotenv
from modules.ecli_fetcher import haal_uitspraak_op
from modules.ai_samenvatting import genereer_case_brief, stel_vraag_over_uitspraak
from modules.database import (
    sla_case_brief_op,
    haal_case_briefs_op,
    haal_top_tags_op,
    haal_alle_tags_op,
    haal_case_brief_op_ecli,
    verwijder_case_brief,
    login_gebruiker,
    registreer_gebruiker,
    uitloggen,
)

# Load .env eerst (voor lokale testing zonder Streamlit secrets)
load_dotenv()


# ── PAGE CONFIG ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Caseflow",
    page_icon="⚖️",
    layout="wide"
)

# ── CUSTOM CSS — Editorial Legal Design ──────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,400&display=swap');

/* ── CSS Variabelen ── */
:root {
    --cf-navy: #0a1628;
    --cf-navy-light: #111d33;
    --cf-navy-mid: #162240;
    --cf-gold: #c9a227;
    --cf-gold-light: #e8c84a;
    --cf-gold-dim: rgba(201, 162, 39, 0.12);
    --cf-text: #e8e6e1;
    --cf-text-muted: #8e99a9;
    --cf-surface: #0f1a2e;
    --cf-border: rgba(201, 162, 39, 0.15);
    --cf-radius: 12px;
    --cf-shadow: 0 2px 16px rgba(0,0,0,0.25);
}

/* ── Basis ── */
.stApp {
    background: linear-gradient(165deg, var(--cf-navy) 0%, #0d1f3c 40%, var(--cf-navy) 100%) !important;
    color: var(--cf-text) !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Typografie ── */
h1, h2, h3, .stTabs [data-baseweb="tab"] {
    font-family: 'DM Serif Display', serif !important;
    color: var(--cf-text) !important;
    letter-spacing: -0.02em;
}

h1 {
    font-size: 2.6rem !important;
    background: linear-gradient(135deg, var(--cf-gold) 0%, var(--cf-gold-light) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    padding-bottom: 0.2em;
}

h2 {
    font-size: 1.6rem !important;
    border-bottom: 2px solid var(--cf-border);
    padding-bottom: 0.4em;
    margin-bottom: 1em;
}

h3 { font-size: 1.25rem !important; }

p, li, label, .stMarkdown, .stCaption, span {
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--cf-navy-light) 0%, var(--cf-navy) 100%) !important;
    border-right: 1px solid var(--cf-border) !important;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: var(--cf-gold) !important;
    -webkit-text-fill-color: var(--cf-gold) !important;
    background: none !important;
    font-size: 1.2rem !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--cf-navy-mid) !important;
    border-radius: var(--cf-radius) !important;
    padding: 4px !important;
    gap: 4px;
    border: 1px solid var(--cf-border) !important;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    padding: 10px 20px !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
    color: var(--cf-text-muted) !important;
    transition: all 0.2s ease !important;
}

.stTabs [aria-selected="true"] {
    background: var(--cf-gold-dim) !important;
    color: var(--cf-gold) !important;
    border-bottom: none !important;
}

.stTabs [data-baseweb="tab-highlight"] {
    display: none !important;
}

.stTabs [data-baseweb="tab-border"] {
    display: none !important;
}

/* ── Knoppen ── */
.stButton > button {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    border: 1px solid var(--cf-border) !important;
    background: var(--cf-navy-mid) !important;
    color: var(--cf-text) !important;
    padding: 0.5rem 1.2rem !important;
    transition: all 0.25s ease !important;
    letter-spacing: 0.01em;
}

.stButton > button:hover {
    background: var(--cf-gold-dim) !important;
    border-color: var(--cf-gold) !important;
    color: var(--cf-gold-light) !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(201, 162, 39, 0.15) !important;
}

.stButton > button[kind="primary"],
button[kind="primary"] {
    background: linear-gradient(135deg, var(--cf-gold) 0%, #b8922a 100%) !important;
    color: var(--cf-navy) !important;
    border: none !important;
    font-weight: 700 !important;
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, var(--cf-gold-light) 0%, var(--cf-gold) 100%) !important;
    color: var(--cf-navy) !important;
}

/* ── Input-velden ── */
.stTextInput > div > div,
.stTextArea > div > div,
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: var(--cf-navy-mid) !important;
    border: 1px solid var(--cf-border) !important;
    border-radius: 8px !important;
    color: var(--cf-text) !important;
    transition: border-color 0.2s ease !important;
}

.stTextInput > div > div:focus-within,
.stTextArea > div > div:focus-within {
    border-color: var(--cf-gold) !important;
    box-shadow: 0 0 0 2px rgba(201, 162, 39, 0.1) !important;
}

/* ── Expanders ── */
.streamlit-expanderHeader {
    font-family: 'DM Serif Display', serif !important;
    font-size: 1.05rem !important;
    background: var(--cf-navy-mid) !important;
    border: 1px solid var(--cf-border) !important;
    border-radius: var(--cf-radius) !important;
    padding: 0.8em 1em !important;
    transition: all 0.2s ease !important;
}

.streamlit-expanderHeader:hover {
    border-color: var(--cf-gold) !important;
}

.streamlit-expanderContent {
    background: rgba(15, 26, 46, 0.6) !important;
    border: 1px solid var(--cf-border) !important;
    border-top: none !important;
    border-radius: 0 0 var(--cf-radius) var(--cf-radius) !important;
    padding: 1em !important;
}

/* ── Alerts (success, error, warning, info) ── */
.stAlert {
    border-radius: 8px !important;
    border-left: 4px solid var(--cf-gold) !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: var(--cf-navy-mid) !important;
    border: 1px solid var(--cf-border) !important;
    border-radius: var(--cf-radius) !important;
    padding: 1em !important;
    text-align: center;
}

[data-testid="stMetricValue"] {
    font-family: 'DM Serif Display', serif !important;
    color: var(--cf-gold) !important;
    font-size: 2rem !important;
}

/* ── Divider ── */
hr {
    border-color: var(--cf-border) !important;
    opacity: 0.5;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: var(--cf-navy); }
::-webkit-scrollbar-thumb { background: var(--cf-navy-mid); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--cf-gold); }

/* ── Radio buttons ── */
.stRadio > div {
    gap: 0.3rem;
}

.stRadio [role="radiogroup"] label {
    background: var(--cf-navy-mid) !important;
    border: 1px solid var(--cf-border) !important;
    border-radius: 8px !important;
    padding: 6px 16px !important;
    transition: all 0.2s ease !important;
}

.stRadio [role="radiogroup"] label:hover {
    border-color: var(--cf-gold) !important;
}

/* ── Sliders ── */
.stSlider [data-baseweb="slider"] [role="slider"] {
    background: var(--cf-gold) !important;
}

.stSlider [data-baseweb="slider"] div[data-testid="stTickBarMin"],
.stSlider [data-baseweb="slider"] div[data-testid="stTickBarMax"] {
    color: var(--cf-text-muted) !important;
}

/* ── Download button ── */
.stDownloadButton > button {
    background: var(--cf-gold-dim) !important;
    border: 1px solid var(--cf-gold) !important;
    color: var(--cf-gold-light) !important;
}

/* ── Code blocks ── */
.stCodeBlock {
    border: 1px solid var(--cf-border) !important;
    border-radius: var(--cf-radius) !important;
}

/* ── Spinner ── */
.stSpinner > div {
    border-top-color: var(--cf-gold) !important;
}

/* ── Animatie: fade-in bij laden ── */
@keyframes cfFadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}

.main .block-container {
    animation: cfFadeIn 0.4s ease-out;
    max-width: 1100px;
}

/* ── Subtiele grain-overlay voor diepte ── */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.03'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 0;
}
</style>
""", unsafe_allow_html=True)


# ── HULPFUNCTIES ──────────────────────────────────────────────────────────────

# BWBR-nummers per wet (voor directe artikel-links op wetten.overheid.nl)
_BW_BOEK_BWBR = {
    "1": "BWBR0002656",
    "2": "BWBR0003045",
    "3": "BWBR0005291",
    "4": "BWBR0002761",
    "5": "BWBR0005288",
    "6": "BWBR0005289",
    "7": "BWBR0005290",
    "8": "BWBR0005287",
}

_WETBOEK_BWBR = {
    "Rv":   "BWBR0001827",   # Wetboek van Burgerlijke Rechtsvordering
    "WvSr": "BWBR0001854",   # Wetboek van Strafrecht
    "Sr":   "BWBR0001854",
    "WvSv": "BWBR0001903",   # Wetboek van Strafvordering
    "Sv":   "BWBR0001903",
    "Gw":   "BWBR0001840",   # Grondwet
    "Awb":  "BWBR0005537",   # Algemene wet bestuursrecht
    "AWB":  "BWBR0005537",
}


def maak_wetsartikel_url(artikel: str) -> str:
    """
    Genereert een directe URL naar het artikel op wetten.overheid.nl.
    Herkent BW X:Y (bijv. BW 6:162) en andere wetboeken (bijv. Rv 36).
    Valt terug op zoek-URL als het artikel niet herkend wordt.
    """
    tekst = artikel.strip()

    # BW: patroon "6:162" → boek 6, artikel 162
    if "BW" in tekst:
        match = re.search(r'(\d+):(\d+)', tekst)
        if match:
            boek, nummer = match.group(1), match.group(2)
            bwbr = _BW_BOEK_BWBR.get(boek)
            if bwbr:
                return f"https://wetten.overheid.nl/{bwbr}/2026-01-01#Artikel{nummer}"

    # Andere wetboeken: zoek code + eerste artikelnummer
    for code, bwbr in _WETBOEK_BWBR.items():
        if code in tekst:
            rest = tekst.replace(code, "")
            match = re.search(r'(\d+[a-z]?)', rest)
            if match:
                nummer = match.group(1)
                return f"https://wetten.overheid.nl/{bwbr}/2026-01-01#Artikel{nummer}"

    # Fallback: zoek-URL
    zoekterm = tekst.replace(":", " ")
    return f"https://wetten.overheid.nl/zoeken?zoekterm={quote(zoekterm)}"


# Bekende wetboek-codes en hun volledige naam
_WETBOEK_NAMEN = {
    "BW": "Burgerlijk Wetboek",
    "WvSr": "Wetboek van Strafrecht",
    "Sr": "Wetboek van Strafrecht",
    "WvSv": "Wetboek van Strafvordering",
    "Sv": "Wetboek van Strafvordering",
    "Rv": "Burgerlijke Rechtsvordering",
    "Gw": "Grondwet",
    "Awb": "Algemene wet bestuursrecht",
    "AWB": "Algemene wet bestuursrecht",
    "WOR": "Wet op de ondernemingsraden",
    "WW": "Werkloosheidswet",
    "ROW": "Rijksoctrooiwet",
    "BBA": "Buitengewoon Besluit Arbeidsverhoudingen",
}


def _parse_wetsartikel(artikel: str) -> dict:
    """Parseert een wetsartikel-string naar code, wetboeknaam en artikelnummer."""
    tekst = artikel.strip()
    for code, naam in _WETBOEK_NAMEN.items():
        if code in tekst:
            rest = tekst.replace(code, "").replace("artikel", "").strip(" :-")
            return {"code": code, "naam": naam, "artikel": rest or tekst}
    return {"code": "", "naam": "", "artikel": tekst}


def _toon_wetsartikelen_grid(wetsartikelen: list):
    """Toont wetsartikelen in een 3-koloms grid met wetboek-naam en link."""
    cols = st.columns(3)
    for idx, artikel in enumerate(wetsartikelen):
        info = _parse_wetsartikel(artikel)
        url = maak_wetsartikel_url(artikel)
        with cols[idx % 3]:
            if info["naam"]:
                st.markdown(
                    f"**{info['code']}** art. {info['artikel']}  \n"
                    f"<small>{info['naam']}</small>  \n"
                    f"[↗ wetten.overheid.nl]({url})",
                    unsafe_allow_html=True
                )
            else:
                st.markdown(f"[{artikel}]({url})")


def _wis_sessie_volledig():
    """Wist alle session state keys inclusief widget-keys."""
    auth_keys = {
        k: st.session_state[k]
        for k in ["auth_email", "auth_access_token", "auth_refresh_token"]
        if k in st.session_state
    }
    for sleutel in list(st.session_state.keys()):
        del st.session_state[sleutel]
    # Herstel auth-sessie zodat gebruiker ingelogd blijft
    st.session_state.update(auth_keys)
    # Expliciet ECLI-invoerveld leegmaken
    st.session_state["ecli_input"] = ""


# ── SIDEBAR: GEBRUIKERSPROFIELEN ──────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 👤 Mijn Account")

    ingelogd_email = st.session_state.get("auth_email")

    if ingelogd_email:
        st.success(f"Ingelogd als:\n**{ingelogd_email}**")
        if st.button("🚪 Uitloggen", use_container_width=True):
            uitloggen()
            for sleutel in ["auth_email", "auth_access_token", "auth_refresh_token"]:
                st.session_state.pop(sleutel, None)
            st.rerun()
    else:
        auth_keuze = st.radio(
            "Kies actie",
            ["Inloggen", "Registreren"],
            horizontal=True,
            label_visibility="collapsed"
        )

        auth_email = st.text_input(
            "E-mailadres",
            placeholder="naam@voorbeeld.nl",
            key="auth_email_input"
        )
        auth_wachtwoord = st.text_input(
            "Wachtwoord",
            type="password",
            key="auth_wachtwoord_input"
        )

        if auth_keuze == "Inloggen":
            if st.button("🔑 Inloggen", use_container_width=True):
                if auth_email and auth_wachtwoord:
                    with st.spinner("Inloggen..."):
                        resultaat = login_gebruiker(auth_email, auth_wachtwoord)
                    if resultaat["succes"]:
                        st.session_state["auth_email"] = resultaat["data"]["email"]
                        st.session_state["auth_access_token"] = resultaat["data"]["access_token"]
                        st.session_state["auth_refresh_token"] = resultaat["data"]["refresh_token"]
                        st.rerun()
                    else:
                        st.error(f"❌ {resultaat['fout']}")
                else:
                    st.warning("⚠️ Vul e-mail en wachtwoord in.")
        else:
            if st.button("📝 Registreren", use_container_width=True):
                if auth_email and auth_wachtwoord:
                    with st.spinner("Account aanmaken..."):
                        resultaat = registreer_gebruiker(auth_email, auth_wachtwoord)
                    if resultaat["succes"]:
                        if resultaat["data"]["bevestiging_vereist"]:
                            st.info(
                                "✅ Account aangemaakt! Controleer je inbox om je "
                                "e-mailadres te bevestigen."
                            )
                        else:
                            st.success("✅ Account aangemaakt! Je kunt nu inloggen.")
                    else:
                        st.error(f"❌ {resultaat['fout']}")
                else:
                    st.warning("⚠️ Vul e-mail en wachtwoord in.")

        st.caption("Geen account? Gebruik 'Registreren' om er een aan te maken.")

    st.divider()
    st.caption("⚖️ Caseflow v0.5")


# ── HEADER ────────────────────────────────────────────────────────────────────

st.title("⚖️ Caseflow")
st.markdown(
    "Gratis web-app voor Nederlandse rechtsstudenten — "
    "uitspraken begrijpen, opslaan en toepassen."
)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📄 Nieuwe Uitspraak",
    "🔍 Kennisbank Doorzoeken",
    "📚 Casus Uitwerken",
    "🛠️ Admin"
])


# ── TAB 1: ECLI INPUT & CASE BRIEF ───────────────────────────────────────────

with tab1:
    st.header("📄 Uitspraak Analyseren")

    # Input sectie
    col1, col2 = st.columns([3, 1])

    with col1:
        ecli_input = st.text_input(
            label="ECLI-nummer",
            placeholder="bijv. ECLI:NL:HR:2002:AE7040",
            help="Het ECLI-nummer van een Nederlandse rechtsuitspraak.",
            key="ecli_input"
        )

    with col2:
        st.write("")  # Uitlijning
        analyze_button = st.button(
            "🔍 Analyseer",
            use_container_width=True,
            key="analyze_button"
        )

    # Reset-knop — wist ook het ECLI-invoerveld
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        if st.button("🔄 Reset", use_container_width=True, key="reset_button"):
            _wis_sessie_volledig()
            st.rerun()

    st.divider()

    # Analyse-logica
    if analyze_button:
        if not ecli_input or not ecli_input.strip():
            st.warning("⚠️ Voer eerst een ECLI-nummer in.")
        else:
            ecli = ecli_input.strip()

            # Stap 1: Haal uitspraak op van Rechtspraak.nl
            with st.spinner("⏳ Uitspraak ophalen van Rechtspraak.nl..."):
                fetch_result = haal_uitspraak_op(ecli)

            if not fetch_result["succes"]:
                st.error(f"❌ {fetch_result['fout']}")
            else:
                uitspraak_tekst = fetch_result["data"]

                # Stap 2: Genereer Case Brief met AI
                with st.spinner(
                    "🤖 AI analyseert de uitspraak... (dit kan 10-30 seconden duren)"
                ):
                    brief_result = genereer_case_brief(uitspraak_tekst, ecli)

                if not brief_result["succes"]:
                    st.error(f"❌ {brief_result['fout']}")
                else:
                    case_brief = brief_result["data"]
                    st.session_state["laatste_case_brief"] = case_brief
                    st.session_state["laatste_ecli"] = ecli
                    st.session_state["laatste_uitspraak_tekst"] = uitspraak_tekst
                    # Wis eventuele eerdere opgeslagen status
                    st.session_state.pop("tags_notities_opgeslagen", None)
                    st.session_state.pop("laatste_vraag_antwoord", None)
                    st.success("✅ Case Brief gegenereerd!")

    # Toon Case Brief uit session state
    laatste_case_brief = st.session_state.get("laatste_case_brief")
    laatste_ecli = st.session_state.get("laatste_ecli")
    laatste_tekst = st.session_state.get("laatste_uitspraak_tekst", "")

    if laatste_case_brief and laatste_ecli:
        case_brief = laatste_case_brief
        ecli = laatste_ecli

        # ── Case Brief weergave ──
        st.subheader("📋 Case Brief")
        st.caption(f"ECLI: `{ecli}`")

        col1, col2 = st.columns(2)

        with col1:
            with st.expander("📌 Feiten", expanded=True):
                st.markdown(case_brief.get("feiten", "N/A"))

            with st.expander("👥 Partijen", expanded=True):
                st.markdown(case_brief.get("partijen", "N/A"))

            with st.expander("❓ Rechtsvraag", expanded=True):
                st.markdown(case_brief.get("rechtsvraag", "N/A"))

        with col2:
            with st.expander("💭 Overwegingen", expanded=True):
                st.markdown(case_brief.get("overwegingen", "N/A"))

            with st.expander("⚖️ Dictum (Uitspraak)", expanded=True):
                st.markdown(case_brief.get("dictum", "N/A"))

            with st.expander("⭐ Juridisch Belang", expanded=True):
                st.markdown(case_brief.get("belang", "N/A"))

        # ── Wetsartikelen met klikbare links ──
        st.divider()
        st.subheader("📜 Relevante Wetsartikelen")
        wetsartikelen = case_brief.get("wetsartikelen", [])

        if wetsartikelen:
            _toon_wetsartikelen_grid(wetsartikelen)
        else:
            st.info("Geen wetsartikelen geïdentificeerd.")

        # ── Is er...? vraag stellen ──
        st.divider()
        st.subheader("🔎 Stel een vraag over deze uitspraak")
        st.caption(
            "Stel een ja/nee-vraag (bijv. 'Is er sprake van eigen schuld?') "
            "en de AI zoekt het antwoord op met de bijbehorende rechtsoverweging."
        )

        vraag_input = st.text_input(
            "Jouw vraag",
            placeholder="Is er sprake van...?",
            key="vraag_input"
        )

        if st.button("💬 Stel vraag", key="vraag_button"):
            if not vraag_input or not vraag_input.strip():
                st.warning("⚠️ Voer een vraag in.")
            elif not laatste_tekst:
                st.warning("⚠️ Analyseer eerst een uitspraak.")
            else:
                with st.spinner("🤖 AI zoekt het antwoord..."):
                    vraag_result = stel_vraag_over_uitspraak(
                        laatste_tekst, ecli, vraag_input
                    )
                if not vraag_result["succes"]:
                    st.error(f"❌ {vraag_result['fout']}")
                else:
                    st.session_state["laatste_vraag_antwoord"] = vraag_result["data"]

        # Toon vraag-antwoord
        if "laatste_vraag_antwoord" in st.session_state:
            ant = st.session_state["laatste_vraag_antwoord"]
            antwoord = ant.get("antwoord", "")

            if antwoord.lower() == "ja":
                st.success("**Antwoord: ✅ Ja**")
            else:
                st.error("**Antwoord: ❌ Nee**")

            ro_nr = ant.get("rechtsoverweging_nr", "")
            if ro_nr:
                st.markdown(f"**Rechtsoverweging:** {ro_nr}")

            citaat = ant.get("citaat", "")
            if citaat:
                st.markdown(f"> {citaat}")

            toelichting = ant.get("toelichting", "")
            if toelichting:
                st.markdown(f"**Toelichting:** {toelichting}")

            rechtspraak_url = (
                f"https://uitspraken.rechtspraak.nl/#!/details?id={ecli}"
            )
            st.markdown(
                f"[📄 Bekijk volledige uitspraak op Rechtspraak.nl]({rechtspraak_url})"
            )

        st.divider()

        # ── Opslaan in kennisbank ──
        st.subheader("💾 Opslaan in Kennisbank")

        titel_default = f"Uitspraak {ecli}"
        titel_input = st.text_input(
            "Titel van de uitspraak",
            value=titel_default,
            key="titel_input"
        )

        # View-mode vs edit-mode voor tags/notities
        if st.session_state.get("tags_notities_opgeslagen"):
            # VIEW MODE: toon opgeslagen waarden
            opgeslagen_tags = st.session_state.get("opgeslagen_tags", [])
            opgeslagen_notities = st.session_state.get("opgeslagen_notities", "")

            st.success("✅ Opgeslagen in de kennisbank!")

            if opgeslagen_tags:
                tags_weergave = " · ".join([f"`{t}`" for t in opgeslagen_tags])
                st.markdown(f"**Tags:** {tags_weergave}")
            else:
                st.markdown("*Geen tags opgeslagen.*")

            if opgeslagen_notities:
                st.markdown("**Notities:**")
                st.markdown(opgeslagen_notities)
            else:
                st.markdown("*Geen notities opgeslagen.*")

            if st.button("✏️ Bewerken", key="bewerken_button"):
                st.session_state["tags_notities_opgeslagen"] = False
                st.rerun()

        else:
            # EDIT MODE: toon invoervelden
            tags_input = st.text_input(
                "Tags (komma-gescheiden)",
                placeholder="bijv. kelderluik, 6:162 BW, onrechtmatige daad",
                key="tags_input"
            )

            notities_input = st.text_area(
                "Eigen notities (optioneel)",
                placeholder="Schrijf hier je eigen observaties...",
                key="notities_input"
            )

            if st.button("💾 Opslaan in kennisbank", key="save_button"):
                tags_lijst = [
                    t.strip() for t in tags_input.split(",") if t.strip()
                ]

                # Bestaande tags/notities samenvoegen
                bestaande_tags = []
                bestaande_notities = ""
                bestaande_resultaat = haal_case_brief_op_ecli(ecli)
                if bestaande_resultaat["succes"]:
                    bestaande = bestaande_resultaat["data"]
                    bestaande_tags = bestaande.get("eigen_tags", [])
                    bestaande_notities = bestaande.get("eigen_notities", "")

                if bestaande_tags:
                    tags_lijst = sorted(list(set(bestaande_tags + tags_lijst)))

                if notities_input.strip() and bestaande_notities:
                    notities_def = (
                        f"{bestaande_notities}\n\n---\n{notities_input.strip()}"
                    )
                elif bestaande_notities and not notities_input.strip():
                    notities_def = bestaande_notities
                else:
                    notities_def = notities_input.strip()

                data_voor_db = {
                    "ecli": ecli,
                    "titel": titel_input.strip() if titel_input else titel_default,
                    "feiten": case_brief.get("feiten", ""),
                    "partijen": case_brief.get("partijen", ""),
                    "rechtsvraag": case_brief.get("rechtsvraag", ""),
                    "overwegingen": case_brief.get("overwegingen", ""),
                    "dictum": case_brief.get("dictum", ""),
                    "belang": case_brief.get("belang", ""),
                    "wetsartikelen": case_brief.get("wetsartikelen", []),
                    "eigen_tags": tags_lijst,
                    "eigen_notities": notities_def
                }

                with st.spinner("Opslaan in Supabase..."):
                    save_result = sla_case_brief_op(data_voor_db)

                if save_result["succes"]:
                    st.session_state["tags_notities_opgeslagen"] = True
                    st.session_state["opgeslagen_tags"] = tags_lijst
                    st.session_state["opgeslagen_notities"] = notities_def
                    st.rerun()
                else:
                    st.error(f"❌ {save_result['fout']}")


# ── TAB 2: KENNISBANK ─────────────────────────────────────────────────────────

with tab2:
    st.header("🔍 Kennisbank Doorzoeken")
    st.markdown("Zoek in je opgeslagen uitspraken en filter op tags.")

    # Zoekterm
    zoekterm = st.text_input(
        "Zoekterm",
        placeholder="bijv. kelderluik, onrechtmatige daad, 6:162 BW",
        key="zoekterm_input"
    )

    # Top 5 meest gebruikte tags
    top_tags_result = haal_top_tags_op(limit=5)
    beschikbare_tags = top_tags_result["data"] if top_tags_result["succes"] else []

    vorige_tags = st.session_state.get("vorige_tags_filter", [])

    tags_filter = st.multiselect(
        "Filter op meestgebruikte tags",
        options=beschikbare_tags,
        default=[t for t in vorige_tags if t in beschikbare_tags],
        key="tags_filter",
        help="Toont de 5 meest gebruikte tags. Selecteer om automatisch te filteren."
    )

    # Detecteer of tags zijn veranderd → automatisch zoeken
    tags_veranderd = set(tags_filter) != set(vorige_tags)
    st.session_state["vorige_tags_filter"] = tags_filter

    def _toon_case_briefs(case_briefs):
        if len(case_briefs) == 0:
            st.info("Geen uitspraken gevonden.")
            return

        st.success(f"✅ {len(case_briefs)} uitspraak(en) gevonden")

        for brief in case_briefs:
            titel = brief.get("titel", "Onbekende titel")
            ecli = brief.get("ecli", "Onbekend ECLI")

            # Voorkom herhaling in koptekst
            is_standaard_titel = titel == f"Uitspraak {ecli}" or titel == ecli
            expander_label = ecli if is_standaard_titel else titel

            with st.expander(f"📄 {expander_label}"):
                # ECLI en link — slechts één keer
                st.markdown(f"**ECLI:** `{ecli}`")
                rechtspraak_url = (
                    f"https://uitspraken.rechtspraak.nl/#!/details?id={ecli}"
                )
                st.markdown(f"[🔗 Open op Rechtspraak.nl]({rechtspraak_url})")

                # Aangepaste titel alleen tonen als die afwijkt van standaard
                if not is_standaard_titel:
                    st.markdown(f"**Titel:** {titel}")

                if brief.get("eigen_tags"):
                    tags_weergave = " · ".join(
                        [f"`{t}`" for t in brief["eigen_tags"]]
                    )
                    st.markdown(f"**Tags:** {tags_weergave}")

                if brief.get("eigen_notities"):
                    st.markdown("**Notities:**")
                    st.markdown(brief["eigen_notities"])

                st.divider()

                st.markdown("**Feiten**")
                st.markdown(brief.get("feiten", ""))

                st.markdown("**Partijen**")
                st.markdown(brief.get("partijen", ""))

                st.markdown("**Rechtsvraag**")
                st.markdown(brief.get("rechtsvraag", ""))

                st.markdown("**Overwegingen**")
                st.markdown(brief.get("overwegingen", ""))

                st.markdown("**Dictum**")
                st.markdown(brief.get("dictum", ""))

                st.markdown("**Juridisch belang**")
                st.markdown(brief.get("belang", ""))

                wetsartikelen = brief.get("wetsartikelen", [])
                if wetsartikelen:
                    st.markdown("**Wetsartikelen:**")
                    _toon_wetsartikelen_grid(wetsartikelen)

                st.divider()

                # ── Bewerken: tags en notities ──
                bewerk_key = f"bewerk_modus_{ecli}"
                if not st.session_state.get(bewerk_key, False):
                    # VIEW MODE
                    if st.button(
                        "✏️ Tags & notities bewerken",
                        key=f"open_bewerk_{ecli}"
                    ):
                        st.session_state[bewerk_key] = True
                        st.rerun()
                else:
                    # EDIT MODE
                    st.markdown("**Tags & notities bewerken**")

                    tags_waarde = ", ".join(brief.get("eigen_tags", []))
                    tags_bewerkt = st.text_input(
                        "Tags (komma-gescheiden)",
                        value=tags_waarde,
                        key=f"tags_bewerk_{ecli}"
                    )

                    notities_bewerkt = st.text_area(
                        "Notities",
                        value=brief.get("eigen_notities", ""),
                        key=f"notities_bewerk_{ecli}"
                    )

                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("💾 Opslaan", key=f"save_{ecli}"):
                            tags_lijst = [
                                t.strip()
                                for t in tags_bewerkt.split(",")
                                if t.strip()
                            ]
                            bijgewerkt = {
                                "ecli": ecli,
                                "titel": titel,
                                "feiten": brief.get("feiten", ""),
                                "partijen": brief.get("partijen", ""),
                                "rechtsvraag": brief.get("rechtsvraag", ""),
                                "overwegingen": brief.get("overwegingen", ""),
                                "dictum": brief.get("dictum", ""),
                                "belang": brief.get("belang", ""),
                                "wetsartikelen": brief.get("wetsartikelen", []),
                                "eigen_tags": tags_lijst,
                                "eigen_notities": notities_bewerkt.strip()
                            }
                            with st.spinner("Wijzigingen opslaan..."):
                                update_result = sla_case_brief_op(bijgewerkt)
                            if update_result["succes"]:
                                brief["eigen_tags"] = tags_lijst
                                brief["eigen_notities"] = notities_bewerkt.strip()
                                st.session_state[bewerk_key] = False
                                st.session_state["laatste_zoekresultaten"] = case_briefs
                                st.rerun()
                            else:
                                st.error(f"❌ {update_result['fout']}")
                    with col_b:
                        if st.button("✖️ Annuleren", key=f"annuleer_{ecli}"):
                            st.session_state[bewerk_key] = False
                            st.rerun()

    zoek_clicked = st.button("🔎 Zoeken", key="zoek_button")

    # Zoek als knop geklikt OF als tags zijn veranderd
    if zoek_clicked or tags_veranderd:
        with st.spinner("Zoeken in kennisbank..."):
            resultaat = haal_case_briefs_op(
                zoekterm=zoekterm,
                tags_filter=tags_filter,
                limit=50
            )
        if not resultaat["succes"]:
            st.error(f"❌ {resultaat['fout']}")
        else:
            case_briefs = resultaat["data"]
            st.session_state["laatste_zoekresultaten"] = case_briefs
            _toon_case_briefs(case_briefs)

    elif "laatste_zoekresultaten" in st.session_state:
        _toon_case_briefs(st.session_state["laatste_zoekresultaten"])


# ── TAB 3: CASUS UITWERKEN ────────────────────────────────────────────────────

with tab3:
    st.header("📚 Casus Uitwerken (OOD 6:162 BW)")
    st.markdown(
        "Werk een casus stap-voor-stap uit volgens OOD 6:162 BW en sla je analyse op."
    )

    # Reset-knop bovenaan als er al een analyse is
    if "ood_samenvatting" in st.session_state:
        if st.button("🔄 Nieuwe casus", key="ood_reset_button"):
            for sleutel in [
                k for k in list(st.session_state.keys()) if k.startswith("ood_")
            ]:
                del st.session_state[sleutel]
            st.rerun()

    st.subheader("🧾 Casus en stappen")

    casus_omschrijving = st.text_area(
        "Casusomschrijving",
        placeholder="Beschrijf kort de feiten van de casus...",
        key="ood_casus"
    )

    onrechtmatigheid = st.text_area(
        "Onrechtmatigheid",
        placeholder="Is het gedrag onrechtmatig? Waarom wel/niet?",
        key="ood_onrechtmatigheid"
    )
    with st.expander("Wat betekent dit?"):
        st.markdown(
            "Onrechtmatigheid: schending van een recht, wettelijke plicht of "
            "maatschappelijke zorgvuldigheidsnorm."
        )

    toerekenbaarheid = st.text_area(
        "Toerekenbaarheid",
        placeholder="Kan het gedrag worden toegerekend aan de dader?",
        key="ood_toerekenbaarheid"
    )
    with st.expander("Wat betekent dit?"):
        st.markdown(
            "Toerekenbaarheid: schuld, risico of wettelijk toerekenbare oorzaak."
        )

    schade = st.text_area(
        "Schade",
        placeholder="Welke schade is geleden?",
        key="ood_schade"
    )
    with st.expander("Wat betekent dit?"):
        st.markdown("Schade: vermogensschade of immateriële schade.")

    causaliteit = st.text_area(
        "Causaliteit",
        placeholder="Is er een causaal verband tussen gedrag en schade?",
        key="ood_causaliteit"
    )
    with st.expander("Wat betekent dit?"):
        st.markdown(
            "Causaliteit: condicio sine qua non-verband en eventuele toerekening."
        )

    relativiteit = st.text_area(
        "Relativiteit",
        placeholder="Strekt de geschonden norm tot bescherming tegen deze schade?",
        key="ood_relativiteit"
    )
    with st.expander("Wat betekent dit?"):
        st.markdown(
            "Relativiteit: art. 6:163 BW — beschermt de norm tegen deze schade?"
        )

    st.subheader("⚖️ Kelderluik-factoren")
    st.markdown("Beoordeel elke factor op een schaal van 1 (laag) tot 5 (hoog).")

    kans_onoplettendheid = st.slider(
        "Kans op onoplettendheid van anderen", 1, 5, 3, key="ood_kans_onoplettendheid"
    )
    ernst_gevolgen = st.slider(
        "Ernst van mogelijke gevolgen", 1, 5, 3, key="ood_ernst_gevolgen"
    )
    kans_ongeval = st.slider(
        "Kans dat ongeval zich voordoet", 1, 5, 3, key="ood_kans_ongeval"
    )
    bezwaarlijkheid = st.slider(
        "Bezwaarlijkheid van veiligheidsmaatregelen", 1, 5, 3, key="ood_bezwaarlijkheid"
    )

    st.subheader("🧠 Conclusie")
    conclusie = st.text_area(
        "Conclusie van je analyse",
        placeholder="Vat kort samen of aansprakelijkheid aanwezig is.",
        key="ood_conclusie"
    )

    if st.button("📝 Analyse tonen", key="ood_analyse_button"):
        kelderluik_totaal = (
            kans_onoplettendheid + ernst_gevolgen + kans_ongeval + bezwaarlijkheid
        )
        samenvatting = {
            "casus": casus_omschrijving,
            "onrechtmatigheid": onrechtmatigheid,
            "toerekenbaarheid": toerekenbaarheid,
            "schade": schade,
            "causaliteit": causaliteit,
            "relativiteit": relativiteit,
            "kelderluik": {
                "kans_onoplettendheid": kans_onoplettendheid,
                "ernst_gevolgen": ernst_gevolgen,
                "kans_ongeval": kans_ongeval,
                "bezwaarlijkheid": bezwaarlijkheid,
                "totaal": kelderluik_totaal
            },
            "conclusie": conclusie
        }
        st.session_state["ood_samenvatting"] = samenvatting
        st.rerun()

    # ── Bewerkbare samenvatting ──
    if "ood_samenvatting" in st.session_state:
        s = st.session_state["ood_samenvatting"]
        st.success(
            "✅ Analyse gegenereerd — pas de velden hieronder aan indien nodig."
        )
        st.markdown("### 📋 Samenvatting (aanpasbaar)")

        bewerkt_casus = st.text_area(
            "Casus", value=s.get("casus", ""), key="ood_bewerkt_casus"
        )
        bewerkt_onrechtmatigheid = st.text_area(
            "Onrechtmatigheid", value=s.get("onrechtmatigheid", ""),
            key="ood_bewerkt_onrechtmatigheid"
        )
        bewerkt_toerekenbaarheid = st.text_area(
            "Toerekenbaarheid", value=s.get("toerekenbaarheid", ""),
            key="ood_bewerkt_toerekenbaarheid"
        )
        bewerkt_schade = st.text_area(
            "Schade", value=s.get("schade", ""), key="ood_bewerkt_schade"
        )
        bewerkt_causaliteit = st.text_area(
            "Causaliteit", value=s.get("causaliteit", ""), key="ood_bewerkt_causaliteit"
        )
        bewerkt_relativiteit = st.text_area(
            "Relativiteit", value=s.get("relativiteit", ""),
            key="ood_bewerkt_relativiteit"
        )
        bewerkt_conclusie = st.text_area(
            "Conclusie", value=s.get("conclusie", ""), key="ood_bewerkt_conclusie"
        )

        kl = s.get("kelderluik", {})
        st.markdown("**Kelderluik-scores:**")
        st.markdown(
            f"- Kans op onoplettendheid: {kl.get('kans_onoplettendheid', 0)}\n"
            f"- Ernst gevolgen: {kl.get('ernst_gevolgen', 0)}\n"
            f"- Kans ongeval: {kl.get('kans_ongeval', 0)}\n"
            f"- Bezwaarlijkheid maatregelen: {kl.get('bezwaarlijkheid', 0)}\n"
            f"- **Totaal:** {kl.get('totaal', 0)}"
        )

        st.divider()
        st.subheader("💾 Opslaan in kennisbank")

        extra_tags = st.text_input(
            "Extra tags (optioneel)",
            placeholder="bijv. ood, aansprakelijkheid",
            key="ood_tags"
        )

        if st.button("💾 Opslaan analyse", key="ood_save_button"):
            tags_lijst = ["ood-analyse"]
            if extra_tags.strip():
                tags_lijst.extend([
                    t.strip() for t in extra_tags.split(",") if t.strip()
                ])

            unieke_id = uuid4().hex[:8]
            ecli_ood = f"OOD-{datetime.now().strftime('%Y%m%d')}-{unieke_id}"
            titel_ood = f"OOD Analyse {datetime.now().strftime('%d-%m-%Y')}"

            data_voor_db = {
                "ecli": ecli_ood,
                "titel": titel_ood,
                "feiten": bewerkt_casus,
                "rechtsvraag": "Is er aansprakelijkheid op grond van 6:162 BW?",
                "overwegingen": (
                    f"Onrechtmatigheid: {bewerkt_onrechtmatigheid}\n"
                    f"Toerekenbaarheid: {bewerkt_toerekenbaarheid}\n"
                    f"Schade: {bewerkt_schade}\n"
                    f"Causaliteit: {bewerkt_causaliteit}\n"
                    f"Relativiteit: {bewerkt_relativiteit}\n"
                    f"Kelderluik-scores: {s.get('kelderluik', {})}"
                ),
                "dictum": bewerkt_conclusie,
                "belang": "Samenvatting van OOD-analyse (6:162 BW).",
                "wetsartikelen": ["BW 6:162", "BW 6:163"],
                "eigen_tags": tags_lijst,
                "eigen_notities": "OOD-analyse"
            }

            with st.spinner("Opslaan in Supabase..."):
                save_result = sla_case_brief_op(data_voor_db)

            if save_result["succes"]:
                st.success("✅ OOD-analyse opgeslagen in kennisbank")
            else:
                st.error(f"❌ {save_result['fout']}")


# ── TAB 4: ADMIN ──────────────────────────────────────────────────────────────

def _haal_admin_email() -> str:
    """Haalt het admin e-mailadres op uit st.secrets of .env."""
    try:
        return st.secrets["ADMIN_EMAIL"]
    except Exception:
        return os.environ.get("ADMIN_EMAIL", "")


with tab4:
    _admin_email = _haal_admin_email()
    _ingelogd_email = st.session_state.get("auth_email", "")

    if not _admin_email:
        st.warning("⚠️ ADMIN_EMAIL is niet ingesteld in .env. Voeg het toe om toegang te beperken.")
    elif not _ingelogd_email or _ingelogd_email.lower() != _admin_email.lower():
        st.error("🔒 Toegang geweigerd. Deze pagina is alleen voor de beheerder.")
        st.stop()

    st.header("🛠️ Admin & Documentatie")

    admin_sectie = st.radio(
        "Sectie",
        ["📖 Documentatie", "📋 Changelog", "📊 Statistieken", "🔧 Utiliteiten"],
        horizontal=True,
        label_visibility="collapsed"
    )

    # ── Documentatie ──
    if admin_sectie == "📖 Documentatie":
        st.subheader("📖 Handleiding Caseflow")
        st.markdown("""
### 📄 Tab 1 — Nieuwe Uitspraak
1. Voer een ECLI-nummer in (bijv. `ECLI:NL:HR:2002:AE7040`)
2. Klik op **Analyseer** — de uitspraak wordt opgehaald van Rechtspraak.nl
3. De AI genereert automatisch een **Case Brief** met feiten, partijen, rechtsvraag, overwegingen, dictum en juridisch belang
4. Klik op een **wetsartikel** om direct naar wetten.overheid.nl te gaan
5. Stel een **ja/nee-vraag** over de uitspraak (bijv. "Is er sprake van eigen schuld?")
6. Sla de uitspraak op in de kennisbank met eigen **tags** en **notities**
7. Klik **Bewerken** om tags/notities later aan te passen
8. Klik **Reset** om een nieuwe uitspraak te analyseren (wist ook het ECLI-veld)

### 🔍 Tab 2 — Kennisbank Doorzoeken
- Zoek op trefwoord in alle opgeslagen uitspraken
- Filter op de **5 meest gebruikte tags** — resultaten worden automatisch bijgewerkt bij tag-selectie
- Bekijk de volledige case brief per uitspraak
- Klik op wetsartikelen voor directe links naar wetten.overheid.nl
- Bewerk tags en notities inline via de **Bewerken**-knop

### 📚 Tab 3 — Casus Uitwerken (OOD 6:162 BW)
- Werk een casus stap-voor-stap uit: onrechtmatigheid, toerekenbaarheid, schade, causaliteit, relativiteit
- Beoordeel de **Kelderluik-factoren** met sliders
- Na het klikken op **Analyse tonen** kun je alle velden nog aanpassen
- Sla de analyse op in de kennisbank met de **Opslaan analyse**-knop
- Klik **Nieuwe casus** om opnieuw te beginnen

### 👤 Mijn Account (Sidebar)
- Maak een gratis account aan met je e-mailadres
- Elke gebruiker heeft zijn eigen kennisbank — anderen zien jouw data niet
- Log in/uit via de linkerzijbalk

### ℹ️ ECLI-nummers vinden
- Ga naar [uitspraken.rechtspraak.nl](https://uitspraken.rechtspraak.nl)
- Zoek een uitspraak op en kopieer het ECLI-nummer uit de URL of de detailpagina
        """)

    # ── Changelog ──
    elif admin_sectie == "📋 Changelog":
        st.subheader("📋 Wijzigingen")

        wijzigingen = [
            {
                "versie": "0.5",
                "datum": "Februari 2026",
                "items": [
                    "Rebranding: Juridische Werkbank → Caseflow",
                    "Volledig nieuw design: Editorial Legal thema met DM Serif Display + DM Sans",
                    "Custom kleurschema: deep navy + warm gold accent",
                    "Verbeterde UI: geanimeerde fade-in, verfijnde kaarten, gepolijste knoppen",
                    "Subtiele textuur-overlay voor visuele diepte",
                ]
            },
            {
                "versie": "0.4",
                "datum": "Februari 2026",
                "items": [
                    "Reset-knop wist nu ook het ECLI-invoerveld correct",
                    "Wetsartikelen zijn klikbare links naar wetten.overheid.nl",
                    "'Is er...?' vraag-feature: stel ja/nee vragen over een uitspraak",
                    "Tags en notities: view-mode na opslaan met Bewerken-knop",
                    "Kennisbank: top 5 meest gebruikte tags in dropdown",
                    "Tag-selectie triggert automatisch zoekresultaten",
                    "Kennisbank: minder herhaling van ECLI in zoekresultaten",
                    "Casus uitwerken: reset-knop en bewerkbare samenvatting",
                    "Admin pagina met documentatie, changelog en statistieken",
                    "Gebruikersprofielen: eigen account via Supabase Auth",
                ]
            },
            {
                "versie": "0.3",
                "datum": "Februari 2026",
                "items": [
                    "OOD 6:162 BW stappenplan (Tab 3)",
                    "Kelderluik-factoren met sliders",
                    "OOD-analyse opslaan in kennisbank",
                ]
            },
            {
                "versie": "0.2",
                "datum": "Februari 2026",
                "items": [
                    "Kennisbank met zoeken en tag-filters (Tab 2)",
                    "Tags en notities toevoegen aan uitspraken",
                    "Inline bewerken van tags en notities",
                    "Supabase-koppeling voor opslag",
                ]
            },
            {
                "versie": "0.1",
                "datum": "Februari 2026",
                "items": [
                    "Eerste versie: ECLI-invoer en Case Brief generatie",
                    "Rechtspraak.nl API-koppeling",
                    "Groq/Llama AI-integratie",
                ]
            }
        ]

        for vi in wijzigingen:
            with st.expander(
                f"v{vi['versie']} — {vi['datum']}",
                expanded=(vi["versie"] == "0.5")
            ):
                for item in vi["items"]:
                    st.markdown(f"- {item}")

    # ── Statistieken ──
    elif admin_sectie == "📊 Statistieken":
        st.subheader("📊 Kennisbank Statistieken")

        if st.button("🔄 Statistieken ophalen", key="stats_button"):
            with st.spinner("Statistieken laden..."):
                alle_briefs = haal_case_briefs_op(zoekterm="", tags_filter=[], limit=1000)
                alle_tags = haal_alle_tags_op()

            if alle_briefs["succes"]:
                briefs = alle_briefs["data"]
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Totaal uitspraken", len(briefs))
                with col2:
                    ood_count = sum(
                        1 for b in briefs if b.get("ecli", "").startswith("OOD-")
                    )
                    st.metric("ECLI-uitspraken", len(briefs) - ood_count)
                with col3:
                    st.metric("OOD-analyses", ood_count)

            if alle_tags["succes"]:
                tags = alle_tags["data"]
                st.metric("Unieke tags", len(tags))
                if tags:
                    st.markdown("**Alle tags:** " + " · ".join(
                        [f"`{t}`" for t in tags]
                    ))
            else:
                st.error(f"❌ {alle_briefs.get('fout', 'Onbekende fout')}")

    # ── Utiliteiten ──
    elif admin_sectie == "🔧 Utiliteiten":
        st.subheader("🔧 Utiliteiten")

        # Verwijder uitspraak
        st.markdown("### 🗑️ Uitspraak verwijderen")
        st.caption("Voer het ECLI-nummer in van de uitspraak die je wilt verwijderen.")

        ecli_verwijder = st.text_input(
            "ECLI-nummer om te verwijderen",
            placeholder="ECLI:NL:HR:2002:AE7040",
            key="ecli_verwijder_input"
        )

        if st.button("🗑️ Verwijder uitspraak", key="verwijder_button", type="primary"):
            if not ecli_verwijder or not ecli_verwijder.strip():
                st.warning("⚠️ Voer een ECLI-nummer in.")
            else:
                with st.spinner("Verwijderen..."):
                    verwijder_result = verwijder_case_brief(ecli_verwijder.strip())
                if verwijder_result["succes"]:
                    st.success(f"✅ Uitspraak `{ecli_verwijder}` verwijderd.")
                else:
                    st.error(f"❌ {verwijder_result['fout']}")

        st.divider()

        # Exporteer als CSV
        st.markdown("### 📤 Kennisbank exporteren als CSV")
        st.caption("Download alle opgeslagen uitspraken als CSV-bestand.")

        if st.button("📤 Exporteer kennisbank", key="export_button"):
            with st.spinner("Exporteren..."):
                export_result = haal_case_briefs_op(
                    zoekterm="", tags_filter=[], limit=1000
                )

            if export_result["succes"] and export_result["data"]:
                import csv
                import io

                briefs = export_result["data"]
                output = io.StringIO()
                velden = [
                    "ecli", "titel", "feiten", "rechtsvraag",
                    "dictum", "belang", "eigen_tags", "eigen_notities"
                ]
                writer = csv.DictWriter(
                    output, fieldnames=velden, extrasaction="ignore"
                )
                writer.writeheader()
                for brief in briefs:
                    brief_copy = dict(brief)
                    if isinstance(brief_copy.get("eigen_tags"), list):
                        brief_copy["eigen_tags"] = ", ".join(brief_copy["eigen_tags"])
                    writer.writerow(brief_copy)

                st.download_button(
                    label="⬇️ Download CSV",
                    data=output.getvalue(),
                    file_name=f"kennisbank_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            elif export_result["succes"]:
                st.info("De kennisbank is leeg — niets te exporteren.")
            else:
                st.error(f"❌ {export_result['fout']}")

        st.divider()

        # Supabase SQL voor gebruikersprofielen
        st.markdown("### 🗄️ Supabase schema voor gebruikersprofielen")
        st.caption(
            "Voer dit SQL uit in Supabase Studio (SQL Editor) om gebruikersprofielen "
            "met Row Level Security in te schakelen."
        )
        sql_migratie = """-- Stap 1: user_id kolom toevoegen
ALTER TABLE case_briefs
  ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;

-- Stap 2: Row Level Security inschakelen
ALTER TABLE case_briefs ENABLE ROW LEVEL SECURITY;

-- Stap 3: RLS-policies aanmaken
CREATE POLICY "Gebruikers zien alleen hun eigen uitspraken"
  ON case_briefs FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Gebruikers slaan alleen hun eigen uitspraken op"
  ON case_briefs FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Gebruikers updaten alleen hun eigen uitspraken"
  ON case_briefs FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Gebruikers verwijderen alleen hun eigen uitspraken"
  ON case_briefs FOR DELETE
  USING (auth.uid() = user_id);"""

        st.code(sql_migratie, language="sql")
