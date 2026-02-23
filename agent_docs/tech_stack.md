# Tech Stack & Tools — Juridische Werkbank

## Volledige Stack

| Laag | Tool | Versie | Gratis Limiet |
|---|---|---|---|
| Frontend + App | Streamlit | 1.41+ | 3 apps, 1 GB RAM |
| Hosting | Streamlit Community Cloud | — | Gratis, publieke GitHub repo |
| Database | Supabase (PostgreSQL) | — | 500 MB, 2 projecten |
| AI-API | Groq · Llama 3.3 70B | llama-3.3-70b-versatile | ~100 req/dag |
| PDF-verwerking | PyMuPDF (fitz) | 1.24+ | Open-source |
| Uitspraken API | Rechtspraak.nl Open Data | — | Ongelimiteerd, max 10 req/sec |

## requirements.txt (Exacte Versies)

```
streamlit==1.41.0
groq==0.12.0
supabase==2.9.0
pymupdf==1.24.0
python-dotenv==1.0.0
requests==2.32.0
```

---

## Initialisatie Patroon (Elke Module)

Gebruik altijd dit patroon voor het laden van API-sleutels — werkt zowel lokaal (`.env`) als op Streamlit Cloud (`st.secrets`):

```python
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def haal_secret_op(sleutel: str) -> str:
    """Werkt lokaal via .env én op Streamlit Cloud via st.secrets."""
    try:
        return st.secrets[sleutel]       # Streamlit Cloud
    except (KeyError, AttributeError):
        return os.environ.get(sleutel)   # Lokaal
```

---

## Groq Client Setup

```python
# modules/ai_samenvatting.py
from groq import Groq

client = Groq(api_key=haal_secret_op("GROQ_API_KEY"))

completion = client.chat.completions.create(
    model="llama-3.3-70b-versatile",   # Altijd dit model gebruiken
    messages=[
        {"role": "system", "content": systeem_prompt},
        {"role": "user", "content": gebruiker_prompt}
    ],
    temperature=0.1,                    # Laag = consistenter, minder hallucinaties
    max_tokens=1500,
    response_format={"type": "json_object"},  # Forceer JSON
)
```

---

## Supabase Client Setup

```python
# modules/database.py
from supabase import create_client, Client

supabase: Client = create_client(
    haal_secret_op("SUPABASE_URL"),
    haal_secret_op("SUPABASE_KEY")
)

# Opslaan (upsert = update als ECLI al bestaat)
supabase.table("case_briefs").upsert(data, on_conflict="ecli").execute()

# Ophalen
supabase.table("case_briefs").select("*").eq("id", id).single().execute()

# Zoeken (full-text, Nederlands)
supabase.table("case_briefs").select("*").text_search(
    "kolom", zoekterm, config="dutch"
).execute()

# Filteren op tag (array-kolom)
supabase.table("case_briefs").select("*").contains("eigen_tags", [tag]).execute()
```

---

## Database Schema

Eenmalig uitvoeren in Supabase SQL Editor:

```sql
CREATE TABLE case_briefs (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    ecli            TEXT UNIQUE,
    titel           TEXT NOT NULL,
    instantie       TEXT,
    datum           TEXT,
    feiten          TEXT,
    partijen        TEXT,
    procedure       TEXT,
    rechtsvraag     TEXT,
    overwegingen    TEXT,
    dictum          TEXT,
    belang          TEXT,
    wetsartikelen   TEXT[],
    zoektermen      TEXT[],
    eigen_tags      TEXT[],
    eigen_notities  TEXT,
    aangemaakt_op   TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    bijgewerkt_op   TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX case_briefs_fts_idx ON case_briefs
    USING GIN (to_tsvector('dutch',
        COALESCE(titel, '') || ' ' ||
        COALESCE(feiten, '') || ' ' ||
        COALESCE(rechtsvraag, '') || ' ' ||
        COALESCE(overwegingen, '') || ' ' ||
        COALESCE(belang, '')
    ));

CREATE INDEX case_briefs_tags_idx ON case_briefs USING GIN(eigen_tags);
CREATE INDEX case_briefs_wetsartikelen_idx ON case_briefs USING GIN(wetsartikelen);
```

---

## Rechtspraak.nl API

```python
# Basis-URL voor uitspraken ophalen
BASE_URL = "https://data.rechtspraak.nl/uitspraken/content?id={ecli}"

# Namespaces voor XML-parsen
NAMESPACES = {
    'atom':    'http://www.w3.org/2005/Atom',
    'rs':      'http://www.rechtspraak.nl/schema/rechtspraak-1.0',
    'dc':      'http://purl.org/dc/elements/1.1/',
    'dcterms': 'http://purl.org/dc/terms/'
}

# Uitspraagtekst zit in dit XML-element:
# {http://www.rechtspraak.nl/schema/rechtspraak-1.0}uitspraak
```

---

## Streamlit UI Patronen

```python
# 3-tab navigatie (standaard structuur voor deze app)
tab1, tab2, tab3 = st.tabs([
    "📄 Nieuwe Uitspraak",
    "🔍 Kennisbank Doorzoeken",
    "📚 Casus Uitwerken"
])

# Foutafhandeling in UI (altijd Nederlands)
if resultaat["succes"]:
    st.success("✅ Gelukt!")
else:
    st.error(f"❌ {resultaat['fout']}")

# Laad-indicator bij AI-aanroepen
with st.spinner("AI analyseert de uitspraak... (10-30 seconden)"):
    resultaat = genereer_case_brief(tekst, ecli)
```

---

## Tekst Afkappen (Altijd Toepassen Voor AI)

```python
def bereid_tekst_voor(tekst: str, max_tekens: int = 12000) -> str:
    if len(tekst) <= max_tekens:
        return tekst
    afgekapt = tekst[:max_tekens]
    laatste_punt = afgekapt.rfind('.')
    if laatste_punt > max_tekens * 0.8:
        afgekapt = afgekapt[:laatste_punt + 1]
    return afgekapt + "\n\n[Tekst afgekort wegens lengte.]"
```

---

## Officiële Documentatie

- Streamlit: https://docs.streamlit.io
- Groq Python SDK: https://console.groq.com/docs/openai
- Supabase Python: https://supabase.com/docs/reference/python/introduction
- PyMuPDF: https://pymupdf.readthedocs.io
- Rechtspraak.nl API: https://data.rechtspraak.nl
