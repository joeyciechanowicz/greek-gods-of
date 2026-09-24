# God Record Schema

Each god gets one JSON file at `data/gods/<slug>.json`. See `pipeline/example-god.json` for a filled-in
example. `scripts/validate.py` enforces these rules.

## Top level

| Field | Type | Notes |
| --- | --- | --- |
| `god` | string | Display name, e.g. `"Athena"` |
| `slug` | string | Lowercase, hyphenated; must match the filename |
| `wikidata` | string or null | Wikidata ID, e.g. `"Q37122"` |
| `summary` | string | One sentence: the god's main domains |
| `functions` | array | Functional and descriptive epithets / attributions (below) |
| `toponymic` | array | Epithets that only name a place (below) |
| `rejected` | array | Popular claims that did not hold up (below) |
| `sources_consulted` | array of strings | URLs or references actually read |
| `researched_at` | string | ISO date, `YYYY-MM-DD` |
| `verified_at` | string or null | ISO date, set by the verifier |

## `functions[]`

One entry per distinct thing the god was *for*.

| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | `<slug>-<epithet-slug>` (e.g. `athena-ergane`); unique within the file |
| `epithet` | string or null | Transliterated title, e.g. `"Ergane"`. `null` if the function is attributed without a title (e.g. "invented the bridle") |
| `epithet_greek` | string or null | Greek form, e.g. `"Ἐργάνη"` |
| `function` | string | Short plain-English description of what they were for, written in our own words |
| `category` | enum | `functional` (a job or sphere) or `descriptive` (appearance, parentage, character) |
| `place` | string or null | Where the cult or usage is attested |
| `ancient_sources` | array of strings | Standard citations, e.g. `"Paus. 3.18.2"`, `"Hom. Il. 5.733"`, `"IG II² 4318"` |
| `modern_sources` | array of strings | URLs or references (Theoi page, MAP entry, Farnell vol./page) |
| `evidence` | enum | `literary`, `inscription`, `lexicon` (e.g. Hesychius), or `scholarly` (modern reference only) |
| `confidence` | enum | `primary` (ancient passage checked), `secondary` (reliable modern reference, passage not checked), `unverified` |
| `verification_note` | string or null | Verifier's note: what the passage actually says, or why it was downgraded |

Rules:

- `primary` requires at least one `ancient_sources` entry that the verifier has read.
- `secondary` requires at least one `ancient_sources` or `modern_sources` entry.
- Researchers never set `primary`; only the verifier does.

## `toponymic[]`

Place-name epithets (e.g. *Zeus Lykaios*, "of Mount Lykaion"). Kept lightweight and not verified.

| Field | Type |
| --- | --- |
| `epithet` | string |
| `place` | string or null |
| `sources` | array of strings |

## `rejected[]`

Claims found online that could not be sourced, kept so nobody re-adds them.

| Field | Type | Notes |
| --- | --- | --- |
| `claim` | string | e.g. `"Athena is the goddess of heirlooms"` |
| `seen_at` | array of strings | Where the claim appears |
| `reason` | string | Why it was rejected |
