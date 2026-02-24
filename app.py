import os
from datetime import datetime
from uuid import uuid4
import streamlit as st
from dotenv import load_dotenv
from modules.ecli_fetcher import haal_uitspraak_op
from modules.ai_samenvatting import genereer_case_brief
from modules.database import (
    sla_case_brief_op,
    haal_case_briefs_op,
    haal_alle_tags_op,
    haal_case_brief_op_ecli
)

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
                    st.session_state["laatste_case_brief"] = case_brief
                    st.session_state["laatste_ecli"] = ecli
                    st.success("✅ Case Brief gegenereerd!")

    # Toon laatste Case Brief uit session state (blijft staan na rerun)
    laatste_case_brief = st.session_state.get("laatste_case_brief")
    laatste_ecli = st.session_state.get("laatste_ecli")

    if laatste_case_brief and laatste_ecli:
        case_brief = laatste_case_brief
        ecli = laatste_ecli

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

        st.divider()

        # ── Opslaan in kennisbank ───────────────────────────
        st.subheader("💾 Opslaan in Kennisbank")

        titel_default = f"Uitspraak {ecli}"
        titel_input = st.text_input(
            "Titel van de uitspraak",
            value=titel_default,
            key="titel_input"
        )

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
            # Parse tags
            tags_lijst = [
                t.strip() for t in tags_input.split(",") if t.strip()
            ]

            # Als tags/notities leeg zijn, probeer bestaande waarden te behouden
            bestaande_tags = []
            bestaande_notities = ""
            bestaande_resultaat = haal_case_brief_op_ecli(ecli)
            if bestaande_resultaat["succes"]:
                bestaande = bestaande_resultaat["data"]
                bestaande_tags = bestaande.get("eigen_tags", [])
                bestaande_notities = bestaande.get("eigen_notities", "")

            # Samenvoegen: bestaande tags + nieuwe tags (uniek)
            if bestaande_tags:
                tags_lijst = sorted(list(set(bestaande_tags + tags_lijst)))

            # Notities samenvoegen (oude + nieuwe, gescheiden)
            if notities_input.strip() and bestaande_notities:
                notities_input = f"{bestaande_notities}\n\n---\n{notities_input.strip()}"
            elif bestaande_notities and not notities_input.strip():
                notities_input = bestaande_notities

            # Bouw data voor database
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
                "eigen_notities": notities_input.strip()
            }

            with st.spinner("Opslaan in Supabase..."):
                save_result = sla_case_brief_op(data_voor_db)

            if save_result["succes"]:
                st.success("✅ Opgeslagen in de kennisbank!")
            else:
                st.error(f"❌ {save_result['fout']}")


# ── TAB 2: KENNISBANK ────────────────────────────────────────────────────────

