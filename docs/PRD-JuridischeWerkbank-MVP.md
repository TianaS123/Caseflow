# Product Requirements Document
# Juridische Werkbank — MVP

**Versie:** 1.0  
**Status:** Draft — Klaar voor Technisch Ontwerp  
**Aangemaakt:** Februari 2026  
**Volgende stap:** Technical Design Document (Part 3)

---

## Product Overview

| Veld | Waarde |
|---|---|
| **App-naam** | Juridische Werkbank |
| **Tagline** | *Van uitspraak naar inzicht — in minder dan een minuut* |
| **Lanceerdoel** | 10–30 medestudenten actief gebruiken binnen 4 weken na lancering |
| **Doelgroep** | Nederlandse rechtsstudenten, alle studiejaren |
| **Budget** | €0 (uitsluitend gratis tiers) |
| **Tijdlijn** | 2 weken naar werkend prototype |
| **Platform** | Web-app (desktop + mobiel) |

---

## Wie Het Voor Is

### Primaire Gebruiker: De Rechtenstudent

Rechtenstudenten in Nederland lezen tijdens hun studie honderden uitspraken. Deze zijn geschreven in een dicht juridisch register, vaak tientallen pagina's lang, met genummerde rechtsoverwegingen en verwijzingen naar andere arresten. Begrijpen *wat* er staat is één uitdaging; begrijpen *waarom het ertoe doet* is een tweede.

Bestaande tools — Legal Intelligence, Rechtsorde, Rechtspraak.nl — zijn ontworpen voor advocaten en juristen die uitspraken *zoeken*. Ze helpen een student niet met *begrijpen, onthouden* of *toepassen*.

**Hun huidige frustraties:**
- Een uitspraak van 8 pagina's lezen kost een uur; de essentie begrijpen kost nog langer
- Aantekeningen staan verspreid over Word-bestanden, Notion-pagina's en losse papieren
- Tijdens tentamenvoorbereiding is er geen systematische manier om geleerde stof terug te vinden
- Casus-uitwerking gaat trial-and-error: welke criteria moet ik ook alweer aflopen?

**Wat ze nodig hebben:**
- Een gestructureerde samenvatting die ze direct snappen
- Eén plek om al hun uitspraken op te slaan en terug te vinden
- Een houvast bij het uitwerken van casussen

### Gebruikerspersona: Lotte

> *Lotte is tweedejaars rechten aan de Universiteit Utrecht. Ze heeft morgen een tentamen over onrechtmatige daad en werkt door een lijst van tien verplichte arresten. Ze opent ECLI:NL:HR:1965:AB7079 op Rechtspraak.nl — acht pagina's dicht juridisch proza. Ze plakt het ECLI-nummer in de Juridische Werkbank. Dertig seconden later heeft ze een heldere Case Brief: feiten, rechtsvraag, de Kelderluik-criteria uitgelegd, het dictum, en waarom dit arrest nog steeds wordt aangehaald. Ze voegt de tag "kelderluik" en "6:162 BW" toe en slaat op. Bij het tiende arrest heeft ze een doorzoekbare kennisbank gebouwd — klaar voor haar tentamen.*

---

## Het Probleem

Bestaande juridische platforms zijn **zoektools voor professionals**, niet **leertools voor studenten**. Ze geven je de uitspraak, maar helpen je er niet mee werken.

| Platform | Sterk punt | Wat het studenten niet geeft |
|---|---|---|
| Legal Intelligence | Uitgebreide zoekindex, gratis via instelling | Geen samenvattingen, geen persoonlijke opslag, geen leerworkflow |
| Rechtsorde / GenIA-L | AI-zoekassistent | Betaald, gericht op advocatuur |
| Rechtspraak.nl | Gratis volledige teksten | Ruwe XML, geen begeleiding, geen structuur |
| Feitlijn (Patroon) | Overzicht per feitencomplex | Geen persoonlijke kennisbank, geen casus-tools |

**De gap:** geen enkel platform helpt studenten bij de *studenten-workflow*: uploaden → begrijpen → opslaan → toepassen.

---

## Gebruikersreis

### Van probleem naar oplossing

```
1. ONTDEKKING
   Lotte hoort van de app via een medestudent of studiegroep
   → Ze opent de app, geen account vereist, direct aan de slag

2. EERSTE GEBRUIK (< 2 minuten)
   Ze voert een ECLI-nummer in of upload een PDF
   → De app haalt de uitspraak op en toont een Case Brief
   → Eerste "yes!"-moment: de rechtsvraag in één zin

3. OPSLAAN & TAGGEN
   Ze voegt tags toe ("6:162 BW", "kelderluik", "tentamen week 4")
   → De uitspraak staat nu in haar persoonlijke kennisbank

4. TERUGVINDEN
   De volgende dag zoekt ze op "kelderluik"
   → Ze ziet alle relevante arresten die ze eerder heeft opgeslagen

5. CASUS UITWERKEN
   Ze werkt een OOD-casus uit via het stappenplan
   → Ze vult criteria in, de app structureert haar analyse

6. TERUGKEREN
   Ze raakt de app gewoon — elke keer dat ze een nieuw arrest leest
```

