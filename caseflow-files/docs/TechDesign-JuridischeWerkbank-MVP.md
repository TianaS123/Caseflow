# Technical Design Document
# Juridische Werkbank — MVP

**Versie:** 1.0  
**Status:** Klaar voor implementatie  
**Aangemaakt:** Februari 2026  
**Vorige documenten:** Onderzoeksrapport (Part 1) · PRD (Part 2)  
**Volgende stap:** AGENTS.md + configuratiebestanden (Part 4)

---

## Hoe We Het Bouwen

### Gekozen Aanpak: Python + Streamlit

Jouw stack is al volledig bepaald in het onderzoeksrapport. Dit document vertaalt die keuzes naar concrete bestanden, code en een bouwvolgorde.

**Waarom deze stack perfect past:**
- Streamlit is 100% Python — geen JavaScript nodig
- AI-assistenten (Claude, Cursor) kennen Streamlit uitstekend
- Gratis hosting via Streamlit Community Cloud
- Alle componenten (Groq, Supabase) hebben officiële Python-bibliotheken
- De hele stack is gratis tot ~50 actieve gebruikers/dag

### Alternatieven die zijn Overwogen

| Optie | Voordelen | Nadelen | Besluit |
|---|---|---|---|
| **Streamlit** ✅ | Pure Python, snel te bouwen, gratis hosting | Beperkte UI-flexibiliteit | **Gekozen** |
| Gradio | Ook Python, goed voor AI-demos | Minder geschikt voor databases en meerdere pagina's | Niet gekozen |
| FastAPI + React | Professioneler eindresultaat | Vereist JavaScript-kennis, veel complexer | V2 optie |
| Reflex | Python voor frontend én backend | Minder volwassen, kleinere community | Niet gekozen |

---

## Volledige Tech Stack

| Laag | Tool | Versie | Gratis Limiet | Officiële Docs |
|---|---|---|---|---|
| **Frontend + App** | Streamlit | 1.41+ | 3 apps, 1 GB RAM | docs.streamlit.io |
| **Hosting** | Streamlit Community Cloud | — | Gratis, publieke GitHub repo vereist | share.streamlit.io |
| **Database** | Supabase (PostgreSQL) | — | 500 MB, 2 projecten | supabase.com/docs |
| **AI-API** | Groq (Llama 3.3 70B) | llama-3.3-70b-versatile | ~100 req/dag | console.groq.com/docs |
| **PDF-verwerking** | PyMuPDF (fitz) | 1.24+ | Open-source | pymupdf.readthedocs.io |
| **Uitspraken ophalen** | Rechtspraak.nl Open Data API | — | Ongelimiteerd (max 10/sec) | data.rechtspraak.nl |
| **Versiebeheer** | GitHub | — | Publieke repos gratis | github.com |
| **Omgevingsbeheer** | python-dotenv | 1.0+ | Gratis | pypi.org/project/python-dotenv |

---

## Projectstructuur

Dit is de volledige mappenstructuur van je app. Elke bestandsnaam en de reden waarom het bestaat:

```
juridische-werkbank/
│
├── app.py                  ← Hoofdbestand: Streamlit UI + navigatie
│
├── modules/
│   ├── __init__.py         ← Maakt 'modules' een Python-pakket (leeg bestand)
│   ├── ecli_fetcher.py     ← Rechtspraak.nl API: ECLI → uitspraaktekst
│   ├── pdf_verwerker.py    ← PyMuPDF: PDF → tekst
│   ├── ai_samenvatting.py  ← Groq/Llama: tekst → gestructureerde Case Brief
│   └── database.py         ← Supabase: opslaan, ophalen, zoeken
│
├── prompts/
│   └── case_brief.py       ← Alle AI-prompts op één plek (makkelijk aanpassen)
│
├── requirements.txt        ← Alle Python-dependencies
├── .env                    ← API-sleutels (NOOIT in GitHub!)
├── .gitignore              ← Bevat .env en andere bestanden die niet in GitHub mogen
└── README.md               ← Uitleg voor anderen (en voor jezelf over 3 maanden)
```

