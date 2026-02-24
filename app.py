import os
import streamlit as st
from dotenv import load_dotenv
from modules.ecli_fetcher import haal_uitspraak_op
from modules.ai_samenvatting import genereer_case_brief

# Load .env eerst (voor lokale testing zonder Streamlit secrets)
load_dotenv()


# ── PAGE CONFIG ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Juridische Werkbank",
    page_icon="⚖️",
    layout="wide"
)


# ── HEADER ───────────────────────────────────────────────────────────────────

st.title("⚖️ Juridische Werkbank")
st.markdown(
    "Gratis web-app voor Nederlandse rechtsstudenten. "
    "Rechtsuitsspraken begrijpen, opslaan en toepassen."
)

# Tabs
tab1, tab2, tab3 = st.tabs([
    "📄 Nieuwe Uitspraak",
    "🔍 Kennisbank Doorzoeken",
    "📚 Casus Uitwerken"
])


# ── TAB 1: ECLI INPUT & CASE BRIEF ───────────────────────────────────────────

with tab1:
    st.header("📄 Uitspraak Analyseren")
    
    # Input section
    col1, col2 = st.columns([3, 1])
    
    with col1:
        ecli_input = st.text_input(
            label="ECLI-nummer",
            placeholder="bijv. ECLI:NL:HR:2002:AE7040",
            help="Het ECLI-nummer van een Nederlandse rechtsuitsraak.",
            key="ecli_input"
        )
    
    with col2:
        st.write("")  # Spacing
        analyze_button = st.button(
            "🔍 Analyseer",
            use_container_width=True,
            key="analyze_button"
        )
    
    # Reset button
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        if st.button("🔄 Reset", use_container_width=True, key="reset_button"):
            st.session_state.clear()
            st.rerun()
    
    st.divider()
    
    # Analyse logic
    if analyze_button:
        # Validatie: ECLI invoer
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
                    st.success("✅ Case Brief gegenereerd!")
                    
                    # Stap 3: Toon Case Brief
                    st.subheader("📋 Case Brief")
                    st.caption(f"ECLI: `{ecli}`")
                    
                    # Twee kolommen voor beter overzicht
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
                    
                    # Wetsartikelen
                    st.divider()
                    st.subheader("📜 Relevante Wetsartikelen")
                    wetsartikelen = case_brief.get("wetsartikelen", [])
                    
                    if wetsartikelen and len(wetsartikelen) > 0:
                        cols = st.columns(3)
                        for idx, artikel in enumerate(wetsartikelen):
                            with cols[idx % 3]:
                                st.markdown(f"🔹 {artikel}")
                    else:
                        st.info("Geen wetsartikelen geïdentificeerd.")


# ── TAB 2: KENNISBANK ────────────────────────────────────────────────────────

with tab2:
    st.header("🔍 Kennisbank Doorzoeken")
    st.info(
        "ℹ️ **Kennisbank functionaliteit** komt in Fase 3.\n\n"
        "Hier kun je:\n"
        "- Opgeslagen uitspraken zoeken\n"
        "- Filteren op tags\n"
        "- Notities toevoegen"
    )


# ── TAB 3: STAPPENPLAN ───────────────────────────────────────────────────────

with tab3:
    st.header("📚 Casus Uitwerken (OOD 6:162 BW)")
    st.info(
        "ℹ️ **Stappenplan functionaliteit** komt in Fase 4.\n\n"
        "Hier kun je:\n"
        "- Een juridische casus stap-voor-stap uitwerken\n"
        "- OOD 6:162 BW (Bijzonder Vermeld Recht) analyseren\n"
        "- Samenvatting opslaan in de kennisbank"
    )
