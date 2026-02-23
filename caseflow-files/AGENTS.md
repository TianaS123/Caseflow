# AGENTS.md — Master Plan: Juridische Werkbank

## Project Overzicht
**App:** Juridische Werkbank  
**Doel:** Gratis web-app die Nederlandse rechtsstudenten helpt uitspraken te begrijpen, op te slaan en toe te passen  
**Stack:** Python · Streamlit · Groq (Llama 3.3 70B) · Supabase (PostgreSQL) · Rechtspraak.nl Open Data API  
**Hosting:** Streamlit Community Cloud (gratis)  
**Huidige Fase:** Fase 1 — Fundament

---

## Hoe Ik Moet Denken

1. **Begrijp de intentie eerst** — Voordat ik antwoord, stel ik vast wat de gebruiker écht nodig heeft
2. **Vraag als ik twijfel** — Als kritieke informatie ontbreekt, vraag ik eerst één duidelijke vraag
3. **Plan vóór coderen** — Ik schets een aanpak en wacht op goedkeuring vóór implementatie
4. **Verifieer na wijzigingen** — Na elke feature test ik lokaal en bevestig dat het werkt
5. **Leg afwegingen uit** — Bij aanbevelingen noem ik ook alternatieven
6. **Één feature tegelijk** — Ik bouw incrementeel, niet alles tegelijk

---

## Plan → Uitvoeren → Verifiëren (Verplicht)

1. **Plan:** Schets een korte aanpak in bullets, wacht op "ga verder" van de gebruiker
2. **Uitvoeren:** Implementeer één feature volledig
3. **Verifiëren:** Controleer of het werkt via testprotocol in `agent_docs/testing.md`
4. **Fix eerst:** Los problemen op vóór je doorgaat naar de volgende feature

---

## Context Bestanden (Laad alleen wat nodig is)

| Bestand | Wanneer laden |
|---|---|
| `agent_docs/tech_stack.md` | Bij technische vragen over stack of libraries |
| `agent_docs/code_patterns.md` | Bij het schrijven van nieuwe code |
| `agent_docs/project_brief.md` | Bij twijfel over conventies of architectuur |
| `agent_docs/product_requirements.md` | Bij twijfel over wat wél/niet gebouwd moet worden |
| `agent_docs/testing.md` | Na elke feature: testprotocollen |

---

## Huidige Status (Dit Bijhouden!)

**Laatst Bijgewerkt:** Februari 2026  
**Bezig Met:** Fase 1 — Project opzetten  
**Recent Afgerond:** AGENTS.md aangemaakt  
**Geblokkeerd Door:** Geen

---

## Roadmap

### Fase 1: Fundament ← JE BENT HIER
- [ ] Projectstructuur aanmaken (mappen + lege bestanden)
- [ ] `requirements.txt` + `venv` werkend
- [ ] `.env` bestand met alle 3 sleutels
- [ ] Supabase tabel aangemaakt via SQL uit `agent_docs/tech_stack.md`
- [ ] `streamlit run app.py` opent lege app lokaal

### Fase 2: Feature 1 — ECLI → Case Brief
- [ ] `modules/ecli_fetcher.py` — Rechtspraak.nl API
- [ ] `modules/ai_samenvatting.py` — Groq/Llama koppeling
- [ ] Tab 1 in `app.py` — ECLI invoer + AI resultaat tonen
- [ ] Testprotocol Feature 1 doorlopen (zie `agent_docs/testing.md`)

### Fase 3: Feature 2 — Kennisbank
- [ ] `modules/database.py` — Supabase koppeling
- [ ] Tab 1 uitbreiden: tags toevoegen + opslaan
- [ ] Tab 2 in `app.py` — Zoeken + tagfilter + resultaten
- [ ] Testprotocol Feature 2 doorlopen

### Fase 4: Feature 3 — Stappenplan OOD
- [ ] Tab 3 in `app.py` — OOD 6:162 BW formulier
- [ ] Samenvatting + opslaan in kennisbank
- [ ] Testprotocol Feature 3 doorlopen

### Fase 5: Lancering
- [ ] Testen op mobiel
- [ ] Deployment op Streamlit Community Cloud
- [ ] Secrets configureren
- [ ] Getest door 2 medestudenten
- [ ] Live URL gedeeld

---

## Wat NIET Te Doen

- **NIET** bestanden verwijderen zonder expliciete bevestiging
- **NIET** het database schema wijzigen zonder eerst de bestaande data te bespreken
- **NIET** features bouwen die niet in de huidige fase staan
- **NIET** doorgaan als een feature niet werkt — fix eerst
- **NIET** API-sleutels in code zetten (alleen via `.env` of `st.secrets`)
- **NIET** Engelstalige foutmeldingen tonen aan de gebruiker — altijd vertalen naar Nederlands
- **NIET** meer dan één feature tegelijk implementeren
