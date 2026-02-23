# GitHub Copilot Instructions — Juridische Werkbank

## Project Context
**App:** Juridische Werkbank  
**Stack:** Python · Streamlit · Groq (Llama 3.3 70B) · Supabase · Rechtspraak.nl API  
**Fase:** MVP Ontwikkeling  
**Gebruikersniveau:** Vibe-coder — leg uit wat je bouwt, schrijf begrijpelijke code met comments

## Altijd Lezen Eerst
Lees bij elke nieuwe taak:
- `AGENTS.md` — huidige fase, roadmap, wat NIET te doen
- `agent_docs/tech_stack.md` — stack details en code-voorbeelden
- `agent_docs/code_patterns.md` — verplichte patronen (foutafhandeling, naamgeving)

## Kernregels
1. **Plan eerst** — schets aanpak in bullets vóór je code schrijft
2. **Alles in het Nederlands** — variabelenamen, comments, foutmeldingen, UI-teksten
3. **Één feature tegelijk** — nooit verder dan de huidige fase in `AGENTS.md`
4. **Foutafhandeling altijd** — elke externe aanroep geeft `{"succes": True/False}` terug
5. **Geen API-sleutels in code** — altijd via `haal_secret_op()` uit `agent_docs/tech_stack.md`
6. **Leg uit wat je doet** — voeg comments toe zodat de gebruiker leert

## Verplicht Codepatroon (Uit `agent_docs/code_patterns.md`)
```python
def functie_naam(parameter: str) -> dict:
    try:
        resultaat = externe_api.aanroep(parameter)
        return {"succes": True, "data": resultaat}
    except Exception as e:
        return {"succes": False, "fout": f"Er ging iets mis: {str(e)}"}
```

## Commando's
```bash
streamlit run app.py          # App starten
pip install -r requirements.txt  # Dependencies installeren
source venv/bin/activate      # Venv activeren (Mac/Linux)
venv\Scripts\activate         # Venv activeren (Windows)
git add . && git commit -m "beschrijving"
git push origin main
```

## Wat NIET Te Doen
- Geen bestanden verwijderen zonder bevestiging
- Geen features bouwen buiten de huidige fase
- Geen Engelstalige foutmeldingen aan de gebruiker tonen
- Geen `print()` statements — gebruik `st.write()` voor debugging
- Nooit doorgaan als een feature niet werkt — fix eerst

## Testprotocollen
Zie `agent_docs/testing.md` voor exacte testprotocollen per feature.
Na elke feature: protocol doorlopen vóór `git commit`.