### Kern-gebruiksloop

**Trigger →** Nieuw arrest te lezen voor college/tentamen  
**Actie →** ECLI invoeren of PDF uploaden  
**Beloning →** Directe, begrijpelijke Case Brief  
**Investering →** Opgeslagen in kennisbank met eigen tags  

---

## MVP Features

### Must Have — P0 (Lancering geblokkeerd zonder deze)

#### Feature 1: ECLI → Automatische Case Brief

**Wat het doet:** De student voert een ECLI-nummer in (bijv. `ECLI:NL:HR:2002:AE7040`). De app haalt de volledige uitspraaktekst op via de gratis Rechtspraak.nl Open Data API, stuurt de tekst naar Groq/Llama 3.3, en toont een gestructureerde Case Brief in het Nederlands.

**User Story:** *Als rechtenstudent wil ik een ECLI-nummer kunnen invoeren zodat ik binnen één minuut de kern van de uitspraak begrijp zonder de hele tekst te hoeven lezen.*

**Acceptatiecriteria:**
- [ ] Student kan een geldig ECLI invoeren en op "Analyseer" klikken
- [ ] App haalt de uitspraaktekst op van Rechtspraak.nl (of toont een foutmelding bij ongeldig ECLI)
- [ ] AI genereert een Case Brief met: feiten, partijen, rechtsvraag, overwegingen, dictum, belang, wetsartikelen
- [ ] Output is in het Nederlands
- [ ] Verwerking duurt maximaal 30 seconden
- [ ] Bij API-fout of timeout krijgt de student een begrijpelijke foutmelding

**Prioriteit:** P0 — Kritisch

---

#### Feature 2: Persoonlijke Kennisbank met Zoeken + Tags

**Wat het doet:** De student kan een gegenereerde Case Brief opslaan in een persoonlijke database, eigen tags toevoegen (bijv. "6:162 BW", "tentamen week 3", "kelderluik"), en later terugzoeken op vrije tekst of tag.

**User Story:** *Als rechtenstudent wil ik mijn uitspraken kunnen opslaan met eigen tags zodat ik ze later snel kan terugvinden op onderwerp of college.*

**Acceptatiecriteria:**
- [ ] Student kan een Case Brief opslaan met één klik na generatie
- [ ] Student kan bij het opslaan één of meerdere tags toevoegen (kommagescheiden invoer)
- [ ] Kennisbank toont alle opgeslagen uitspraken, meest recent bovenaan
- [ ] Zoekbalk zoekt over alle tekstvelden (feiten, rechtsvraag, overwegingen)
- [ ] Tag-filter toont alle uitspraken met een specifieke tag
- [ ] Klikken op een opgeslagen uitspraak toont de volledige Case Brief
- [ ] Studenten kunnen notities toevoegen aan opgeslagen uitspraken

**Prioriteit:** P0 — Kritisch

---

#### Feature 3: Interactief Stappenplan — Onrechtmatige Daad (6:162 BW)

**Wat het doet:** De student kan een casus uitwerken via een geleid stappenplan voor onrechtmatige daad. Per stap (onrechtmatigheid → toerekenbaarheid → schade → causaliteit → relativiteit) worden de relevante criteria uitgevraagd met uitlegknoppen. Aan het einde krijgt de student een gestructureerde analyse.

**User Story:** *Als rechtenstudent wil ik een casus systematisch kunnen uitwerken via een stappenplan zodat ik geen juridische stap oversla en tentamenklaar ben.*

**Acceptatiecriteria:**
- [ ] Stappenplan volgt de OOD-structuur: onrechtmatigheid (type) → Kelderluik-criteria → toerekenbaarheid → schade → CSQn-verband → relativiteit
- [ ] Elke stap heeft een "Wat betekent dit?"-uitlegknop met beknopte uitleg
- [ ] Student kan per stap invullen en doorgaan naar de volgende stap
- [ ] Aan het einde wordt een samenvatting van de analyse getoond
- [ ] De analyse kan worden opgeslagen in de kennisbank

**Prioriteit:** P0 — Kritisch

---

### Nice to Have — P1 (Als er tijd over is)

