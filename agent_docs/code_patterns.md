# Code Patronen — Juridische Werkbank

## Het Gouden Patroon: Altijd Een Dict Teruggeven

Elke functie die een externe API aanroept (Groq, Supabase, Rechtspraak.nl) geeft ALTIJD een dict terug met `succes` en `data` of `fout`. Nooit een naakte waarde, nooit een exception naar boven laten bubbelen.

```python
# ✅ CORRECT — Veilig patroon
def haal_iets_op(parameter: str) -> dict:
    try:
        resultaat = externe_api.aanroep(parameter)
        return {"succes": True, "data": resultaat}
    except TimeoutError:
        return {"succes": False, "fout": "De verbinding duurde te lang. Probeer opnieuw."}
    except Exception as e:
        return {"succes": False, "fout": f"Er ging iets mis: {str(e)}"}

# ❌ FOUT — Geeft een naakte waarde, crasht de app bij fout
def haal_iets_op(parameter: str) -> str:
    return externe_api.aanroep(parameter)  # Crasht als de API niet reageert!
```

---

## Naamgevingsconventies

**Python (deze app is volledig Nederlandstalig):**
- Variabelen en functies: `snake_case` in het Nederlands → `uitspraak_tekst`, `genereer_case_brief`
- Klassen (zelden nodig in Streamlit): `PascalCase` → `CaseBriefGenerator`
- Constanten: `HOOFDLETTERS` → `MAX_TEKENS = 12000`
- Bestanden: `snake_case` → `ecli_fetcher.py`, `ai_samenvatting.py`

**Database (Supabase):**
- Tabellen: `snake_case` enkelvoud of meervoud consistent → `case_briefs`
- Kolommen: `snake_case` Nederlands → `eigen_tags`, `aangemaakt_op`

---

## Module Structuur (Elke Module Volgt Dit Patroon)

```python
# modules/voorbeeld_module.py
"""
Korte beschrijving van wat deze module doet.
Aanroepen: from modules.voorbeeld_module import hoofd_functie
"""

import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


# ── Constanten ──────────────────────────────────────────────────────────────

MAX_TEKENS = 12000
TIMEOUT_SECONDEN = 15


# ── Hulpfuncties ────────────────────────────────────────────────────────────

def _opschonen(tekst: str) -> str:
    """Private hulpfunctie (begint met _). Niet aanroepen vanuit app.py."""
    import re
    tekst = re.sub(r'\n{3,}', '\n\n', tekst)
    tekst = re.sub(r' {2,}', ' ', tekst)
    return tekst.strip()


# ── Publieke Functies ────────────────────────────────────────────────────────

def hoofd_functie(parameter: str) -> dict:
    """
    Beschrijving van wat deze functie doet.
    
    Args:
        parameter: Beschrijving van het argument
    
    Returns:
        {"succes": True, "data": resultaat} of
        {"succes": False, "fout": "begrijpelijke melding"}
    """
    if not parameter or not parameter.strip():
        return {"succes": False, "fout": "Parameter mag niet leeg zijn."}
    
    try:
        # ... implementatie
        return {"succes": True, "data": resultaat}
    except Exception as e:
        return {"succes": False, "fout": f"Er ging iets mis: {str(e)}"}
```

---

## App.py Structuur (Tabs)

```python
# app.py — Altijd in deze volgorde
import streamlit as st
from modules.ecli_fetcher import haal_uitspraak_op
from modules.ai_samenvatting import genereer_case_brief
from modules.database import sla_case_brief_op, zoek_case_briefs

# 1. Pagina-configuratie (altijd bovenaan)
st.set_page_config(
    page_title="Juridische Werkbank",
    page_icon="⚖️",
    layout="wide"
)

# 2. Titel
st.title("⚖️ Juridische Werkbank")
st.caption("Jouw persoonlijke kennisbank voor Nederlandse jurisprudentie")

# 3. Tabs (vaste structuur, niet wijzigen)
tab1, tab2, tab3 = st.tabs([
    "📄 Nieuwe Uitspraak",
    "🔍 Kennisbank Doorzoeken",
    "📚 Casus Uitwerken"
])

# 4. Tab-inhoud (elke tab in een with-blok)
with tab1:
    # ... Tab 1 code

with tab2:
    # ... Tab 2 code

with tab3:
    # ... Tab 3 code
```

