# Teststrategie — Juridische Werkbank

## Aanpak
Voor deze MVP gebruiken we **handmatige testprotocollen**. Na elke feature voer je de bijbehorende tests uit. Pas als alle vinkjes groen zijn, ga je naar de volgende feature.

Geen geautomatiseerde tests in de MVP — die voegen we toe in v2 als de basis stabiel is.

---

## Kwaliteitspoort Vóór Elke Commit

Voer dit altijd uit voordat je een `git commit` doet:

```bash
# 1. Start de app opnieuw (vangt import-fouten)
streamlit run app.py

# 2. Controleer op zichtbare Python-fouten in de terminal
# Als je een rood traceback ziet: fix het eerst

# 3. Controleer handmatig de feature die je net bouwde (zie protocollen hieronder)

# 4. Controleer op API-sleutels in code (nooit committen!)
grep -r "gsk_" .         # Groq-sleutel
grep -r "eyJhbGci" .     # Supabase-sleutel
```

---

## Testprotocol: Fase 1 — Fundament

Controleer na het opzetten van de basis:

```
[ ] streamlit run app.py opent de app in de browser zonder fout
[ ] De drie tabs zijn zichtbaar: "📄 Nieuwe Uitspraak", "🔍 Kennisbank", "📚 Casus Uitwerken"
[ ] .env bestand bestaat en bevat alle 3 sleutels
[ ] Supabase: tabel 'case_briefs' is zichtbaar in Table Editor
[ ] requirements.txt: alle packages installeren zonder fout
[ ] .gitignore: .env staat erin
```

---

## Testprotocol: Feature 1 — ECLI → Case Brief

Voer elke test uit en vink af als het werkt:

**Test 1A: Geldig ECLI (happy path)**
```
Invoer: ECLI:NL:HR:2002:AE7040 (Kelderluik-arrest — altijd beschikbaar)
Verwacht:
[ ] Spinner verschijnt tijdens laden
[ ] Binnen 30 seconden: Case Brief verschijnt
[ ] Alle velden gevuld: feiten, partijen, rechtsvraag, overwegingen, dictum, belang
[ ] Wetsartikelen-lijst is niet leeg
[ ] Tekst is in het Nederlands
```

**Test 1B: Nog een geldig ECLI**
```
Invoer: ECLI:NL:HR:1919:AG1776 (Lindenbaum/Cohen — klassiek arrest)
Verwacht:
[ ] Case Brief verschijnt zonder fout
[ ] Andere inhoud dan Test 1A (bewijst dat het daadwerkelijk ophaalt)
```

**Test 1C: Ongeldig ECLI**
```
Invoer: ECLI:NL:HR:BESTAAT:NIET
Verwacht:
[ ] Geen crash of Python-traceback
[ ] Rode foutmelding in het Nederlands
[ ] App blijft bruikbaar (kan opnieuw proberen)
```

**Test 1D: Leeg invoerveld**
```
Invoer: (niets ingevuld, direct op knop klikken)
Verwacht:
[ ] Geen API-aanroep gedaan
[ ] Oranje waarschuwing: "Voer eerst een ECLI-nummer in"
```

**Test 1E: Groq-fout simuleren**
```
Methode: Zet tijdelijk een verkeerde GROQ_API_KEY in .env
Verwacht:
[ ] Geen crash
[ ] Begrijpelijke foutmelding in het Nederlands
[ ] Herstel: zet de juiste sleutel terug, app werkt weer
```

---

## Testprotocol: Feature 2 — Kennisbank

**Test 2A: Case Brief opslaan**
```
Stap: Genereer een Case Brief (Test 1A), voeg tags in "kelderluik, 6:162 bw", klik Opslaan
Verwacht:
[ ] ✅ Succesbericht verschijnt
[ ] In Supabase dashboard: rij zichtbaar in case_briefs tabel
[ ] ECLI, tags en Case Brief-velden zijn opgeslagen
```

