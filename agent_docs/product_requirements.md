# Product Vereisten — Juridische Werkbank

## Kernprobleem
Bestaande juridische tools (Legal Intelligence, Rechtsorde) zijn zoekplatforms voor professionals. Ze geven studenten de uitspraak, maar helpen niet bij *begrijpen, onthouden of toepassen*. Er is geen tool die de studenten-workflow ondersteunt.

## Primaire Gebruiker
Nederlandse rechtsstudenten, alle studiejaren. Primair voor tentamenvoorbereiding en casus-uitwerking.

**Persona Lotte:** Tweedejaars rechten, tentamen morgen over OOD. Vindt een ECLI op Rechtspraak.nl maar begrijpt de 8 pagina's niet. Wil binnen 1 minuut de kern begrijpen.

---

## Must-Have Features (MVP — Lancering Geblokkeerd Zonder)

### Feature 1: ECLI → Automatische Case Brief
**User Story:** Als rechtenstudent wil ik een ECLI-nummer invoeren zodat ik binnen één minuut de kern van de uitspraak begrijp.

**Acceptatiecriteria:**
- Student voert ECLI in en klikt "Analyseer"
- App haalt tekst op van Rechtspraak.nl
- AI genereert Case Brief met: feiten, partijen, rechtsvraag, overwegingen, dictum, belang, wetsartikelen
- Output in het Nederlands
- Verwerking < 30 seconden
- Begrijpelijke foutmelding bij fout

### Feature 2: Persoonlijke Kennisbank met Zoeken + Tags
**User Story:** Als rechtenstudent wil ik uitspraken opslaan met eigen tags zodat ik ze later snel kan terugvinden.

**Acceptatiecriteria:**
- Case Brief opslaan met één klik
- Tags toevoegen (kommagescheiden invoer)
- Zoekbalk zoekt over alle tekstvelden
- Tag-filter toont uitspraken per tag
- Klik op uitspraak toont volledige Case Brief
- Notities toevoegen aan opgeslagen uitspraken

### Feature 3: Interactief Stappenplan — OOD 6:162 BW
**User Story:** Als rechtenstudent wil ik een casus systematisch uitwerken via een stappenplan zodat ik geen stap oversla.

**Acceptatiecriteria:**
- Stappenplan: onrechtmatigheid → Kelderluik → toerekenbaarheid → schade → CSQn → relativiteit
- Uitlegknop per stap
- Samenvatting van analyse aan het einde
- Analyse opslaan in kennisbank

---

## Nice to Have (P1 — Als Tijd Over)
- PDF uploaden → Case Brief
- Tekst plakken → Case Brief
- Wetsartikel-filter in kennisbank

---

## Niet in MVP (Voor Versie 2)
- Notificaties / herinneringen
- Gebruikersaccounts / inloggen
- Samenwerken / gedeelde kennisbank
- Export naar Word/PDF
- Meer stappenplannen (wanprestatie, bestuursrecht)

---

## Succesmetrics (Eerste 30 Dagen)

| Metric | Doel |
|---|---|
| Actieve gebruikers | 10–30 studenten |
| Gegenereerde Case Briefs | ≥ 50 |
| Opgeslagen uitspraken | ≥ 30 |
| Terugkerende gebruikers | ≥ 5 (gebruikt app >2×) |
| Kwalitatief | Positieve reactie van 3+ medestudenten |

---

## Design Vibe
**Compact, snel, studentvriendelijk**

- Geen onnodige knoppen — elke actie heeft één knop
- Resultaat eerst — Case Brief direct zichtbaar, uitleg daarna
- Bekende patronen — tabs, tags, zoekbalk
- Kleurcodering: ✅ groen = opgeslagen, ⚠️ oranje = let op, ❌ rood = fout

---

## Beperkingen
- Budget: €0/maand
- Tijdlijn: 2 weken naar werkend prototype
- Geen login vereist in MVP
- Alle data gedeeld op één Supabase-instantie (acceptabel voor MVP-schaal)
