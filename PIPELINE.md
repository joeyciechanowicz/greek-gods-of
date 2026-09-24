# Research Pipeline

An agent-led pipeline that researches what each Greek god was for, one subagent per god. It
implements [SOURCING-PLAN.md](SOURCING-PLAN.md) using Claude Code.

## How it works

```
/research-gods  (orchestrator: your Claude Code session)
 │
 ├─ reads pipeline/gods.json ── 166 gods in 11 batches
 │
 ├─ research phase ── god-researcher × N in parallel
 │     each one: Theoi, Wikipedia, MAP, Wikidata, ToposText, web search
 │     writes data/gods/<slug>.json   (confidence: secondary / unverified)
 │
 ├─ verify phase ──── epithet-verifier × N in parallel
 │     each one: looks up every ancient citation on Perseus / ToposText
 │     marks rows primary / secondary / unverified, fixes wrong claims
 │
 ├─ scripts/validate.py after every subagent (retry up to 2× on failure)
 └─ scripts/build_pages.py → gods/<slug>.md + gods/INDEX.md, log in pipeline/RUN-LOG.md
```

| File | Role |
| --- | --- |
| `.claude/skills/research-gods/SKILL.md` | Orchestrator instructions (the `/research-gods` command) |
| `.claude/agents/god-researcher.md` | Subagent that researches one god |
| `.claude/agents/epithet-verifier.md` | Subagent that checks one god's citations |
| `.claude/settings.json` | Pre-approves web access, the scripts, and writes to `data/gods/` and `gods/` |
| `pipeline/gods.json` | The god list, grouped into batches |
| `pipeline/SCHEMA.md`, `pipeline/example-god.json` | Record format |
| `scripts/validate.py` | Schema and sourcing rules (e.g. `primary` needs a checked ancient source) |
| `scripts/build_pages.py` | Renders the Markdown pages from the data |

The pipeline is resumable: gods that already have a file are skipped, and gods whose file has
`verified_at: null` are picked up by the verify phase.

## Running it

Requirements: [Claude Code](https://code.claude.com/docs), Python 3, and unrestricted web access to
theoi.com, wikipedia.org, wikidata.org, topostext.org, perseus.tufts.edu and
base-map-polytheisms.huma-num.fr.

Start with the pilot to check quality and cost:

```sh
claude
> /research-gods athena
```

Then run batch by batch:

```sh
> /research-gods olympians --commit
> /research-gods underworld titans --parallel 8 --commit
```

Or run it headless:

```sh
claude -p "/research-gods olympians --commit" --permission-mode acceptEdits
```

Options:

| Option | Effect |
| --- | --- |
| `all`, `<batch>`, `<slug>` | What to run. With no target, runs the next unfinished batch |
| `--research-only` / `--verify-only` | Run one phase |
| `--force` | Re-research gods that already have data (extends the file) |
| `--parallel N` | Subagents at once (default 5) |
| `--commit` | Commit after each batch (never pushes) |

Batches: `olympians`, `underworld`, `primordials`, `titans`, `sea`, `nature`, `healing`,
`love-and-family`, `arts-and-fortune`, `personifications`, `household-daimones`.
To add a god, add it to `pipeline/gods.json`.

## Cost and tuning

- The large gods (Zeus, Apollo, Athena and so on) have hundreds of titles and are the expensive part.
  The personification batches are cheap.
- The subagents use `model: inherit`, so they run on whatever model your session uses. To cut cost,
  change `model:` in `.claude/agents/god-researcher.md` to `sonnet`, and keep the verifier on a
  stronger model, since judging whether a passage supports a claim is the harder step.
- Lower `--parallel` if you hit rate limits.

## Reviewing the output

- `gods/INDEX.md` shows progress per batch.
- `python3 scripts/build_pages.py --include-unverified` also shows unverified claims, which is useful
  when reviewing what the verifier threw out.
- Spot-check a few `primary` rows per batch against their `verification_note` before trusting a batch.