**Test 2B: Opgeslagen uitspraak terugvinden via zoeken**
```
Stap: Ga naar Tab 2, typ "kelderluik" in de zoekbalk
Verwacht:
[ ] Eerder opgeslagen uitspraak verschijnt
[ ] Klikken op uitspraak toont volledige Case Brief
```

**Test 2C: Filteren op tag**
```
Stap: Typ "6:162 bw" in het tagfilter-veld
Verwacht:
[ ] Alleen uitspraken met deze tag verschijnen
[ ] Uitspraken zonder deze tag zijn niet zichtbaar
```

**Test 2D: Notitie toevoegen**
```
Stap: Open een opgeslagen uitspraak, voeg notitie toe, sla op
Verwacht:
[ ] Notitie opgeslagen in Supabase
[ ] Notitie zichtbaar bij heropen van de uitspraak
```

**Test 2E: Dubbel opslaan (dezelfde ECLI)**
```
Stap: Sla hetzelfde ECLI-nummer twee keer op
Verwacht:
[ ] Geen fout (upsert werkt)
[ ] Slechts één rij in Supabase (niet twee)
```

**Test 2F: Lege kennisbank**
```
Stap: Zoek naar iets wat niet bestaat, bijv. "bestaat_niet_xyz"
Verwacht:
[ ] Geen crash
[ ] Bericht: "Geen uitspraken gevonden"
```

---

## Testprotocol: Feature 3 — Stappenplan OOD

**Test 3A: Alle stappen invullen**
```
Stap: Ga naar Tab 3, vul alle stappen in, klik op "Analyse tonen"
Verwacht:
[ ] Samenvatting verschijnt met alle ingevulde waarden
[ ] Correct weergegeven: onrechtmatigheid, Kelderluik-scores, toerekenbaarheid, schade, relativiteit
```

**Test 3B: Uitlegknop per stap**
```
Stap: Klik op "Wat betekent dit?" bij elke stap
Verwacht:
[ ] Uitleg verschijnt (bijv. wat betekent CSQn-verband?)
[ ] Uitleg sluit/verbergt zich na opnieuw klikken
```

**Test 3C: Analyse opslaan**
```
Stap: Vul analyse in, klik "Opslaan in Kennisbank"
Verwacht:
[ ] Opgeslagen in Supabase
[ ] Terug te vinden in Tab 2 met tag "ood-analyse"
```

**Test 3D: Lege velden**
```
Stap: Klik op "Analyse tonen" zonder iets in te vullen
Verwacht:
[ ] Geen crash
[ ] Samenvatting toont lege velden of standaardtekst
```

---

## Testprotocol: Lancering

Voer dit uit vlak voor je de URL deelt met medestudenten:

```
[ ] Deployment: app is live op Streamlit Community Cloud URL
[ ] Secrets: alle 3 sleutels geconfigureerd in Streamlit Secrets
[ ] Mobiel: URL geopend op telefoon, alle tabs werken
[ ] Tablet: getest op tablets (studenten gebruiken iPads)
[ ] ECLI-test op live URL: Kelderluik-arrest werkt
[ ] Opslaan-test op live URL: kennisbank werkt
[ ] Getest door 2 medestudenten (niet jijzelf)
[ ] Bekende bugs gedocumenteerd in README.md
```

---

## Wat Te Doen Bij Een Falende Test

1. **Lees de foutmelding** — de meeste fouten leggen zichzelf uit
2. **Vraag Claude** met dit patroon:
   ```
   Mijn test [TEST X] faalt in de Juridische Werkbank (Streamlit/Groq/Supabase).
   Foutmelding: [kopieer de fout]
   Relevante code: [plak de code]
   Wat ik probeer: [uitleg]
   Fix het en leg uit wat er mis was.
   ```
3. **Fix de bug VOOR je doorgaat** naar de volgende feature