- **PDF uploaden → Case Brief:** Student upload een PDF-arrest direct (i.p.v. via ECLI). Minder urgent omdat de meeste arresten via ECLI bereikbaar zijn, maar waardevol voor gescande stukken of buitenlandse uitspraken.
- **Tekst plakken → Case Brief:** Student plakt ruwe tekst. Vangnet voor gevallen waarin noch ECLI noch PDF werkt.
- **Wetsartikel-filter:** Kennisbank filteren op wetsartikel (bijv. alle uitspraken met "6:162 BW"). Vereist minimale extra code.

---

### Niet in MVP — Voor Versie 2

| Feature | Reden om te wachten | Wanneer toevoegen |
|---|---|---|
| Notificaties / herinneringen | Vereist achtergrondprocessen en auth; te complex voor v1 | Na gebruikersvalidatie |
| Gebruikersaccounts / inloggen | Verhoogt drempel enorm; Streamlit heeft geen native auth | Als meerdere gebruikers data willen scheiden |
| Samenwerken / gedeelde kennisbank | Vereist multi-user auth en permissies | Na bewijs van solo-waarde |
| Export naar Word/PDF | Mooi-to-have, geen kernbehoefte voor leren | Na eerste gebruikersfeedback |
| Meer stappenplannen (wanprestatie, bestuursrecht) | OOD eerst valideren; daarna uitbreiden | Na positieve reactie op OOD-stappenplan |

*Rationale: Elke feature die wordt weggelaten, is een feature die de lancering niet blokkeert. Een werkende app met drie sterke features is waardevoller dan een half-werkende app met tien.*

---

## Hoe We Weten Dat Het Werkt

### Lanceringsmetrics (Eerste 30 Dagen)

| Metric | Doel | Hoe Meten |
|---|---|---|
| Actieve gebruikers | 10–30 studenten gebruiken de app | Supabase rij-tellingen; Streamlit Community Cloud analytics |
| Gegenereerde Case Briefs | ≥ 50 in de eerste maand | Tellen van database-rijen |
| Opgeslagen uitspraken | ≥ 30 opgeslagen in kennisbank | Database-tellingen |
| Terugkerende gebruikers | ≥ 5 studenten gebruiken de app >2× | Timestamps in database |
| Kwalitatief | Positieve reactie van 3+ medestudenten | Directe gesprekken / WhatsApp |

### Groeiindicatoren (Maand 2–3)

| Metric | Doel |
|---|---|
| Mond-tot-mond verspreiding | Nieuwe gebruikers zonder actieve promotie |
| Feature-requests | Studenten vragen om specifieke verbeteringen (signaal van waarde) |
| Stappenplan-gebruik | ≥ 20 ingevulde OOD-analyses |

---

## Look & Feel

**Design Vibe:** Compact, snel, studentvriendelijk

**Ontwerpprincipes:**
1. **Geen onnodige knoppen** — Elke actie heeft één knop, geen verborgen menu's
2. **Resultaat eerst** — De Case Brief staat direct bovenaan, uitleg pas daarna
3. **Bekende patronen** — Gebruik wat studenten al kennen (tabs, tags, zoekbalk)
4. **Groen = opgeslagen, oranje = let op, rood = fout** — Consequente kleurcodering

**Hoofdschermen:**

| Scherm | Doel | Kernactie |
|---|---|---|
| Tab 1: Nieuwe Uitspraak | ECLI invoeren, Case Brief genereren, opslaan | "Analyseer"-knop |
| Tab 2: Kennisbank | Zoeken, filteren op tag, uitspraken bekijken | Zoekbalk + tagfilter |
| Tab 3: Casus Uitwerken | Stap-voor-stap OOD-analyse invullen | Formuliervelden per stap |

**Vereenvoudigd Schermschets — Tab 1:**

```
┌─────────────────────────────────────────┐
│  ⚖️  Juridische Werkbank                │
├─────────────────────────────────────────┤
│  [📄 Nieuwe Uitspraak] [🔍 Kennisbank]  │
│  [📚 Casus Uitwerken]                   │
├─────────────────────────────────────────┤
│                                         │
│  Voer ECLI in:                          │
│  [ECLI:NL:HR:2002:AE7040          ]    │
│                              [Ophalen]  │
│                                         │
│  ✅ Opgehaald: Kelderluik-arrest        │
│  ─────────────────────────────────────  │
│  FEITEN        RECHTSVRAAG              │
│  [.........]   [................]       │
│                                         │
│  OVERWEGINGEN                           │
│  [....................................]  │
│                                         │
│  DICTUM        BELANG                   │
│  [.........]   [................]       │
│                                         │
│  Tags: [6:162 BW, kelderluik    ]      │
│                  [💾 Opslaan]           │
└─────────────────────────────────────────┘
```

---

## Technische Randvoorwaarden

*(Gebaseerd op het onderzoeksrapport — volledig uitgewerkt in het Technical Design Document)*

