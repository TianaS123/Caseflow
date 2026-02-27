# CLAUDE.md — Claude Configuratie voor Juridische Werkbank

## Project Context
**App:** Juridische Werkbank  
**Stack:** Python · Streamlit · Groq · Supabase  
**Fase:** MVP Ontwikkeling  
**Gebruikersniveau:** Vibe-coder (AI schrijft code, gebruiker test en stuurt)  
**Taal:** Alles in het Nederlands — code-comments, foutmeldingen, UI-teksten

---

## Instructies

1. **Lees altijd eerst `AGENTS.md`** — dit bevat de huidige fase en openstaande taken
2. **Raadpleeg `agent_docs/`** voor stack-details, codepatronen en testprotocollen
3. **Plan vóór coderen** — schets aanpak in bullets, wacht op "ga verder"
4. **Één feature tegelijk** — bouw incrementeel, test na elke stap
5. **Geen verassingen** — kondig aan welke bestanden je aanmaakt of wijzigt
6. **Leg uit wat je doet** — de gebruiker leert terwijl je bouwt
7. **Foutmeldingen in het Nederlands** — alle `st.error()` en `st.warning()` in het Nederlands

---

## Commando's

```bash
# Lokaal starten
streamlit run app.py

# Dependencies installeren
pip install -r requirements.txt

# Virtuele omgeving activeren (Mac/Linux)
source venv/bin/activate

# Virtuele omgeving activeren (Windows)
venv\Scripts\activate
```

---

## Git Workflow

### Branches
- **`main`** → live app op Streamlit Cloud (alleen stabiele code)
- **`dev`** → ontwikkel- en testbranch (hier werk je dagelijks)

### Dagelijks werken (op dev)
```bash
# Zorg dat je op dev zit
git checkout dev

# Wijzigingen opslaan en pushen
git add .
git commit -m "Beschrijving van wat je hebt gebouwd"
git push origin dev
```

### Klaar voor productie (dev → main)
```bash
# Schakel naar main
git checkout main

# Merge dev in main
git merge dev

# Push naar GitHub → Streamlit Cloud deployt automatisch
git push origin main

# Terug naar dev voor verder werken
git checkout dev
```

---

## Bestandsstructuur (Nooit Afwijken)

```
juridische-werkbank/
├── app.py                  ← Streamlit UI (tabs + navigatie)
├── modules/
│   ├── __init__.py
│   ├── ecli_fetcher.py
│   ├── pdf_verwerker.py
│   ├── ai_samenvatting.py
│   └── database.py
├── prompts/
│   └── case_brief.py
├── agent_docs/             ← Documentatie voor AI-assistenten
├── AGENTS.md
├── CLAUDE.md
├── requirements.txt
├── .env                    ← NOOIT in GitHub
└── .gitignore
```

---

## Verwezen Documentatie
- Volledige stack: `agent_docs/tech_stack.md`
- Codepatronen: `agent_docs/code_patterns.md`
- Projectregels: `agent_docs/project_brief.md`
- Vereisten: `agent_docs/product_requirements.md`
- Testprotocollen: `agent_docs/testing.md`
