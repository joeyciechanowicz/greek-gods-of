# Plan: Sourcing Comprehensive Lists of What Each God Was For

## Goal

Build a sourced, checkable dataset of **every recorded thing each Greek god was for**, down to the
small ones (flies, mice, flour mills). Every claim must point to where it comes from.

The small functions mostly survive as **epithets** (cult titles), for example *Zeus Apomyios*
("averter of flies") or *Apollo Smintheus* ("of mice"). The scale is large: over a thousand epithets
survive for Zeus alone. So the job is mostly to **harvest epithets, classify them, and verify them**.

## What one record looks like

Store the data as rows in `data/` (CSV or YAML), one row per god + epithet + function:

| Field | Example |
| --- | --- |
| `god` | Zeus (with Wikidata ID, e.g. `Q34201`) |
| `epithet` | Apomyios (Greek: Ἀπόμυιος) |
| `function` | Averting flies from sacrifices |
| `category` | `functional` / `toponymic` (a place name) / `descriptive` (appearance, parentage) |
| `place` | Olympia |
| `ancient_source` | Pausanias 5.14.1 |
| `modern_source` | Theoi.com Zeus titles; MAP database entry ID |
| `evidence` | `literary` / `inscription` / `lexicon` |
| `confidence` | `primary` (ancient text checked) / `secondary` (scholarly reference only) / `unverified` |

Most epithets are **toponymic**: they name a shrine's location ("Zeus of Mount Lykaion") and tell you
nothing about function. We keep those rows but tag them, so the "what they were for" pages can filter
to `functional`.

## Sources, in priority order

### Tier 1: Structured, machine-readable data

