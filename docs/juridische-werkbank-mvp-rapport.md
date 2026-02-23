# Juridische Werkbank — MVP Onderzoeksrapport
### Een 100% gratis web-app voor Nederlandse rechtsstudenten

> **Opgesteld voor:** Vibe-coder met basiskennis Python  
> **Budget:** €0  
> **Doel:** Werkend prototype binnen 2 weken  
> **Datum:** Februari 2026

---

## Inhoudsopgave

1. [Marktlandschap — Wat bestaat er al?](#1-marktlandschap)
2. [Tech Stack Tabel — Jouw Gratis Gereedschapskist](#2-tech-stack-tabel)
3. [Data Flow Diagram — Van ECLI naar Opgeslagen Samenvatting](#3-data-flow-diagram)
4. [Hoe haal je een uitspraak op? (ECLI & PDF)](#4-uitspraken-ophalen)
5. [Hoe prik ik AI-samenvattingen gratis? (Groq + Llama 3.3)](#5-ai-koppeling-groq)
6. [De Doorzoekbare Kennisbank (Supabase)](#6-database-supabase)
7. [Frontend in Streamlit — Knoppen, geen prompts](#7-frontend-streamlit)
8. [Prompt Engineering Gids — Nederlandse Case Briefs](#8-prompt-engineering)
9. [MVP Roadmap — 2 Weken Plan](#9-mvp-roadmap)
10. [Zero-Budget Plan — Limieten & Wanneer Betalen?](#10-zero-budget-plan)

---

## 1. Marktlandschap

### Wie zijn de spelers en wat doen ze?

| Platform | Doelgroep | Prijs (student) | Wat het doet | Wat het **niet** doet |
|---|---|---|---|---|
| **Legal Intelligence** (legalintelligence.com) | WO/HBO studenten | Gratis via instelling | Zoeken in jurisprudentie, wetgeving, literatuur; AI-zoekassistent | Geen persoonlijke kennisbank, geen case briefs, geen leerworkflow |
| **Rechtsorde** (rechtsorde.nl) | Advocaten, juristen | Betaald abonnement | GenIA-L AI-zoeken, NL + EU bronnen | Gericht op professionals, niet op studenten |
| **SDU OpMaat** | Professionals | Betaald | Wetgeving + commentaar | Duur, geen student-tools |
| **Feitlijn** (Patroon) | Advocaten + studenten | Gratis | Overzicht jurisprudentie per feit | Geen persoonlijke opslag, geen samenvattingen |
| **Legal Mind** (legal-mind.nl) | Juridisch professionals | Betaald | AI-analyse, documentgeneratie | Niet voor studenten |
| **Rechtspraak.nl Open Data** | Iedereen | Gratis | Ruwe XML-uitspraken via API | Geen samenvattingen, geen student-UX |

### Jouw kans: de "studenten-workflow" gap

Alle bestaande tools zijn **zoekplatforms voor professionals**. Ze geven je de uitspraak, maar ze helpen je er niet mee *leren*. Jouw Juridische Werkbank richt zich op een fundamenteel andere behoefte:

**Bestaande tools:** Zoeken → Lezen  
**Juridische Werkbank:** Uploaden → Begrijpen → Onthouden → Toepassen

Concreet zijn dit de onderscheidende functies:

- **Gestructureerde Case Brief** in het Nederlands (feiten, rechtsvraag, overwegingen, dictum, belang)
- **Persoonlijke kennisbank** met eigen tags (bijv. "6:162 BW", "onrechtmatige daad", "tentamen week 3")
- **Interactief stappenplan** voor casus-uitwerking (bijv. Kelderluik-criteria afvinken)
- **Gratis** — geen instelling nodig, geen licentie vereist

---

## 2. Tech Stack Tabel

### De 100% Gratis Gereedschapskist

| Laag | Aanbevolen Tool | Gratis Limiet | Alternatief | URL |
|---|---|---|---|---|
| **Frontend** | Streamlit | 3 apps, 1 GB RAM | Gradio | streamlit.io |
| **Hosting** | Streamlit Community Cloud | Gratis, publieke GitHub repo vereist | Hugging Face Spaces | share.streamlit.io |
| **Database** | Supabase (PostgreSQL) | 500 MB, 2 projecten | PlanetScale (MySQL) | supabase.com |
| **Volledige-tekst zoeken** | Supabase Full-Text Search (ingebouwd) | Inbegrepen | Meilisearch (self-hosted) | — |
| **AI-API** | Groq (Llama 3.3 70B) | ~14.400 req/dag (Free Tier) | Google Gemini Flash (gratis) | console.groq.com |
| **PDF-verwerking** | PyMuPDF (fitz) | Open-source | pdfplumber | pypi.org/project/pymupdf |
| **ECLI-ophalen** | Rechtspraak.nl Open Data API | Publiek, max 10 req/sec | — | data.rechtspraak.nl |
| **Omgevingsbeheer** | python-dotenv | Gratis | — | pypi.org |
| **Versiebeheer** | GitHub (gratis) | Publieke repos gratis | GitLab | github.com |

### Waarom Groq boven Hugging Face Inference API?

Groq draait modellen op speciale LPU-hardware — de **snelheid is 10–100x sneller** dan standaard GPU-inference. Voor een student die een uitspraak van 5.000 woorden wil samenvatten, is een responstijd van 2–3 seconden (Groq) veel prettiger dan 30–60 seconden (HF Inference API gratis tier). Bovendien ondersteunt Llama 3.3 70B uitstekend Nederlands.

---

## 3. Data Flow Diagram

```
╔══════════════════════════════════════════════════════════════════╗
║                        GEBRUIKER (browser)                       ║
║                                                                  ║
║   [Voer ECLI in]  of  [Upload PDF]   of  [Plak tekst]           ║
╚════════════════╦═════════════════════════════════════════════════╝
                 │
                 ▼
╔══════════════════════════════════════════════════════════════════╗
║                    STREAMLIT APP (Python)                         ║
║                                                                  ║
║  Stap 1: Invoer detecteren                                       ║
║    ├─ ECLI? → Haal XML op via data.rechtspraak.nl API            ║
║    ├─ PDF?  → Extraheer tekst met PyMuPDF                        ║
║    └─ Tekst? → Direct doorgeven                                  ║
║                                                                  ║
║  Stap 2: Tekst opschonen                                         ║
║    └─ Verwijder XML-tags, kopteksten, overbodige witruimte       ║
║       Maximaal 8.000 tokens afkappen (Groq context window)       ║
║                                                                  ║
║  Stap 3: AI-samenvatting aanvragen                               ║
║    └─ POST naar Groq API (Llama 3.3-70B-versatile)               ║
║       met juridisch Case Brief prompt (zie §8)                   ║
║                                                                  ║
║  Stap 4: Resultaat tonen aan gebruiker                           ║
║    └─ Gestructureerde Case Brief in Streamlit UI                 ║
║       Student kan tags toevoegen, notities schrijven             ║
║                                                                  ║
║  Stap 5: Opslaan in database                                     ║
║    └─ POST naar Supabase (PostgreSQL)                            ║
║       Velden: ecli, titel, feiten, rechtsvraag, overwegingen,    ║
║               dictum, belang, tags[], notities, datum            ║
╚══════════════════════════════════════════════════════════════════╝
                 │
                 ▼
╔══════════════════════════════════════════════════════════════════╗
║                    SUPABASE DATABASE                             ║
║                                                                  ║
║  Tabel: case_briefs                                              ║
║  ┌────────┬──────────┬───────────┬──────────┬──────────────┐    ║
║  │ id     │ ecli     │ feiten    │ tags     │ opgeslagen_op│    ║
║  │ (uuid) │ (text)   │ (text)    │ (text[]) │ (timestamp)  │    ║
║  └────────┴──────────┴───────────┴──────────┴──────────────┘    ║
║                                                                  ║
║  Full-text zoeken op: feiten, rechtsvraag, overwegingen, tags   ║
╚══════════════════════════════════════════════════════════════════╝
                 │
                 ▼
╔══════════════════════════════════════════════════════════════════╗
║               ZOEKEN & TERUGVINDEN (Streamlit)                   ║
║                                                                  ║
║  [Zoekbalk] → Supabase full-text query → Resultatenlijst        ║
║  [Tag filter "6:162 BW"] → Gefilterde resultaten                ║
║  [Klik op uitspraak] → Volledige Case Brief weergeven           ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## 4. Uitspraken Ophalen

### 4a. Via ECLI (de aanbevolen route)

De Rechtspraak heeft een **gratis, publieke REST API** op `data.rechtspraak.nl`. Geen API-sleutel nodig, maximaal 10 verzoeken per seconde.

```python
# ecli_fetcher.py
import requests
from xml.etree import ElementTree as ET

def haal_uitspraak_op(ecli: str) -> dict:
    """
    Haalt een uitspraak op via de Open Data API van Rechtspraak.nl
    
    Args:
        ecli: Bijv. "ECLI:NL:HR:2002:AE7040" (Kelderluik-arrest)
    
    Returns:
        Dict met 'tekst', 'titel', 'datum', 'instantie'
    """
    url = f"https://data.rechtspraak.nl/uitspraken/content?id={ecli}"
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return {"fout": f"Kon uitspraak niet ophalen: {e}"}
    
    # Rechtspraak levert XML in Atom-formaat
    # Verwijder de namespace-prefix voor makkelijker parsen
    xml_tekst = response.text
    
    try:
        root = ET.fromstring(xml_tekst.encode('utf-8'))
        
        # Namespace mapping (Rechtspraak gebruikt meerdere namespaces)
        ns = {
            'atom': 'http://www.w3.org/2005/Atom',
            'rs': 'http://www.rechtspraak.nl/schema/rechtspraak-1.0',
            'dc': 'http://purl.org/dc/elements/1.1/',
            'dcterms': 'http://purl.org/dc/terms/'
        }
        
        # Haal metadata op
        titel = root.find('.//atom:title', ns)
        datum = root.find('.//dcterms:date', ns)
        instantie = root.find('.//dcterms:creator', ns)
        
        # Haal de volledige uitspraaktekst op
        # De tekst zit in <rs:uitspraak> of als platte tekst in de content
        uitspraak_elem = root.find('.//{http://www.rechtspraak.nl/schema/rechtspraak-1.0}uitspraak')
        
        if uitspraak_elem is not None:
            # Haal alle tekst recursief op
            tekst = " ".join(uitspraak_elem.itertext()).strip()
        else:
            # Fallback: alle tekst uit het document
            tekst = " ".join(root.itertext()).strip()
        
        return {
            "ecli": ecli,
            "titel": titel.text if titel is not None else ecli,
            "datum": datum.text if datum is not None else "Onbekend",
            "instantie": instantie.text if instantie is not None else "Onbekend",
            "tekst": tekst[:15000],  # Kap af op ~15.000 tekens (~4.000 tokens)
        }
        
    except ET.ParseError as e:
        return {"fout": f"XML-parsefout: {e}", "ruwe_tekst": xml_tekst[:500]}


# Voorbeeld gebruik:
if __name__ == "__main__":
    # Het beroemde Kelderluik-arrest
    resultaat = haal_uitspraak_op("ECLI:NL:HR:2002:AE7040")
    print(f"Titel: {resultaat['titel']}")
    print(f"Tekst (eerste 500 tekens): {resultaat['tekst'][:500]}")
```

### 4b. Via PDF Upload

```python
# pdf_verwerker.py
import fitz  # PyMuPDF — installeer met: pip install pymupdf

def extraheer_tekst_uit_pdf(pdf_bytes: bytes) -> str:
    """
    Extraheert tekst uit een PDF-bestand.
    Werkt met zowel tekstgebaseerde als gescande PDFs (beperkt).
    
    Args:
        pdf_bytes: De raw bytes van het PDF-bestand (van st.file_uploader)
    
    Returns:
        De geëxtraheerde tekst als string
    """
    tekst_delen = []
    
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for pagina_nr, pagina in enumerate(doc):
            tekst = pagina.get_text("text")  # Eenvoudige tekstextractie
            if tekst.strip():
                tekst_delen.append(tekst)
    
    volledige_tekst = "\n\n".join(tekst_delen)
    
    # Verwijder overmatige witruimte
    import re
    volledige_tekst = re.sub(r'\n{3,}', '\n\n', volledige_tekst)
    volledige_tekst = re.sub(r' {2,}', ' ', volledige_tekst)
    
    return volledige_tekst[:15000]  # Kap af voor de AI
```

---

## 5. AI-Koppeling via Groq

### Setup (eenmalig)

```bash
pip install groq python-dotenv pymupdf requests
```

Maak een `.env` bestand aan in je projectmap:
```
GROQ_API_KEY=gsk_jouwsleutelkopiërenvanconsolegrooq
SUPABASE_URL=https://jouwproject.supabase.co
SUPABASE_KEY=jouw_supabase_anon_key
```

### De AI-Samenvatting aanvragen

```python
# ai_samenvatting.py
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def genereer_case_brief(uitspraak_tekst: str, ecli: str = "") -> dict:
    """
    Stuurt een uitspraaktekst naar Groq/Llama 3.3 en krijgt een
    gestructureerde Case Brief terug in JSON-formaat.
    
    Args:
        uitspraak_tekst: De volledige of afgekapte uitspraaktekst
        ecli: Optioneel ECLI-nummer voor context
    
    Returns:
        Dict met alle Case Brief-secties
    """
    
    # De prompt — zie §8 voor uitgebreidere versies
    systeem_prompt = """Je bent een juridisch assistent gespecialiseerd in het Nederlandse recht. 
Je taak is om uitspraken van Nederlandse rechtbanken samen te vatten in een gestructureerde 
Case Brief voor rechtenstudenten. Antwoord ALTIJD in het Nederlands.
Antwoord UITSLUITEND in geldig JSON-formaat, zonder extra tekst of uitleg daaromheen."""

    gebruiker_prompt = f"""Analyseer de volgende Nederlandse rechterlijke uitspraak en maak een 
gestructureerde Case Brief. Lever het resultaat op als JSON met deze exacte structuur:

{{
  "feiten": "Korte beschrijving van de relevante feiten (2-4 zinnen)",
  "partijen": "Wie procedeert tegen wie, en in welke hoedanigheid",
  "procedure": "Welk type procedure (kort geding, bodemprocedure, cassatie, etc.) en bij welke instantie",
  "rechtsvraag": "De centrale juridische vraag die de rechter moest beantwoorden (1-2 zinnen)",
  "overwegingen": "De belangrijkste juridische redenering van de rechter (4-6 zinnen)",
  "wetsartikelen": ["Lijst van aangehaalde wetsartikelen, bijv. '6:162 BW'"],
  "dictum": "De uitkomst/beslissing van de rechter (1-2 zinnen)",
  "belang": "Waarom is deze uitspraak juridisch belangrijk? Wat is het precedent-effect? (2-3 zinnen)",
  "zoektermen": ["5-8 relevante zoektermen voor studenten, bijv. 'onrechtmatige daad', 'kelderluik']"
}}

ECLI: {ecli if ecli else "Niet beschikbaar"}

UITSPRAAK:
{uitspraak_tekst}"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Beste gratis model voor Nederlands
            messages=[
                {"role": "system", "content": systeem_prompt},
                {"role": "user", "content": gebruiker_prompt}
            ],
            temperature=0.1,        # Laag = consistenter, minder hallucinaties
            max_tokens=1500,        # Genoeg voor een goede samenvatting
            response_format={"type": "json_object"},  # Forceer JSON-output
        )
        
        import json
        ruwe_output = completion.choices[0].message.content
        case_brief = json.loads(ruwe_output)
        return {"succes": True, "data": case_brief}
        
    except json.JSONDecodeError:
        return {"succes": False, "fout": "AI gaf geen geldig JSON terug", "ruwe": ruwe_output}
    except Exception as e:
        return {"succes": False, "fout": str(e)}


# Voorbeeld gebruik:
if __name__ == "__main__":
    voorbeeld_tekst = """
    Arrest van de Hoge Raad der Nederlanden, 5 november 1965...
    [hier komt de echte uitspraaktekst]
    """
    resultaat = genereer_case_brief(voorbeeld_tekst, "ECLI:NL:HR:1965:AB7079")
    if resultaat["succes"]:
        import json
        print(json.dumps(resultaat["data"], indent=2, ensure_ascii=False))
```

---

## 6. Database — Supabase

### Eenmalige setup (5 minuten)

1. Ga naar [supabase.com](https://supabase.com) en maak een gratis account
2. Maak een nieuw project aan
3. Ga naar **SQL Editor** en voer dit script uit:

```sql
-- Maak de hoofdtabel voor case briefs
CREATE TABLE case_briefs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    ecli TEXT UNIQUE,                    -- ECLI-nummer (unieke identificator)
    titel TEXT NOT NULL,                  -- Bijv. "HR 5 november 1965 (Kelderluik)"
    instantie TEXT,                       -- Bijv. "Hoge Raad"
    datum TEXT,                           -- Datum van uitspraak
    
    -- Case Brief velden (gegenereerd door AI)
    feiten TEXT,
    partijen TEXT,
    procedure TEXT,
    rechtsvraag TEXT,
    overwegingen TEXT,
    dictum TEXT,
    belang TEXT,
    
    -- Gestructureerde data
    wetsartikelen TEXT[],                 -- Array bijv. {"6:162 BW", "6:163 BW"}
    zoektermen TEXT[],
    
    -- Student-eigen velden
    eigen_tags TEXT[],                    -- Student-toegevoegde tags
    eigen_notities TEXT,                  -- Persoonlijke aantekeningen
    
    -- Volledige tekst voor zoeken
    volledige_tekst TEXT,
    
    -- Metadata
    aangemaakt_op TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    bijgewerkt_op TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Full-text zoeken instellen (voor Nederlandse tekst)
-- 'dutch' vertelt PostgreSQL welke stopwoorden en stemming te gebruiken
CREATE INDEX case_briefs_fts_idx ON case_briefs 
    USING GIN (to_tsvector('dutch', 
        COALESCE(titel, '') || ' ' ||
        COALESCE(feiten, '') || ' ' ||
        COALESCE(rechtsvraag, '') || ' ' ||
        COALESCE(overwegingen, '') || ' ' ||
        COALESCE(belang, '')
    ));

-- Index op tags voor snel filteren
CREATE INDEX case_briefs_tags_idx ON case_briefs USING GIN(eigen_tags);
CREATE INDEX case_briefs_wetsartikelen_idx ON case_briefs USING GIN(wetsartikelen);

-- Automatisch bijgewerkt_op updaten
CREATE OR REPLACE FUNCTION update_bijgewerkt_op()
RETURNS TRIGGER AS $$
BEGIN NEW.bijgewerkt_op = NOW(); RETURN NEW; END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_bijgewerkt_op
    BEFORE UPDATE ON case_briefs
    FOR EACH ROW EXECUTE FUNCTION update_bijgewerkt_op();
```

### Python-koppeling

```python
# database.py
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

supabase: Client = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_KEY")
)

def sla_case_brief_op(ecli: str, titel: str, case_brief: dict, 
                       eigen_tags: list = None, notities: str = "") -> dict:
    """Slaat een gegenereerde Case Brief op in de database."""
    
    data = {
        "ecli": ecli,
        "titel": titel,
        "feiten": case_brief.get("feiten", ""),
        "partijen": case_brief.get("partijen", ""),
        "procedure": case_brief.get("procedure", ""),
        "rechtsvraag": case_brief.get("rechtsvraag", ""),
        "overwegingen": case_brief.get("overwegingen", ""),
        "dictum": case_brief.get("dictum", ""),
        "belang": case_brief.get("belang", ""),
        "wetsartikelen": case_brief.get("wetsartikelen", []),
        "zoektermen": case_brief.get("zoektermen", []),
        "eigen_tags": eigen_tags or [],
        "eigen_notities": notities,
    }
    
    # upsert = update als ECLI al bestaat, anders insert
    resultaat = supabase.table("case_briefs").upsert(data, on_conflict="ecli").execute()
    return resultaat.data


def zoek_case_briefs(zoekterm: str = "", tag_filter: str = "") -> list:
    """
    Doorzoekt de kennisbank op tekst of tag.
    
    Args:
        zoekterm: Vrije tekst, bijv. "onrechtmatige daad" of "6:162"
        tag_filter: Een specifieke tag, bijv. "kelderluik"
    
    Returns:
        Lijst van matchende case briefs
    """
    query = supabase.table("case_briefs").select(
        "id, ecli, titel, instantie, datum, rechtsvraag, belang, eigen_tags, wetsartikelen"
    )
    
    if zoekterm:
        # Full-text zoeken met PostgreSQL
        query = query.text_search(
            "volledige_tekst",  # of gebruik fts-kolom
            zoekterm,
            config="dutch"
        )
    
    if tag_filter:
        # Filter op specifieke tag in de array
        query = query.contains("eigen_tags", [tag_filter])
    
    resultaat = query.order("aangemaakt_op", desc=True).limit(20).execute()
    return resultaat.data


def haal_case_brief_op(id: str) -> dict:
    """Haalt één volledige Case Brief op via ID."""
    resultaat = supabase.table("case_briefs").select("*").eq("id", id).single().execute()
    return resultaat.data
```

---

## 7. Frontend in Streamlit

### De volledige app — `app.py`

```python
# app.py — Juridische Werkbank MVP
import streamlit as st
import json
from ecli_fetcher import haal_uitspraak_op
from pdf_verwerker import extraheer_tekst_uit_pdf
from ai_samenvatting import genereer_case_brief
from database import sla_case_brief_op, zoek_case_briefs, haal_case_brief_op

# Pagina-configuratie
st.set_page_config(
    page_title="Juridische Werkbank",
    page_icon="⚖️",
    layout="wide"
)

st.title("⚖️ Juridische Werkbank")
st.caption("Jouw persoonlijke kennisbank voor Nederlandse jurisprudentie")

# ═══════════════════════════════════════════════════════
# NAVIGATIE — 3 hoofdfuncties
# ═══════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs(["📄 Nieuwe Uitspraak", "🔍 Kennisbank Doorzoeken", "📚 Casus Uitwerken"])


# ═══════════════════════════════════════════════════════
# TAB 1: Nieuwe uitspraak verwerken
# ═══════════════════════════════════════════════════════
with tab1:
    st.header("Uitspraak Analyseren")
    
    invoer_methode = st.radio(
        "Hoe wil je de uitspraak invoeren?",
        ["ECLI-nummer", "PDF uploaden", "Tekst plakken"],
        horizontal=True
    )
    
    uitspraak_tekst = ""
    ecli = ""
    titel = "Onbekende uitspraak"
    
    if invoer_methode == "ECLI-nummer":
        ecli_invoer = st.text_input(
            "ECLI-nummer",
            placeholder="bijv. ECLI:NL:HR:2002:AE7040",
            help="Vind ECLI-nummers op rechtspraak.nl"
        )
        if ecli_invoer and st.button("📥 Ophalen van Rechtspraak.nl"):
            with st.spinner("Uitspraak ophalen..."):
                resultaat = haal_uitspraak_op(ecli_invoer)
                if "fout" not in resultaat:
                    uitspraak_tekst = resultaat["tekst"]
                    ecli = resultaat["ecli"]
                    titel = resultaat["titel"]
                    st.success(f"✅ Opgehaald: {titel}")
                    with st.expander("Ruwe tekst bekijken"):
                        st.text(uitspraak_tekst[:1000] + "...")
                else:
                    st.error(f"❌ Fout: {resultaat['fout']}")
    
    elif invoer_methode == "PDF uploaden":
        pdf_bestand = st.file_uploader("Upload een PDF", type=["pdf"])
        if pdf_bestand:
            with st.spinner("PDF verwerken..."):
                uitspraak_tekst = extraheer_tekst_uit_pdf(pdf_bestand.read())
                titel = pdf_bestand.name.replace(".pdf", "")
                st.success(f"✅ PDF verwerkt: {len(uitspraak_tekst)} tekens geëxtraheerd")
    
    else:  # Tekst plakken
        uitspraak_tekst = st.text_area(
            "Plak hier de tekst van de uitspraak",
            height=200,
            placeholder="Kopieer en plak de uitspraaktekst hier..."
        )
        ecli = st.text_input("ECLI (optioneel)", placeholder="ECLI:NL:HR:...")
    
    # AI-samenvatting genereren
    if uitspraak_tekst:
        st.divider()
        
        col1, col2 = st.columns([3, 1])
        with col1:
            eigen_tags = st.text_input(
                "Tags toevoegen (kommagescheiden)",
                placeholder="bijv. 6:162 BW, onrechtmatige daad, tentamen week 4"
            )
        with col2:
            analyseer_knop = st.button("🤖 Analyseer met AI", type="primary", use_container_width=True)
        
        if analyseer_knop:
            with st.spinner("AI analyseert de uitspraak... (10-30 seconden)"):
                resultaat = genereer_case_brief(uitspraak_tekst, ecli)
            
            if resultaat["succes"]:
                cb = resultaat["data"]
                
                st.success("✅ Case Brief gegenereerd!")
                st.subheader("📋 Case Brief")
                
                # Toon de Case Brief in een overzichtelijke layout
                col_l, col_r = st.columns(2)
                
                with col_l:
                    st.markdown("**⚖️ Partijen**")
                    st.info(cb.get("partijen", "—"))
                    
                    st.markdown("**📋 Feiten**")
                    st.write(cb.get("feiten", "—"))
                    
                    st.markdown("**❓ Rechtsvraag**")
                    st.warning(cb.get("rechtsvraag", "—"))
                    
                    st.markdown("**🏛️ Procedure**")
                    st.write(cb.get("procedure", "—"))
                
                with col_r:
                    st.markdown("**💭 Overwegingen**")
                    st.write(cb.get("overwegingen", "—"))
                    
                    st.markdown("**⚡ Dictum (Uitkomst)**")
                    st.error(cb.get("dictum", "—"))
                    
                    st.markdown("**🎯 Juridisch Belang**")
                    st.success(cb.get("belang", "—"))
                
                st.markdown("**📜 Wetsartikelen**")
                wetsartikelen = cb.get("wetsartikelen", [])
                if wetsartikelen:
                    st.write(" • ".join(wetsartikelen))
                
                # Opslaan
                st.divider()
                tags_lijst = [t.strip() for t in eigen_tags.split(",") if t.strip()] if eigen_tags else []
                
                if st.button("💾 Opslaan in Kennisbank", type="primary"):
                    sla_case_brief_op(ecli, titel, cb, tags_lijst)
                    st.success("✅ Opgeslagen in je kennisbank!")
                    st.balloons()
            else:
                st.error(f"❌ AI-fout: {resultaat.get('fout', 'Onbekend')}")


# ═══════════════════════════════════════════════════════
# TAB 2: Kennisbank doorzoeken
# ═══════════════════════════════════════════════════════
with tab2:
    st.header("🔍 Kennisbank Doorzoeken")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        zoekterm = st.text_input("Zoek op tekst", placeholder="bijv. 'onrechtmatige daad' of '6:162 BW'")
    with col2:
        tag_filter = st.text_input("Filter op tag", placeholder="bijv. 'week 3'")
    
    if zoekterm or tag_filter or st.button("📚 Toon alle uitspraken"):
        resultaten = zoek_case_briefs(zoekterm, tag_filter)
        
        if resultaten:
            st.write(f"**{len(resultaten)} uitspraken gevonden**")
            for r in resultaten:
                with st.expander(f"⚖️ {r['titel']} — {r.get('instantie', '')} {r.get('datum', '')}"):
                    st.markdown(f"**ECLI:** `{r.get('ecli', 'N/A')}`")
                    st.markdown(f"**Rechtsvraag:** {r.get('rechtsvraag', '—')}")
                    st.markdown(f"**Belang:** {r.get('belang', '—')}")
                    if r.get('wetsartikelen'):
                        st.markdown(f"**Artikelen:** {' • '.join(r['wetsartikelen'])}")
                    if r.get('eigen_tags'):
                        st.markdown("**Jouw tags:** " + " ".join([f"`{t}`" for t in r['eigen_tags']]))
        else:
            st.info("Geen uitspraken gevonden. Voeg eerst uitspraken toe via de eerste tab.")


# ═══════════════════════════════════════════════════════
# TAB 3: Casus uitwerken (stappenplan)
# ═══════════════════════════════════════════════════════
with tab3:
    st.header("📚 Casus Uitwerken — Stappenplan")
    
    rechtsgebied = st.selectbox(
        "Kies een juridisch framework",
        ["Onrechtmatige daad (6:162 BW)", "Wanprestatie (6:74 BW)", 
         "Ongerechtvaardigde verrijking (6:212 BW)", "Eigen stappenplan"]
    )
    
    if rechtsgebied == "Onrechtmatige daad (6:162 BW)":
        st.subheader("Analyse 6:162 BW — Onrechtmatige Daad")
        
        with st.form("odd_stappenplan"):
            st.markdown("### Stap 1: Is er een onrechtmatige daad?")
            odd_type = st.multiselect(
                "Welk type onrechtmatige daad?",
                ["Inbreuk op een recht", "Strijd met een wettelijke plicht", 
                 "Strijd met maatschappelijke betamelijkheid"]
            )
            odd_toelichting = st.text_area("Toelichting:", height=80)
            
            st.markdown("### Stap 2: Kelderluik-criteria (bij gevaarzetting)")
            kans = st.slider("Kans op verwezenlijking schade", 0, 10, 5)
            ernst = st.slider("Ernst van de schade", 0, 10, 5)
            bezwaar = st.slider("Bezwaarlijkheid van voorzorgsmaatregelen", 0, 10, 5)
            
            st.markdown("### Stap 3: Toerekenbaarheid (6:162 lid 3 BW)")
            toerekenbaar = st.radio("Is de daad toerekenbaar?", ["Ja, schuld", "Ja, risico-aansprakelijkheid", "Nee"])
            
            st.markdown("### Stap 4: Schade en causaal verband")
            schade_aanwezig = st.checkbox("Schade aanwezig?")
            conditio_sine = st.checkbox("Conditio sine qua non-verband aanwezig?")
            toerekeningsnorm = st.text_area("Toerekening o.g.v. 6:98 BW:", height=60)
            
            st.markdown("### Stap 5: Relativiteit (6:163 BW)")
            relativiteit = st.radio(
                "Strekt de geschonden norm tot bescherming van de eiser?",
                ["Ja, relativiteit aanwezig", "Nee, relativiteitseis staat vordering in de weg"]
            )
            
            ingediend = st.form_submit_button("📝 Sla Analyse Op")
            
            if ingediend:
                st.success("✅ Analyse opgeslagen! (In MVP: weergegeven als samenvatting)")
                st.markdown(f"""
**Jouw OOD-analyse:**
- Type: {', '.join(odd_type) if odd_type else 'Niet ingevuld'}
- Kelderluik-score: kans={kans}/10, ernst={ernst}/10, bezwaar={bezwaar}/10
- Toerekenbaar: {toerekenbaar}
- Schade: {'✅' if schade_aanwezig else '❌'} | CSQn: {'✅' if conditio_sine else '❌'}
- Relativiteit: {relativiteit}
""")
```

### Projectstructuur

```
juridische-werkbank/
├── app.py                 # Hoofdapplicatie (Streamlit)
├── ecli_fetcher.py        # Rechtspraak.nl API koppeling
├── pdf_verwerker.py       # PDF tekstextractie
├── ai_samenvatting.py     # Groq/Llama koppeling
├── database.py            # Supabase koppeling
├── requirements.txt       # Dependencies
├── .env                   # API-sleutels (NIET in GitHub!)
└── .gitignore             # Bevat .env
```

**`requirements.txt`:**
```
streamlit==1.41.0
groq==0.12.0
supabase==2.9.0
pymupdf==1.24.0
python-dotenv==1.0.0
requests==2.32.0
```

---

## 8. Prompt Engineering Gids

### De anatomie van een goede juridische prompt voor Nederlands

Nederlandse juridische teksten kennen specifiek jargon dat LLMs zoals Llama 3.3 goed kennen, maar waarvoor je de AI wél moet sturen. De volgende technieken werken het best:

**Principe 1: Geef de AI een rol**
```
"Je bent een juridisch assistent gespecialiseerd in het Nederlandse recht, 
met expertise in burgerlijk recht, strafrecht en bestuursrecht."
```

**Principe 2: Specificeer de output-structuur vooraf**
Zonder structuur geeft de AI een vloeiende tekst. Met JSON-structuur krijg je direct bruikbare data voor je database.

**Principe 3: Gebruik juridische terminologie in de prompt zelf**
De AI "weet" dat woorden als "dictum", "rechtsoverweging", "procespartijen" en "ECLI" juridische betekenis hebben. Dit verbetert de output.

### Prompt Variant 1: Snelle Case Brief (standaard)

```python
PROMPT_STANDAARD = """
Maak een beknopte Case Brief van de onderstaande uitspraak voor een eerstejaars rechtenstudent.
Gebruik de volgende vaste structuur:

**FEITEN**: [Wat is er feitelijk gebeurd? Max 3 zinnen]
**PARTIJEN**: [Eiser vs. verweerder, met hun hoedanigheid]  
**RECHTSVRAAG**: [De centrale juridische vraag in één zin]
**OVERWEGINGEN**: [De kern van de juridische redenering]
**DICTUM**: [De eindbeslissing van de rechter]
**BELANG**: [Waarom is dit arrest/vonnis belangrijk?]
**WETSARTIKELEN**: [Alle geciteerde artikelen]

Houd het beknopt en begrijpelijk. Vermijd jargon waar mogelijk.

UITSPRAAK: {tekst}
"""
```

### Prompt Variant 2: Uitgebreide Annotatie (voor hogere jaren)

```python
PROMPT_ANNOTATIE = """
Je bent een juridisch docent die een arrest annoteert voor de Nederlandse Jurisprudentie (NJ).
Schrijf een uitgebreide annotatie van de volgende uitspraak met aandacht voor:

1. **Feitencomplex**: Uitgebreide feitenbeschrijving inclusief de processuele voorgeschiedenis
2. **Rechtsvragen**: Welke rechtsvragen worden beantwoord? (meerdere indien aanwezig)
3. **Juridisch kader**: Welke wettelijke bepalingen en eerdere jurisprudentie zijn relevant?
4. **Overwegingen van de Hoge Raad / rechter**: Stap-voor-stap analyse van de redenering
5. **Oordeel en motivering**: Is het oordeel overtuigend gemotiveerd?
6. **Precedentwerking**: Welke invloed heeft deze uitspraak op toekomstige zaken?
7. **Kritische noot**: Zijn er zwakke punten of alternatieve redeneringen?

Schrijf in academisch Nederlands. Verwijs expliciet naar de rechtsoverwegingen (r.o. x.x).

UITSPRAAK: {tekst}
"""
```

### Prompt Variant 3: Casus-koppeling (voor tentamenvoorbereiding)

```python
PROMPT_TENTAMEN = """
Analyseer het volgende arrest en beschrijf:
1. Welke rechtsvraag stond centraal?
2. Welk toetsingscriterium/welke maatstaf formuleert de rechter?
3. Hoe zou je dit criterium toepassen op een nieuwe casus met dezelfde feiten, maar waarbij:
   a) de schade twee keer zo groot is
   b) de veroorzaker handelde te goeder trouw

Gebruik de puntensgewijze methode zoals in een tentamen:
- Noem het toepasselijke artikel
- Pas de norm toe op de feiten  
- Trek een conclusie

ARREST: {tekst}
"""
```

### Tips voor betere resultaten met Nederlandse juridische teksten

**Probleem:** Het model hallucineert wetsartikelen.  
**Oplossing:** Voeg toe aan de systeem-prompt: *"Noem alleen wetsartikelen die expliciet in de tekst worden geciteerd. Noem nooit een artikel tenzij je het exact in de uitspraak kunt terugvinden."*

**Probleem:** Het model geeft Engelstalige output.  
**Oplossing:** Begin de systeem-prompt met: *"Antwoord UITSLUITEND in het Nederlands, ook als de uitspraak deels in andere talen is."*

**Probleem:** De samenvatting is te lang.  
**Oplossing:** Voeg toe: *"De totale Case Brief mag niet langer zijn dan 400 woorden."*

**Probleem:** Technisch cassatietaal wordt niet vereenvoudigd.  
**Oplossing:** Voeg toe: *"Herschrijf juridisch jargon in begrijpelijke taal voor een student die het eerste jaar rechten volgt."*

---

## 9. MVP Roadmap — 2 Weken Plan

### Week 1: Fundament bouwen

| Dag | Doel | Tijdsinschatting | Resultaat |
|---|---|---|---|
| **Dag 1** | Accounts aanmaken: Groq, Supabase, GitHub, Streamlit Cloud | 1 uur | Alle accounts actief |
| **Dag 1** | Lokale omgeving opzetten: `pip install`, `.env` configureren | 30 min | App start lokaal |
| **Dag 2** | `ecli_fetcher.py` bouwen en testen met 3 bekende ECLI's | 2 uur | ECLI-ophalen werkt |
| **Dag 2** | `pdf_verwerker.py` bouwen en testen met een PDF-arrest | 1 uur | PDF-extractie werkt |
| **Dag 3** | `ai_samenvatting.py` bouwen, prompt fine-tunen | 3 uur | AI genereert Case Brief |
| **Dag 4** | Supabase tabel aanmaken (SQL uit §6), `database.py` schrijven | 2 uur | Opslaan en ophalen werkt |
| **Dag 5** | Tab 1 van `app.py` bouwen (ECLI invoer + AI + opslaan) | 3 uur | Werkende eerste tab |

**Milestone einde Week 1:** Je kunt een ECLI invoeren, een Case Brief laten genereren, en opslaan in de database.

### Week 2: Afmaken en deployen

| Dag | Doel | Tijdsinschatting | Resultaat |
|---|---|---|---|
| **Dag 8** | Tab 2 bouwen: zoekfunctionaliteit | 2 uur | Zoeken werkt |
| **Dag 9** | Tab 3 bouwen: stappenplan OOD | 3 uur | Basis stappenplan werkt |
| **Dag 10** | Testen met 10 echte uitspraken, bugs fixen | 2 uur | Stabiele app |
| **Dag 11** | Push naar publieke GitHub repo | 30 min | Code op GitHub |
| **Dag 12** | Deploy op Streamlit Community Cloud | 1 uur | App live op internet |
| **Dag 12** | Feedback vragen aan 1-2 medestudenten | — | Eerste echte gebruikers |
| **Dag 13-14** | Bugs fixen op basis van feedback | variabel | Stabiele v0.1 |

**Milestone einde Week 2:** Werkende MVP live op internet, gedeeld met medestudenten.

### Deployen op Streamlit Community Cloud

```bash
# 1. Push je code naar GitHub (zorg dat .env NIET in de repo zit!)
git init
echo ".env" >> .gitignore
git add .
git commit -m "Juridische Werkbank MVP v0.1"
git push origin main

# 2. Ga naar share.streamlit.io
# 3. Klik "New app" → koppel GitHub repo → kies app.py
# 4. Voeg secrets toe via Settings → Secrets (vervangt .env):
#    GROQ_API_KEY = "gsk_..."
#    SUPABASE_URL = "https://..."
#    SUPABASE_KEY = "..."
```

---

## 10. Zero-Budget Plan — Limieten & Wanneer Betalen?

### Overzicht van alle gratis limieten

| Service | Gratis Limiet | Wat gebeurt er als je overschrijdt? | Wanneer betalen? |
|---|---|---|---|
| **Groq (Free Tier)** | ~6.000 tokens/min, ~14.400 req/dag voor Llama 3.3 70B | HTTP 429 fout — app geeft foutmelding | Bij >50 actieve studenten/dag |
| **Supabase (Free)** | 500 MB database, 2 projecten, pauzeert na 1 week inactiviteit | Database gestopt | Bij >1.000 opgeslagen uitspraken |
| **Streamlit Community Cloud** | 3 apps, 1 GB RAM, publieke GitHub repo vereist | App crasht bij geheugengebrek | Bij veel gelijktijdige gebruikers |
| **Rechtspraak.nl API** | 10 req/seconde | Tijdelijke blokkade | Nooit (ongelimiteerd dagelijks volume) |
| **GitHub (gratis)** | Onbeperkte publieke repos | — | Nooit voor dit project |

### Groq Free Tier — Praktische gevolgen

Llama 3.3 70B op de Free Tier heeft deze limieten (grofweg):

- **~6.000 tokens per minuut** — Een uitspraak van 3.000 woorden + samenvatting ≈ 5.000 tokens. Je kunt dus ~1 uitspraak per minuut verwerken.
- **~100 requests per dag** (afhankelijk van model en tijdstip)
- Limiet wordt elke minuut/dag gereset

**Oplossing als je de limiet raakt:** Voeg een wachtrij toe in Streamlit met `time.sleep(3)` tussen verzoeken, of schakel over op **Gemini Flash 2.0** van Google (ook gratis, hogere limieten, via `google-generativeai` package).

### Supabase Free Tier — Let op de pauze

Supabase pauzeert gratis projecten na **1 week inactiviteit**. De database herstart automatisch bij het eerste verzoek (duurt ~30 seconden). Gedurende een actief semester is dit geen probleem.

**Oplossing:** Voeg een ping-script toe dat elke 5 dagen een dummy-query uitvoert (via een gratis cron-service zoals `cron-job.org`).

### Wanneer wél betalen?

Betalen is zinvol als het project uitgroeit tot een serieuze tool voor meerdere studenten:

| Scenario | Aanbevolen upgrade | Kosten |
|---|---|---|
| >50 studenten dagelijks | Groq Developer Tier | ~$0.03/1M tokens (heel goedkoop) |
| >1.000 uitspraken opgeslagen | Supabase Pro | $25/maand |
| Privé GitHub repo nodig | GitHub — gratis voor studenten via GitHub Education | Gratis |
| Meer rekenkracht nodig | Streamlit → Hugging Face Spaces (betaald) of Railway.app | Variabel |

### Alternatief: 100% lokaal draaien (nul servers)

Als je geen cloud wilt, kun je de hele stack lokaal draaien:

- **Database:** SQLite (ingebouwd in Python, geen installatie nodig)
- **AI:** Ollama + Llama 3.2 3B (lokaal model, vereist ~4 GB RAM)
- **Frontend:** Streamlit lokaal op `localhost:8501`

Dit is ideaal voor persoonlijk gebruik maar minder geschikt voor samenwerken.

---

## Bronnen & Verdere Leesstof

| Bron | URL | Gebruik |
|---|---|---|
| Rechtspraak.nl Open Data | rechtspraak.nl/Uitspraken/Paginas/Open-Data.aspx | API documentatie (gratis) |
| Groq API Docs | console.groq.com/docs | Llama 3.3 aanroepen |
| Supabase Docs | supabase.com/docs | Database setup |
| Streamlit Docs | docs.streamlit.io | Frontend bouwen |
| Legal Intelligence | legalintelligence.com | Concurrerende tool |
| Feitlijn (Patroon) | patroon.ai | Gratis jurisprudentie-tool |
| PyMuPDF Docs | pymupdf.readthedocs.io | PDF-verwerking |
| WetSuite Project | wetsuite.knobs-dials.com | Python-bibliotheek voor Rechtspraak.nl |

---

*Rapport gegenereerd: Februari 2026. Alle genoemde gratis limieten zijn onderhevig aan wijziging door de respectievelijke dienstverleners. Controleer altijd de actuele voorwaarden via de officiële websites.*
