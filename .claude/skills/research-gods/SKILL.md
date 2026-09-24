---
name: research-gods
description: Orchestrates the Greek gods research pipeline. Spawns a god-researcher subagent per god, then an epithet-verifier subagent per god, validates the output and rebuilds the pages. Use when asked to research, verify or refresh the gods data.
argument-hint: "[all | <batch> | <slug> ...] [--research-only | --verify-only] [--force] [--parallel N] [--commit]"
---

# Research Gods

You are the orchestrator. You do **not** research gods yourself: you pick targets, spawn subagents,
check their output and keep a log. Subagents can't spawn subagents, so all fan-out happens here.

Arguments: `$ARGUMENTS`

## 1. Pick targets

Read `pipeline/gods.json`. It has `batches` (in order) and `gods` (each with `god`, `slug`, `batch`).

Parse the arguments:

- Targets: `all`, one or more batch names (e.g. `olympians`), or one or more slugs (e.g. `athena`).
  No target means the first batch that still has work to do.
- `--research-only`: skip verification. `--verify-only`: skip research.
- `--force`: re-research gods that already have a file (the researcher extends the existing file).
- `--parallel N`: how many subagents to run at once. Default 5.
- `--commit`: after each batch, commit `data/`, `gods/` and `pipeline/RUN-LOG.md`.

For each target god, the work needed is:

- **research** if `data/gods/<slug>.json` doesn't exist (or `--force`).
- **verify** if the file exists and `verified_at` is null (or it was just researched).

Tell the user the plan in a few lines: how many gods, which batches, research and verify counts.

## 2. Research phase

Spawn `god-researcher` subagents with the Agent tool (named Task in older Claude Code versions),
**N at a time in a single message** so they run in parallel. Wait for each wave before starting the
next. Prompt for each:

> Research the Greek god **<god>** (slug: `<slug>`, batch: `<batch>`). Write `data/gods/<slug>.json`
> following `pipeline/SCHEMA.md`, then run `python3 scripts/validate.py <slug>` and fix any errors.

After each subagent returns, run `python3 scripts/validate.py <slug>` yourself. If it fails, spawn a
fresh `god-researcher` with the validator output and the instruction to fix the existing file. After
two failed attempts, mark the god as failed in the log and move on.

## 3. Verify phase

Same pattern with `epithet-verifier` subagents, N at a time:

> Verify the citations in `data/gods/<slug>.json` for **<god>** following your instructions, then run
> `python3 scripts/validate.py <slug>` and fix any errors.

Validate after each one returns, with the same two-attempt retry rule.

## 4. Build and log

1. Run `python3 scripts/validate.py` on everything and `python3 scripts/build_pages.py`.
2. Append a section to `pipeline/RUN-LOG.md` (create it if needed): date, targets, and one line per god
   with its counts (functional / descriptive / toponymic / rejected; primary / secondary / unverified),
   any failures and any sources the subagents couldn't reach.
3. With `--commit`, commit after each batch:
   `git add data gods pipeline/RUN-LOG.md && git commit -m "Research <batch>: <n> gods"`.
   Never push; the user reviews and pushes.

## 5. Report

End with a short summary: gods completed, gods failed and why, total sourced functions, and the
handful of most surprising small functions found in this run.

## Ground rules

- Never write god data yourself; if something needs fixing, send it back to a subagent.
- Never mark anything `primary` yourself.
- If a whole source is unreachable (e.g. every subagent reports theoi.com blocked), stop after the
  current wave and tell the user; don't burn the remaining batches on degraded research.