| Categorie | Vereiste |
|---|---|
| **Platform** | Web-app; werkt in Chrome, Safari, Firefox (laatste versie) |
| **Responsive** | Ja — werkt op laptop én telefoon |
| **Laadtijd** | Pagina laadt in < 3 seconden; AI-respons in < 30 seconden |
| **Beschikbaarheid** | Streamlit Community Cloud uptime (~99%; pauzes na inactiviteit acceptabel voor MVP) |
| **Privacy** | Geen persoonsgegevens opgeslagen; uitspraken zijn openbaar; geen login vereist |
| **Schaalbaarheid** | MVP: 10–30 gelijktijdige gebruikers (Streamlit free tier) |
| **Foutafhandeling** | Elke API-fout geeft een begrijpelijke melding in het Nederlands |
| **Toegankelijkheid** | Basis: leesbaar kleurcontrast, werkende tabvolgorde |

---

## Budget & Beperkingen

| Component | Tool | Gratis Limiet | Kosten |
|---|---|---|---|
| Frontend + Hosting | Streamlit Community Cloud | 3 apps, 1 GB RAM | €0 |
| Database | Supabase (PostgreSQL) | 500 MB, 2 projecten | €0 |
| AI-API | Groq (Llama 3.3 70B) | ~100 req/dag free tier | €0 |
| Uitspraken ophalen | Rechtspraak.nl Open Data API | Ongelimiteerd (max 10/sec) | €0 |
| Versiebeheer | GitHub (publiek) | Onbeperkt | €0 |
| **Totaal** | | | **€0/maand** |

**Wanneer betalen?** Bij >50 actieve studenten/dag of >1.000 opgeslagen uitspraken. Zie Zero-Budget Plan in het onderzoeksrapport voor details.

---

## Risico's

| Risico | Kans | Impact | Maatregel |
|---|---|---|---|
| Groq rate limit bij groepsgebruik | Middel | Middel | Wachtrij inbouwen; fallback naar Gemini Flash |
| Supabase pauzeert bij inactiviteit | Laag | Laag | Ping-script via cron-job.org |
| Rechtspraak.nl API geeft malformed XML | Laag | Middel | Robuuste foutafhandeling in parser |
| AI hallucineert wetsartikelen | Middel | Middel | Prompt instrueert model om alleen geciteerde artikelen te noemen |
| Streamlit geheugenprobleem bij grote PDFs | Laag | Laag | Tekst afkappen op 15.000 tekens voor AI-verwerking |

---

## Openstaande Vragen & Aannames

**Aannames:**
- Studenten vertrouwen de AI-samenvatting genoeg om er op te vertrouwen bij tentamenvoorbereiding (te valideren met eerste gebruikers)
- Geen login vereist voor MVP — alle data is gedeeld op één Supabase-instantie (aanpassen zodra privacy een probleem wordt)
- De meeste benodigde uitspraken zijn beschikbaar via Rechtspraak.nl Open Data

**Openstaande vragen:**
- Willen studenten de samenvatting kunnen bewerken/corrigeren na generatie?
- Is één stappenplan (OOD) genoeg voor de eerste lancering, of is een tweede (wanprestatie) nodig voor genoeg waarde?
- Hoe gaan studenten de app delen? (directe link, QR-code voor tijdens college?)

---

## Definition of Done voor MVP

De MVP is klaar om te lanceren wanneer:

- [ ] Alle P0-features zijn functioneel end-to-end
- [ ] ECLI-invoer werkt met minimaal 10 echte uitspraken getest
- [ ] Opslaan en terugzoeken in kennisbank werkt
- [ ] OOD-stappenplan werkt van stap 1 tot samenvatting
- [ ] Foutmeldingen zijn in het Nederlands en begrijpelijk
- [ ] App werkt op mobiel (telefoon) én desktop
- [ ] Gedeployed op Streamlit Community Cloud
- [ ] Getest door minimaal 2 medestudenten
- [ ] Geen kritieke bugs bij normale gebruikerstaken

---

## Volgende Stappen

1. **Nu:** Review deze PRD — klopt alles?
2. **Daarna:** Technical Design Document (Part 3) — hoe het gebouwd wordt
3. **Dan:** Ontwikkelomgeving opzetten (zie onderzoeksrapport §9 voor dag-tot-dag plan)
4. **Bouwen:** MVP implementeren met AI-assistentie
5. **Testen:** 5–10 medestudenten uitnodigen voor beta
6. **Lanceren:** Live zetten en delen

---

*PRD Versie: 1.0*  
*Status: Draft — Klaar voor Technical Design*  
*Gebaseerd op: Juridische Werkbank MVP Onderzoeksrapport (Deel 1)*