| Source | What it gives | Access / licence |
| --- | --- | --- |
| [Mapping Ancient Polytheisms (MAP)](https://base-map-polytheisms.huma-num.fr/) | 22,000+ divine names and epithets from 18,000 **inscriptions**, 1000 BCE–400 CE, with places and dates. The best source of real cult epithets | Open access; SQL-backed web database. Check for an export or API; otherwise contact the team ([project site](https://map-polytheisms.huma-num.fr/?lang=en), [tutorials](https://map-polytheisms.huma-num.fr/ressources/map-database-tutorials/?lang=en)) |
| [Wikidata](https://www.wikidata.org/wiki/Property:P2925) | Canonical IDs for each god; property **P2925 "domain of saint or deity"** gives some domains | CC0; SPARQL endpoint. Good for the god list and IDs, but domain data is sparse |
| [ToposText](https://topostext.org/) | Index of 22,000 names (gods and festivals included) linked to 430,000 ancient passages and to Wikidata | Web; check terms for bulk use |
| MANTO ([dataset note](https://www.manto-myth.org/blog/a-dataset-of-mythical-names-with-stable-uris)) | 3,618 mythical people with stable URIs, drawn from Homer, Hesiod, Apollodorus and Pausanias | Check licence and download |

### Tier 2: Reference compilations (epithet lists with citations)

| Source | Notes |
| --- | --- |
| Theoi.com cult titles pages (e.g. [Zeus titles](https://www.theoi.com/Cult/ZeusTitles.html)) | The most usable English lists, each epithet with an ancient citation. **Copyrighted**: use as an index and cite it, but write our own descriptions |
| Wikipedia "Epithets of …" pages (e.g. [Epithets of Zeus](https://en.wikipedia.org/wiki/Epithets_of_Zeus)) | Good coverage; CC BY-SA, so copying text requires attribution and a share-alike licence |
| Bruchmann, *Epitheta deorum quae apud poetas Graecos leguntur* (1893) ([HathiTrust](https://catalog.hathitrust.org/Record/008897727)) | Public domain. Latin; every epithet of every god **in Greek poetry**, alphabetical by god. Needs OCR and translation |
| Roscher, *Ausführliches Lexikon der griechischen und römischen Mythologie* ([archive.org](https://archive.org/details/ausfhrlicheslexi134rosc)) | Public domain, German. Very detailed articles per god and epithet |
| Farnell, *The Cults of the Greek States* (5 vols, 1896–1909) | Public domain, English. Organised by god and by function; strong on local cults |
| Smith, *Dictionary of Greek and Roman Biography and Mythology* (1849) | Public domain, English; on Perseus |
| Pauly–Wissowa, *Realencyclopädie* | German; much of it is transcribed on German Wikisource |

### Tier 3: Primary texts, for verification

[PerseusDL canonical-greekLit](https://github.com/PerseusDL/canonical-greekLit) (TEI XML, CC BY-SA 4.0)
has most of the authors we need in Greek and often in English: **Pausanias** (the richest source of
local cults), Athenaeus, Aelian, Homeric Hymns, Hesiod, Orphic Hymns, Pindar and Aristophanes.
Hesychius's lexicon and inscription collections (e.g. PHI Greek Inscriptions, the Collection of Greek
Ritual Norms) cover the rest.

### Treat as leads only

Modern Hellenic-revival sites (e.g. hellenicgods.org), pop-mythology sites and AI answers. They mix
ancient evidence with modern practice. A claim from these needs a Tier 1–3 source before it counts
(the "Athena, goddess of heirlooms" claim is an example).

## Pipeline

1. **Unblock network access.** This cloud environment currently blocks most of the sites above
   (theoi.com, wikipedia.org, wikidata.org, topostext.org, perseus.tufts.edu, the MAP database, archive.org,
   HathiTrust). Add them to the environment's allowed domains before starting. GitHub is reachable, so
   Perseus's GitHub repos work already.
2. **God list.** Pull Greek deities, including minor gods and personifications, from Wikidata by
   SPARQL, and keep their IDs as the key for everything else.
3. **Harvest epithets** per god from Wikipedia's "Epithets of …" pages, Theoi's titles pages and MAP.
   Merge variant spellings (Apomyios / Apomuios / Ἀπόμυιος) by the Greek form.
4. **Classify** each epithet as functional, toponymic or descriptive, and write a short function
   description for the functional ones. The Greek meaning (e.g. *-myios*, "fly") usually settles it.
5. **Verify.** For each functional epithet, look up the cited passage in Perseus and set
   `confidence`. Anything without a checkable ancient source stays `unverified` and is kept off the
   public pages.
6. **Fill gaps** from Bruchmann (poetic epithets) and Farnell (cult functions), mainly for the minor
   gods that Wikipedia and Theoi cover thinly.
7. **Generate pages.** A small script builds `README.md`, `LITTLE-THINGS.md` and one page per god from
   `data/`, so the Markdown is never edited by hand.
8. **Check in CI.** Fail the build if a row marked `primary` or `secondary` lacks a source, or if IDs
   are duplicated.

## Pilot first

Start with **Athena**. She has a well-documented, mid-sized set of epithets (roughly 100–150), with a
mix of functional ones (Ergane, Hippia, Ophthalmitis, Salpinx) and toponymic ones. The pilot tests
the data format, measures how long verification takes per epithet, and tells us how many of the
epithets are functional.

Then do the rest of the twelve Olympians, then Hades, Hestia, Hecate and Persephone, then the minor
gods and personifications.

## Risks

- **Copyright.** Theoi.com text is copyrighted, and Wikipedia text is CC BY-SA. Copy facts and
  citations, not prose; or license the repo CC BY-SA.
- **Language and OCR.** The best older compilations are in Latin and German, from scanned pages.
- **Scale.** Several thousand epithets in total, most of them toponymic. Filtering early keeps the
  verification work to the functional ones.
- **Made-up claims.** Automated or AI-assisted extraction can invent functions. The rule that every
  row needs a checked source is the safeguard.

## Decisions needed

1. **Scope.** Include heroes and local *daimones* (Kyamites, Matton, Keraon), or only gods?
2. **Licence** for the repo (affects how much Wikipedia text can be reused).
3. **Output.** Markdown pages in the repo only, or also a searchable web page generated from the data?