---

## Foutafhandeling in de UI

```python
# Patroon voor elke knop-actie in Streamlit

if st.button("🤖 Analyseer met AI", type="primary"):
    
    # Valideer input VOOR de API-aanroep
    if not invoer.strip():
        st.error("❌ Voer eerst een ECLI-nummer in.")
        st.stop()  # Stopt verdere uitvoering van dit blok
    
    # Laad-indicator
    with st.spinner("Bezig... (dit kan 10-30 seconden duren)"):
        resultaat = genereer_case_brief(tekst, ecli)
    
    # Verwerk resultaat
    if resultaat["succes"]:
        st.success("✅ Case Brief gegenereerd!")
        # ... toon resultaat
    else:
        st.error(f"❌ {resultaat['fout']}")
        # Optioneel: meer hulp aanbieden
        with st.expander("💡 Wat kan ik proberen?"):
            st.write("- Controleer of het ECLI-nummer correct is")
            st.write("- Probeer het opnieuw (soms is de server even druk)")
            st.write("- Gebruik de 'Tekst plakken' optie als alternatief")
```

---

## JSON Verwerken Vanuit Groq

```python
import json

ruwe_output = completion.choices[0].message.content

# Veilig parsen (nooit direct json.loads zonder try/except)
try:
    case_brief = json.loads(ruwe_output)
    return {"succes": True, "data": case_brief}
except json.JSONDecodeError:
    # Soms geeft de AI extra tekst rondom de JSON
    # Probeer JSON eruit te halen
    import re
    json_match = re.search(r'\{.*\}', ruwe_output, re.DOTALL)
    if json_match:
        try:
            case_brief = json.loads(json_match.group())
            return {"succes": True, "data": case_brief}
        except json.JSONDecodeError:
            pass
    return {
        "succes": False,
        "fout": "AI gaf een onverwacht formaat terug. Probeer opnieuw.",
        "ruwe_output": ruwe_output[:200]  # Voor debugging
    }
```

---

## Tags Verwerken

```python
# Van tekst-invoer naar lijst (gebruiker typt: "6:162 BW, kelderluik, week 3")
def verwerk_tags(tags_invoer: str) -> list:
    """Zet kommagescheiden tekst om naar een schone lijst."""
    if not tags_invoer or not tags_invoer.strip():
        return []
    return [tag.strip().lower() for tag in tags_invoer.split(",") if tag.strip()]

# Gebruik:
tags_tekst = st.text_input("Tags (kommagescheiden)")
tags_lijst = verwerk_tags(tags_tekst)
# Resultaat: ["6:162 bw", "kelderluik", "week 3"]
```

---

## Veelgemaakte Fouten (Voorkom Deze)

```python
# ❌ API-sleutel hardcoded in code
client = Groq(api_key="gsk_mijnsleutel123")

# ✅ Correct
client = Groq(api_key=haal_secret_op("GROQ_API_KEY"))

# ❌ Engelstalige foutmelding aan gebruiker
st.error("Connection timeout. Please try again.")

# ✅ Correct
st.error("❌ Verbinding mislukt. Probeer het opnieuw.")

# ❌ Geen validatie voor API-aanroep
tekst = st.text_area("Tekst")
resultaat = genereer_case_brief(tekst)  # Crasht als tekst leeg is!

# ✅ Correct
tekst = st.text_area("Tekst")
if tekst.strip():
    resultaat = genereer_case_brief(tekst)
else:
    st.warning("⚠️ Voer eerst tekst in.")

# ❌ Lange uitspraak direct naar AI sturen
resultaat = genereer_case_brief(uitspraak_tekst)  # Kan 80.000 tekens zijn!

# ✅ Correct
resultaat = genereer_case_brief(bereid_tekst_voor(uitspraak_tekst))
```
