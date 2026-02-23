# Project Brief (Persistent) — Juridische Werkbank

## Productvisioen
Gratis web-app die Nederlandse rechtsstudenten helpt uitspraken te begrijpen, op te slaan en toe te passen — via automatische Case Briefs, een doorzoekbare kennisbank en interactieve stappenplannen.

---

## Kernregels (Nooit Afwijken)

### Taal
- **Alles in het Nederlands:** UI-teksten, foutmeldingen, code-comments, variabelenamen
- Uitzondering: variabelenamen die technische termen zijn (`uuid`, `url`, `api_key`)

### Architectuur
- `app.py` bevat alleen Streamlit UI-code (tabs, knoppen, tekst tonen)
- Alle logica zit in `modules/` (API-aanroepen, data-verwerking)
- Geen database-aanroepen direct in `app.py` — altijd via `modules/database.py`

### Veiligheid
- API-sleutels NOOIT in code — altijd via `haal_secret_op()`
- `.env` staat altijd in `.gitignore`
- Elke commit controleren: geen sleutels zichtbaar?

### Gebruikerservaring
- Elke actie heeft één duidelijke knop
- Laadtijden altijd aangeven met `st.spinner()`
- Foutmeldingen beginnen altijd met ❌ en zijn begrijpelijk voor niet-technici
- Succesmeldingen beginnen altijd met ✅

---

## Kwaliteitspoorten

Vóór elke `git commit`:
1. `streamlit run app.py` start zonder fout
2. De feature die je net bouwde werkt met de testprotocollen in `agent_docs/testing.md`
3. Geen API-sleutels zichtbaar in code
4. Geen `print()` statements (gebruik `st.write()` voor debugging)

---

## Bouwvolgorde (Nooit Overslaan)

1. Fase 1 volledig klaar → Dan pas Fase 2
2. Fase 2 volledig klaar → Dan pas Fase 3
3. Enzovoort (zie AGENTS.md roadmap)

---

## Sleutelcommando's

```bash
streamlit run app.py          # App lokaal starten
pip install -r requirements.txt  # Dependencies installeren
git add . && git commit -m "..."  # Committen
git push origin main           # Naar GitHub pushen
```

---

## Upgrade Drempels (Wanneer Gratis Tier Niet Meer Voldoet)

| Situatie | Actie |
|---|---|
| >50 AI-aanroepen/dag (Groq) | Overweeg Groq Developer tier (~$0.03/1M tokens) |
| >1.000 rijen in Supabase | Overweeg Supabase Pro ($25/maand) |
| App crasht door geheugen | Overweeg betaald hosting |
| Meerdere gebruikers willen eigen data | Login systeem toevoegen (Fase 2+) |

---

## Dit Document Bijwerken Wanneer

- Nieuwe dependency wordt toegevoegd aan `requirements.txt`
- Een architectuurbeslissing wordt gewijzigd
- Een nieuwe fase begint
- Projectnaam of URL verandert