with tab2:
    st.header("🔍 Kennisbank Doorzoeken")
    st.markdown("Zoek in je opgeslagen uitspraken en filter op tags.")

    # Zoekveld en filters
    zoekterm = st.text_input(
        "Zoekterm",
        placeholder="bijv. kelderluik, onrechtmatige daad, 6:162 BW",
        key="zoekterm_input"
    )

    # Tags ophalen voor filter
    tags_result = haal_alle_tags_op()
    beschikbare_tags = tags_result["data"] if tags_result["succes"] else []

    tags_filter = st.multiselect(
        "Filter op tags",
        options=beschikbare_tags,
        default=[],
        key="tags_filter"
    )

    def _toon_case_briefs(case_briefs):
        if len(case_briefs) == 0:
            st.info("Geen uitspraken gevonden.")
            return

        st.success(f"✅ {len(case_briefs)} uitspraak(en) gevonden")

        for brief in case_briefs:
            titel = brief.get("titel", "Onbekende titel")
            ecli = brief.get("ecli", "Onbekend ECLI")

            with st.expander(f"{titel} — {ecli}"):
                st.markdown(f"**ECLI:** {ecli}")
                st.markdown(f"**Titel:** {titel}")

                # Link naar Rechtspraak.nl
                rechtspraak_url = (
                    f"https://uitspraken.rechtspraak.nl/#!/details?id={ecli}"
                )
                st.markdown(
                    f"[Open uitspraak op Rechtspraak.nl]({rechtspraak_url})"
                )

                if brief.get("eigen_tags"):
                    st.markdown(
                        "**Tags:** " + ", ".join(brief["eigen_tags"])
                    )

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
                    st.markdown(
                        "**Wetsartikelen:** " + ", ".join(wetsartikelen)
                    )

                st.divider()

                # Bewerken: tags en notities
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

                if st.button("💾 Wijzigingen opslaan", key=f"save_{ecli}"):
                    tags_lijst = [
                        t.strip() for t in tags_bewerkt.split(",") if t.strip()
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
                        st.success("✅ Wijzigingen opgeslagen")
                        # Update direct in UI
                        brief["eigen_tags"] = tags_lijst
                        brief["eigen_notities"] = notities_bewerkt.strip()
                        st.session_state["laatste_zoekresultaten"] = case_briefs
                    else:
                        st.error(f"❌ {update_result['fout']}")

    zoek_clicked = st.button("🔎 Zoeken", key="zoek_button")

    if zoek_clicked:
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

    # Toon laatst gevonden resultaten als er niet net gezocht is
    if (not zoek_clicked) and "laatste_zoekresultaten" in st.session_state:
        _toon_case_briefs(st.session_state["laatste_zoekresultaten"])


# ── TAB 3: STAPPENPLAN ───────────────────────────────────────────────────────

with tab3:
    st.header("📚 Casus Uitwerken (OOD 6:162 BW)")
    st.markdown(
        "Werk een casus stap-voor-stap uit volgens OOD 6:162 BW en sla je analyse op."
    )

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
            "Causaliteit: condicio sine qua non-verband en eventuele toerekening.")

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

    if "ood_samenvatting" in st.session_state:
        s = st.session_state["ood_samenvatting"]
        st.success("✅ Analyse gegenereerd")
        st.markdown("### 📋 Samenvatting")
        st.markdown(f"**Casus:** {s.get('casus', '')}")
        st.markdown(f"**Onrechtmatigheid:** {s.get('onrechtmatigheid', '')}")
        st.markdown(f"**Toerekenbaarheid:** {s.get('toerekenbaarheid', '')}")
        st.markdown(f"**Schade:** {s.get('schade', '')}")
        st.markdown(f"**Causaliteit:** {s.get('causaliteit', '')}")
        st.markdown(f"**Relativiteit:** {s.get('relativiteit', '')}")

        kl = s.get("kelderluik", {})
        st.markdown("**Kelderluik-scores:**")
        st.markdown(
            f"- Kans op onoplettendheid: {kl.get('kans_onoplettendheid', 0)}\n"
            f"- Ernst gevolgen: {kl.get('ernst_gevolgen', 0)}\n"
            f"- Kans ongeval: {kl.get('kans_ongeval', 0)}\n"
            f"- Bezwaarlijkheid maatregelen: {kl.get('bezwaarlijkheid', 0)}\n"
            f"- **Totaal:** {kl.get('totaal', 0)}"
        )

        st.markdown(f"**Conclusie:** {s.get('conclusie', '')}")

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
                "feiten": s.get("casus", ""),
                "rechtsvraag": "Is er aansprakelijkheid op grond van 6:162 BW?",
                "overwegingen": (
                    f"Onrechtmatigheid: {s.get('onrechtmatigheid', '')}\n"
                    f"Toerekenbaarheid: {s.get('toerekenbaarheid', '')}\n"
                    f"Schade: {s.get('schade', '')}\n"
                    f"Causaliteit: {s.get('causaliteit', '')}\n"
                    f"Relativiteit: {s.get('relativiteit', '')}\n"
                    f"Kelderluik-scores: {s.get('kelderluik', {})}"
                ),
                "dictum": s.get("conclusie", ""),
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