**Waarom modules in een aparte map?**
Zo blijft `app.py` overzichtelijk — het beschrijft alleen de UI. De logica zit in `modules/`. Als de AI een bug moet fixen in de Supabase-koppeling, weet je exact in welk bestand dat is.

---

## Accounts Aanmaken (Dag 1)

### Stap 1: Groq API-sleutel
1. Ga naar [console.groq.com](https://console.groq.com)
2. Maak een gratis account aan
3. Ga naar "API Keys" → "Create API Key"
4. Kopieer de sleutel (begint met `gsk_`)
5. Bewaar in `.env` als: `GROQ_API_KEY=gsk_jouwsleutel`

### Stap 2: Supabase Project
1. Ga naar [supabase.com](https://supabase.com) → "Start your project"
2. Maak een gratis account aan
3. Klik "New project" → geef het een naam (bijv. "juridische-werkbank")
4. Onthoud je database-wachtwoord
5. Ga naar Project Settings → API
6. Kopieer "Project URL" en "anon public" sleutel
7. Bewaar in `.env`:
   ```
   SUPABASE_URL=https://jouwproject.supabase.co
   SUPABASE_KEY=eyJhbGci...
   ```

### Stap 3: GitHub Repository
1. Ga naar [github.com](https://github.com) → "New repository"
2. Naam: `juridische-werkbank`
3. Visibility: **Public** (vereist voor gratis Streamlit hosting)
4. Voeg `.gitignore` toe met "Python" template

### Stap 4: Streamlit Community Cloud
1. Ga naar [share.streamlit.io](https://share.streamlit.io)
2. Log in met je GitHub-account
3. Koppel je `juridische-werkbank` repository
4. *(Secrets configureer je later, bij het deployen)*

---

## Lokale Omgeving Opzetten (Dag 1–2)

### Vereisten
- Python 3.11+ geïnstalleerd ([python.org](https://python.org))
- Git geïnstalleerd ([git-scm.com](https://git-scm.com))
- VS Code of Cursor als code-editor

### Stap-voor-stap

```bash
# 1. Kloon je GitHub-repository naar je computer
git clone https://github.com/jouwgebruikersnaam/juridische-werkbank
cd juridische-werkbank

# 2. Maak een virtuele omgeving aan (houdt dependencies netjes gescheiden)
python -m venv venv

# 3. Activeer de virtuele omgeving
# Op Mac/Linux:
source venv/bin/activate
# Op Windows:
venv\Scripts\activate

# 4. Installeer alle dependencies
pip install -r requirements.txt

# 5. Maak je .env bestand aan
# Kopieer de inhoud hieronder en vul je eigen sleutels in

# 6. Start de app lokaal
streamlit run app.py
```

### `.env` bestand (vul jouw sleutels in)
```
GROQ_API_KEY=gsk_jouwsleutelkopierenvangroq
SUPABASE_URL=https://jouwproject.supabase.co
SUPABASE_KEY=eyJhbGci_jouwsupabasesleutel
```

### `requirements.txt`
```
streamlit==1.41.0
groq==0.12.0
supabase==2.9.0
pymupdf==1.24.0
python-dotenv==1.0.0
requests==2.32.0
```

### `.gitignore`
```
# Geheimen — NOOIT publiceren
.env
.env.local
.env.*.local

# Python
__pycache__/
*.pyc
*.pyo
venv/
.venv/

# Streamlit
.streamlit/secrets.toml

# OS-bestanden
.DS_Store
Thumbs.db
```

---

## Database Schema (Supabase)

Voer dit SQL-script eenmalig uit in de **Supabase SQL Editor** (te vinden via het dashboard):

```sql
-- ═══════════════════════════════════════════════
-- TABEL: case_briefs
-- Slaat alle gegenereerde samenvattingen op
-- ═══════════════════════════════════════════════
CREATE TABLE case_briefs (
    -- Identificatie
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    ecli            TEXT UNIQUE,                    -- bijv. "ECLI:NL:HR:2002:AE7040"
    
    -- Metadata van de uitspraak
    titel           TEXT NOT NULL,                  -- bijv. "Kelderluik-arrest"
    instantie       TEXT,                           -- bijv. "Hoge Raad"
    datum           TEXT,                           -- bijv. "2002-09-05"
    
    -- AI-gegenereerde Case Brief velden
    feiten          TEXT,
    partijen        TEXT,
    procedure       TEXT,
    rechtsvraag     TEXT,
    overwegingen    TEXT,
    dictum          TEXT,
    belang          TEXT,
    
    -- Gestructureerde data (arrays in PostgreSQL)
    wetsartikelen   TEXT[],                         -- {"6:162 BW", "6:163 BW"}
    zoektermen      TEXT[],                         -- AI-gegenereerde zoektermen
    
    -- Student-eigen velden
    eigen_tags      TEXT[],                         -- {"kelderluik", "tentamen week 3"}
    eigen_notities  TEXT,                           -- Persoonlijke aantekeningen
    
    -- Systeemvelden
    aangemaakt_op   TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    bijgewerkt_op   TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ═══════════════════════════════════════════════
-- INDEXEN voor snelle zoekopdrachten
-- ═══════════════════════════════════════════════

-- Full-text zoeken in het Nederlands
-- 'dutch' gebruikt Nederlandse stopwoorden en woordstammen
CREATE INDEX case_briefs_fts_idx ON case_briefs
    USING GIN (to_tsvector('dutch',
        COALESCE(titel, '') || ' ' ||
        COALESCE(feiten, '') || ' ' ||
        COALESCE(rechtsvraag, '') || ' ' ||
        COALESCE(overwegingen, '') || ' ' ||
        COALESCE(belang, '')
    ));

-- Snel filteren op tags en wetsartikelen
CREATE INDEX case_briefs_tags_idx         ON case_briefs USING GIN(eigen_tags);
CREATE INDEX case_briefs_wetsartikelen_idx ON case_briefs USING GIN(wetsartikelen);

-- ═══════════════════════════════════════════════
-- TRIGGER: bijgewerkt_op automatisch updaten
-- ═══════════════════════════════════════════════
CREATE OR REPLACE FUNCTION update_bijgewerkt_op()
RETURNS TRIGGER AS $$
BEGIN
    NEW.bijgewerkt_op = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_bijgewerkt_op
    BEFORE UPDATE ON case_briefs
    FOR EACH ROW EXECUTE FUNCTION update_bijgewerkt_op();
```

**Test of het werkte:** Ga in Supabase naar "Table Editor" — je ziet nu de tabel `case_briefs`.

---

## Data Flow: Van ECLI naar Opgeslagen Case Brief

```
GEBRUIKER typt ECLI  →  app.py (Streamlit)
                              │
                    ┌─────────▼─────────┐
                    │  ecli_fetcher.py  │
                    │                   │
                    │  GET request naar │
                    │  data.rechtspraak │
                    │  .nl/uitspraken/  │
                    │  content?id=ECLI  │
                    └─────────┬─────────┘
                              │ XML-respons
                    ┌─────────▼─────────┐
                    │  XML parsen       │
                    │  Tekst extraheren │
                    │  Max 15.000 tekens│
                    └─────────┬─────────┘
                              │ Schone tekst
                    ┌─────────▼─────────┐
                    │ ai_samenvatting.py│
                    │                   │
                    │  POST naar        │
                    │  api.groq.com     │
                    │  /v1/chat/        │
                    │  completions      │
                    │                   │
                    │  Model: llama-3.3 │
                    │  -70b-versatile   │
                    └─────────┬─────────┘
                              │ JSON Case Brief
                    ┌─────────▼─────────┐
                    │  app.py toont     │
                    │  Case Brief in UI │
                    │  Student voegt    │
                    │  tags toe         │
                    └─────────┬─────────┘
                              │ Student klikt Opslaan
                    ┌─────────▼─────────┐
                    │   database.py     │
                    │                   │
                    │  POST naar        │
                    │  Supabase REST    │
                    │  API              │
                    │                   │
                    │  UPSERT in        │
                    │  case_briefs tabel│
                    └───────────────────┘
```

---

## Feature Implementatie

### Feature 1: ECLI → Case Brief

**Bestanden:** `modules/ecli_fetcher.py` → `modules/ai_samenvatting.py` → `app.py` (Tab 1)

**Bouw in deze volgorde:**
1. Schrijf `ecli_fetcher.py` en test met `ECLI:NL:HR:2002:AE7040` (Kelderluik)
2. Schrijf `ai_samenvatting.py` en test met de opgehaalde tekst
3. Voeg Tab 1 toe aan `app.py`

**Testprotocol Feature 1:**
```
Test A: Geldig ECLI → verwacht: Case Brief verschijnt binnen 30 sec
Test B: Ongeldig ECLI (bijv. "ECLI:NL:HR:FOUT") → verwacht: foutmelding in het Nederlands
Test C: Groq-limiet bereikt → verwacht: foutmelding, geen crash
Test D: Controleer of alle Case Brief-velden zijn gevuld
```

---

### Feature 2: Kennisbank met Zoeken + Tags

**Bestanden:** `modules/database.py` → `app.py` (Tab 2)

**Bouw in deze volgorde:**
1. Schrijf `database.py` met functies: `sla_op()`, `zoek()`, `haal_op()`
2. Test `sla_op()` door handmatig een rij in Supabase te controleren
3. Test `zoek()` met een bekende zoekterm
4. Voeg Tab 2 toe aan `app.py`

**Testprotocol Feature 2:**
```
Test A: Sla een Case Brief op → verwacht: verschijnt in Supabase dashboard
Test B: Zoek op "kelderluik" → verwacht: juiste uitspraak gevonden
Test C: Filter op tag "6:162 BW" → verwacht: alleen relevante resultaten
Test D: Klik op opgeslagen uitspraak → verwacht: volledige Case Brief zichtbaar
Test E: Voeg notitie toe → verwacht: opgeslagen en zichtbaar bij heropen
```

---

### Feature 3: Stappenplan OOD (6:162 BW)

**Bestanden:** `app.py` (Tab 3) — alles in één tab, geen extra module nodig

**Bouw in deze volgorde:**
1. Bouw het formulier stap voor stap in Tab 3
2. Test alle 5 stappen (onrechtmatigheid → toerekenbaarheid → schade → CSQn → relativiteit)
3. Zorg dat de samenvatting aan het einde correct verschijnt
4. Voeg "Opslaan in kennisbank" toe als laatste actie

**Testprotocol Feature 3:**
```
Test A: Vul alle stappen in → verwacht: samenvatting verschijnt
Test B: Sla analyse op → verwacht: staat in Supabase met tag "ood-analyse"
Test C: Laat een stap leeg → verwacht: geen crash, lege velden behandeld
```

---

## Foutafhandeling — Strategie

Elke externe API-aanroep kan mislukken. Dit is hoe we dat afhandelen:

```python
# Patroon voor alle API-aanroepen in dit project
def veilige_api_aanroep(functie, *args, **kwargs):
    """
    Roept een functie aan en geeft altijd een dict terug:
    - Bij succes: {"succes": True, "data": resultaat}
    - Bij fout:   {"succes": False, "fout": "begrijpelijke melding"}
    """
    try:
        resultaat = functie(*args, **kwargs)
        return {"succes": True, "data": resultaat}
    except requests.exceptions.Timeout:
        return {"succes": False, "fout": "De verbinding duurde te lang. Probeer opnieuw."}
    except requests.exceptions.ConnectionError:
        return {"succes": False, "fout": "Geen internetverbinding. Controleer je verbinding."}
    except Exception as e:
        return {"succes": False, "fout": f"Er ging iets mis: {str(e)}"}
```

**In de Streamlit UI:**
```python
# Altijd controleren voor je iets toont
if resultaat["succes"]:
    st.success("✅ Gelukt!")
    # ... toon het resultaat
else:
    st.error(f"❌ {resultaat['fout']}")
    # ... toon geen half-ingevuld scherm
```

---

## AI-Assistent Strategie

### Welke AI voor welke taak

| Taak | Beste AI | Voorbeeldprompt |
|---|---|---|
| Nieuwe feature bouwen | Claude (deze chat) | "Schrijf de code voor [feature] op basis van mijn PRD en TDD" |
| Bug fixen | Claude of ChatGPT | "Ik krijg deze fout: [fout]. Mijn code: [code]. Hoe fix ik dit?" |
| UI verbeteren | Claude | "Maak Tab 2 overzichtelijker. Huidig code: [code]" |
| Begrijpen wat code doet | Claude | "Leg deze code uit alsof ik beginner ben: [code]" |
| Prompt verbeteren | Claude | "Mijn Case Briefs missen altijd de rechtsvraag. Verbeter deze prompt: [prompt]" |

### Prompt-templates voor dit project

**Voor nieuwe features:**
```
Ik bouw een Juridische Werkbank in Python/Streamlit.
Stack: Streamlit + Groq (Llama 3.3) + Supabase + Rechtspraak.nl API

Mijn huidige bestandsstructuur:
- app.py (Streamlit UI)
- modules/ecli_fetcher.py
- modules/ai_samenvatting.py  
- modules/database.py

Ik wil [beschrijf feature] toevoegen.
Vereisten uit mijn PRD:
- [vereiste 1]
- [vereiste 2]

Schrijf de code voor [bestandsnaam].py en geef aan waar ik het aanroep in app.py.
```

**Voor het fixen van bugs:**
```
Ik krijg deze fout in mijn Juridische Werkbank (Python/Streamlit):
[Plak hier de volledige foutmelding]

Dit is de relevante code:
[Plak hier de code]

Wat ik probeer te doen: [uitleg]
Wat er fout gaat: [uitleg]

Leg uit wat er mis is en geef de gecorrigeerde code.
```

**Voor het verbeteren van AI-output:**
```
Mijn Juridische Werkbank maakt Case Briefs via Groq/Llama 3.3.
De output is [te kort / te lang / mist X / hallucineert wetsartikelen / etc.]

Dit is mijn huidige prompt:
[Plak hier de prompt]

Dit is een voorbeeld van slechte output:
[Plak hier het probleem]

Verbeter de prompt zodat de output [gewenste verbetering].
```

---

## Deployment: Van Lokaal naar Internet

### Stap 1: Secrets instellen in Streamlit Cloud

Na het deployen, ga naar je app-instellingen op share.streamlit.io en voeg toe onder "Secrets":

```toml
# Dit is het formaat voor Streamlit Secrets (TOML)
# Plak dit in Settings → Secrets op Streamlit Community Cloud
GROQ_API_KEY = "gsk_jouwsleutel"
SUPABASE_URL = "https://jouwproject.supabase.co"
SUPABASE_KEY = "eyJhbGci_jouwsleutel"
```

**Let op:** Je `.env` werkt lokaal. Streamlit Cloud gebruikt `st.secrets` in productie. Gebruik dit patroon in je code zodat beide werken:

```python
import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()  # Laadt .env lokaal

def haal_secret_op(sleutel: str) -> str:
    """Werkt zowel lokaal (.env) als op Streamlit Cloud (st.secrets)."""
    try:
        return st.secrets[sleutel]       # Streamlit Cloud
    except (KeyError, AttributeError):
        return os.environ.get(sleutel)   # Lokaal via .env
```

### Stap 2: Deployen

```bash
# 1. Zorg dat alles in GitHub staat
git add .
git commit -m "MVP klaar voor deployment"
git push origin main

# 2. Ga naar share.streamlit.io
# 3. Klik "New app"
# 4. Selecteer: Repository = juridische-werkbank, Branch = main, File = app.py
# 5. Klik "Deploy"
# 6. Wacht 2-3 minuten
# 7. Voeg Secrets toe via Settings
# 8. App herstarten
```

### Stap 3: Testen na deployment

Controleer deze zaken op de live URL:
- [ ] Pagina laadt zonder fout
- [ ] ECLI-ophalen werkt (test met `ECLI:NL:HR:2002:AE7040`)
- [ ] Opslaan in database werkt
- [ ] Zoekfunctie geeft resultaten
- [ ] Werkt op telefoon (open URL op je mobiel)

---

## Prestaties & Limieten

### Groq Rate Limiting — Praktische omgang

De Groq gratis tier heeft een limiet van ~6.000 tokens per minuut. Bij normaal solo-gebruik is dit geen probleem. Bij groepsgebruik kun je dit toevoegen:

```python
import time

def genereer_case_brief_met_backoff(tekst: str, ecli: str = "") -> dict:
    """Probeert maximaal 3 keer bij rate limit fouten."""
    max_pogingen = 3
    
    for poging in range(max_pogingen):
        resultaat = genereer_case_brief(tekst, ecli)
        
        if resultaat["succes"]:
            return resultaat
        
        # Als het een rate limit fout is, wacht dan
        if "rate_limit" in str(resultaat.get("fout", "")).lower():
            wachttijd = (poging + 1) * 10  # 10, 20, 30 seconden
            st.warning(f"⏳ Even wachten ({wachttijd} sec) — te veel verzoeken tegelijk...")
            time.sleep(wachttijd)
        else:
            return resultaat  # Andere fout — niet opnieuw proberen
    
    return {"succes": False, "fout": "Groq-limiet bereikt. Probeer het over 1 minuut opnieuw."}
```

### Tekst afkappen voor Groq

Lange uitspraken (>15.000 tekens) kunnen de context window overschrijden. Gebruik altijd:

```python
def bereid_tekst_voor(tekst: str, max_tekens: int = 12000) -> str:
    """Kapt tekst af en voegt een indicator toe als dat nodig is."""
    if len(tekst) <= max_tekens:
        return tekst
    
    afgekapt = tekst[:max_tekens]
    # Kap af op het laatste punt (geen halve zin)
    laatste_punt = afgekapt.rfind('.')
    if laatste_punt > max_tekens * 0.8:  # Alleen als het niet te vroeg is
        afgekapt = afgekapt[:laatste_punt + 1]
    
    return afgekapt + "\n\n[Tekst afgekort wegens lengte. Samenvatting op basis van eerste deel.]"
```

---

## Kostenoverzicht

### Tijdens Ontwikkeling (Gratis)

| Service | Gratis Tier | Jij gebruikt | Kosten |
|---|---|---|---|
| Streamlit Community Cloud | 3 apps, 1 GB RAM | 1 app | €0 |
| Supabase | 500 MB, 2 projecten | 1 project, ~10 MB voor MVP | €0 |
| Groq | ~100 req/dag (Llama 3.3 70B) | <50 req/dag bij MVP | €0 |
| GitHub | Onbeperkt publiek | 1 publieke repo | €0 |
| Rechtspraak.nl API | Ongelimiteerd | Variabel | €0 |
| **Totaal** | | | **€0/maand** |

### Wanneer Overstappen naar Betaald?

| Drempel | Aanbevolen upgrade | Geschatte kosten |
|---|---|---|
| >50 actieve gebruikers/dag | Groq Developer Tier | ~$0.03/1M tokens (bijna gratis) |
| >1.000 opgeslagen uitspraken | Supabase Pro | $25/maand |
| App crasht door geheugen | Streamlit → Hugging Face Spaces betaald | $9/maand |

---

## Veiligheid & Privacy

### Wat wel en niet wordt opgeslagen

| Gegeven | Opgeslagen? | Waar? | Reden |
|---|---|---|---|
| Uitspraakteksten | Nee (alleen samenvatting) | — | Uitspraken zijn openbaar |
| Case Briefs (samenvatting) | Ja | Supabase | Kernfunctionaliteit |
| Eigen tags + notities | Ja | Supabase | Kernfunctionaliteit |
| Naam of e-mail van student | **Nee** | — | Geen login in MVP |
| IP-adres | Nee (Streamlit slaat dit op in logs) | Streamlit logs | Standaard webserver-logs |

### API-sleutels beschermen

```python
# GOED: Sleutels via omgevingsvariabelen
import os
api_key = os.environ.get("GROQ_API_KEY")

# FOUT: Sleutels direct in code (NOOIT doen)
api_key = "gsk_mijngeheimesleutel"  # ← Dit mag NOOIT in GitHub!
```

**Controleer voor elke `git commit`:**
- Staat `.env` in je `.gitignore`? 
- Zie je geen API-sleutels in je code?

---

## Onderhoud & Updates

### Maandelijkse controles (15 minuten)

```bash
# Controleer of dependencies updates hebben
pip list --outdated

# Update een specifiek pakket (test altijd lokaal eerst!)
pip install --upgrade streamlit

# Sla de nieuwe versies op
pip freeze > requirements.txt
```

### Als de app het niet meer doet na een update

```bash
# Ga terug naar de vorige versie
git log --oneline                    # Bekijk recente commits
git revert HEAD                      # Maak de laatste commit ongedaan
git push origin main                 # Pushes de revert naar GitHub
# Streamlit herdeployt automatisch
```

---

## Succeschecklist

### Voor je begint met bouwen
- [ ] Alle 4 accounts aangemaakt (Groq, Supabase, GitHub, Streamlit Cloud)
- [ ] `.env` bestand aangemaakt met alle 3 sleutels
- [ ] `pip install -r requirements.txt` succesvol uitgevoerd
- [ ] `streamlit run app.py` opent de app lokaal in de browser
- [ ] Supabase tabel aangemaakt via SQL Editor

### Tijdens het bouwen
- [ ] Na elke feature: testen met de bovenstaande testprotocollen
- [ ] Na elke werkende feature: `git commit -m "Feature X werkend"`
- [ ] Foutmeldingen zijn altijd in het Nederlands
- [ ] Geen API-sleutels in code of GitHub

### Voor de lancering
- [ ] Alle P0-features werken end-to-end
- [ ] Getest met 10 echte ECLI-nummers
- [ ] Werkt op mobiel (open de live URL op je telefoon)
- [ ] Getest door minimaal 2 medestudenten
- [ ] Secrets geconfigureerd op Streamlit Community Cloud
- [ ] App live en bereikbaar via publieke URL

---

## Wanneer Vastkomen

### De Debug-stappenreeks

1. **Lees de foutmelding goed** — de meeste fouten leggen zichzelf al uit
2. **Zoek de exacte foutmelding op Google** — iemand heeft dit eerder gehad
3. **Vraag Claude** met het debuggingprompt uit §"AI-Assistent Strategie"
4. **Controleer de documentatie:**
   - Streamlit-probleem? → docs.streamlit.io
   - Groq-probleem? → console.groq.com/docs
   - Supabase-probleem? → supabase.com/docs
5. **Herstart de app** — soms lost dit kleine problemen op

### Veelvoorkomende problemen

| Fout | Waarschijnlijke oorzaak | Oplossing |
|---|---|---|
| `KeyError: 'GROQ_API_KEY'` | `.env` niet geladen of verkeerde naam | Controleer `.env` bestand en variabelenamen |
| `401 Unauthorized` (Groq) | Verkeerde of verlopen API-sleutel | Genereer een nieuwe sleutel op console.groq.com |
| `postgrest.exceptions.APIError` | Supabase-sleutel of URL fout | Kopieer opnieuw van Supabase dashboard |
| Streamlit app crasht bij grote PDF | PDF > 15.000 tekens zonder afkapping | Voeg `tekst = tekst[:12000]` toe voor de AI-aanroep |
| `XMLParseError` bij ECLI-ophalen | Rechtspraak.nl geeft onverwacht formaat | Voeg try/except toe rondom XML-parser |

---

*Technical Design Document: Juridische Werkbank MVP*  
*Aanpak: Python + Streamlit (Vibe-coder pad)*  
*Geschatte bouwtijd: 2 weken*  
*Geschatte kosten: €0/maand*  
*Volgende stap: AGENTS.md + tool-configuratie (Part 4)*
