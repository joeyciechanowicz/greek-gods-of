#!/usr/bin/env python3
"""Render data/gods/*.json into Markdown pages under gods/.

Usage:
    python3 scripts/build_pages.py                       # primary + secondary rows only
    python3 scripts/build_pages.py --include-unverified  # also show unverified rows

Writes gods/<slug>.md for each record and gods/INDEX.md, grouped by the
batches in pipeline/gods.json.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "gods"
OUT = ROOT / "gods"
SEED = ROOT / "pipeline" / "gods.json"

CONFIDENCE_LABEL = {"primary": "✅ checked", "secondary": "📚 reference", "unverified": "❓ unverified"}


def cell(value):
    if value is None or value == []:
        return ""
    if isinstance(value, list):
        value = "; ".join(value)
    return str(value).replace("|", "\\|").replace("\n", " ")


def sources(fn):
    return cell(fn["ancient_sources"] + [f"<{u}>" if u.startswith("http") else u for u in fn["modern_sources"]])


def function_table(rows):
    lines = [
        "| Epithet | What for | Place | Sources | Confidence |",
        "| --- | --- | --- | --- | --- |",
    ]
    for fn in rows:
        name = fn["epithet"] or "—"
        if fn["epithet_greek"]:
            name = f"{name} ({fn['epithet_greek']})"
        lines.append(
            f"| {cell(name)} | {cell(fn['function'])} | {cell(fn['place'])} | {sources(fn)} "
            f"| {CONFIDENCE_LABEL[fn['confidence']]} |"
        )
    return lines


def render(rec, include_unverified):
    shown = [f for f in rec["functions"] if include_unverified or f["confidence"] != "unverified"]
    functional = [f for f in shown if f["category"] == "functional"]
    descriptive = [f for f in shown if f["category"] == "descriptive"]
    hidden = len(rec["functions"]) - len(shown)

    lines = [f"# {rec['god']}", "", rec["summary"], ""]
    meta = [f"Researched {rec['researched_at']}"]
    meta.append(f"verified {rec['verified_at']}" if rec["verified_at"] else "not yet verified")
    if rec["wikidata"]:
        meta.append(f"[Wikidata {rec['wikidata']}](https://www.wikidata.org/wiki/{rec['wikidata']})")
    lines += ["_" + " · ".join(meta) + "_", ""]

    lines += ["## What they were for", ""]
    lines += function_table(functional) if functional else ["_Nothing sourced yet._"]
    lines.append("")
    if descriptive:
        lines += ["## Descriptive titles", ""] + function_table(descriptive) + [""]
    if hidden:
        lines += [f"_{hidden} unverified claim(s) hidden. Run with `--include-unverified` to show them._", ""]
    if rec["toponymic"]:
        places = ", ".join(
            f"{t['epithet']}" + (f" ({t['place']})" if t["place"] else "") for t in rec["toponymic"]
        )
        lines += ["## Place titles", "", f"Titles that name a cult site ({len(rec['toponymic'])}): {places}.", ""]
    if rec["rejected"]:
        lines += ["## Claims that don't hold up", ""]
        lines += [f"- **{cell(r['claim'])}**: {cell(r['reason'])}" for r in rec["rejected"]]
        lines.append("")
    lines += ["## Sources consulted", ""]
    lines += [f"- <{s}>" if s.startswith("http") else f"- {s}" for s in rec["sources_consulted"]]
    lines.append("")
    return "\n".join(lines)


def main(args):
    include_unverified = "--include-unverified" in args
    records = {}
    for path in sorted(DATA.glob("*.json")):
        rec = json.loads(path.read_text(encoding="utf-8"))
        records[rec["slug"]] = rec
    OUT.mkdir(exist_ok=True)
    for slug, rec in records.items():
        (OUT / f"{slug}.md").write_text(render(rec, include_unverified), encoding="utf-8")

    seed = json.loads(SEED.read_text(encoding="utf-8"))
    index = ["# Gods Index", "", "Generated from `data/gods/` by `scripts/build_pages.py`. Do not edit by hand.", ""]
    for batch in seed["batches"]:
        members = [g for g in seed["gods"] if g["batch"] == batch]
        index += [f"## {batch.replace('-', ' ').title()}", ""]
        for g in members:
            rec = records.get(g["slug"])
            if rec:
                n = sum(1 for f in rec["functions"] if f["category"] == "functional" and f["confidence"] != "unverified")
                index.append(f"- [{rec['god']}]({g['slug']}.md): {n} sourced functions")
            else:
                index.append(f"- {g['god']}: _not researched yet_")
        index.append("")
    (OUT / "INDEX.md").write_text("\n".join(index), encoding="utf-8")
    print(f"Wrote {len(records)} god page(s) and gods/INDEX.md")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
