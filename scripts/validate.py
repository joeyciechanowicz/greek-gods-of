#!/usr/bin/env python3
"""Validate god records in data/gods/*.json against pipeline/SCHEMA.md.

Usage:
    python3 scripts/validate.py                  # every record
    python3 scripts/validate.py athena zeus      # selected slugs
    python3 scripts/validate.py path/to/file.json

Exits non-zero if any record has errors.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "gods"

DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
WIKIDATA = re.compile(r"^Q\d+$")

TOP_FIELDS = {
    "god": str, "slug": str, "wikidata": (str, type(None)), "summary": str,
    "functions": list, "toponymic": list, "rejected": list,
    "sources_consulted": list, "researched_at": str, "verified_at": (str, type(None)),
}
FUNCTION_FIELDS = {
    "id": str, "epithet": (str, type(None)), "epithet_greek": (str, type(None)),
    "function": str, "category": str, "place": (str, type(None)),
    "ancient_sources": list, "modern_sources": list, "evidence": str,
    "confidence": str, "verification_note": (str, type(None)),
}
ENUMS = {
    "category": {"functional", "descriptive"},
    "evidence": {"literary", "inscription", "lexicon", "scholarly"},
    "confidence": {"primary", "secondary", "unverified"},
}


def check_fields(obj, fields, where, errors):
    if not isinstance(obj, dict):
        errors.append(f"{where}: expected an object")
        return False
    for name, typ in fields.items():
        if name not in obj:
            errors.append(f"{where}: missing '{name}'")
        elif not isinstance(obj[name], typ):
            errors.append(f"{where}: '{name}' has wrong type")
    for name in obj:
        if name not in fields:
            errors.append(f"{where}: unknown field '{name}'")
    return True


def strings(value):
    return isinstance(value, list) and all(isinstance(v, str) and v.strip() for v in value)


def validate(path):
    errors = []
    try:
        rec = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{path.name}: cannot parse: {exc}"]

    if not check_fields(rec, TOP_FIELDS, path.name, errors):
        return errors

    slug = rec.get("slug")
    if isinstance(slug, str):
        if not SLUG.match(slug):
            errors.append(f"{path.name}: bad slug '{slug}'")
        if path.parent == DATA and path.stem != slug:
            errors.append(f"{path.name}: slug '{slug}' does not match filename")
    if isinstance(rec.get("wikidata"), str) and not WIKIDATA.match(rec["wikidata"]):
        errors.append(f"{path.name}: bad wikidata id '{rec['wikidata']}'")
    for field in ("researched_at", "verified_at"):
        if isinstance(rec.get(field), str) and not DATE.match(rec[field]):
            errors.append(f"{path.name}: '{field}' must be YYYY-MM-DD")
    if not strings(rec.get("sources_consulted")):
        errors.append(f"{path.name}: 'sources_consulted' must be a list of non-empty strings")

    seen = set()
    for i, fn in enumerate(rec.get("functions") or []):
        where = f"{path.name}: functions[{i}]"
        if not check_fields(fn, FUNCTION_FIELDS, where, errors):
            continue
        fid = fn.get("id")
        if isinstance(fid, str):
            where = f"{path.name}: {fid}"
            if fid in seen:
                errors.append(f"{where}: duplicate id")
            seen.add(fid)
            if isinstance(slug, str) and not fid.startswith(slug + "-"):
                errors.append(f"{where}: id must start with '{slug}-'")
        for name, allowed in ENUMS.items():
            if isinstance(fn.get(name), str) and fn[name] not in allowed:
                errors.append(f"{where}: '{name}' must be one of {sorted(allowed)}")
        if isinstance(fn.get("function"), str) and not fn["function"].strip():
            errors.append(f"{where}: empty 'function'")
        for name in ("ancient_sources", "modern_sources"):
            if isinstance(fn.get(name), list) and not strings(fn[name]):
                errors.append(f"{where}: '{name}' must contain non-empty strings")
        ancient, modern = fn.get("ancient_sources") or [], fn.get("modern_sources") or []
        if fn.get("confidence") == "primary":
            if not ancient:
                errors.append(f"{where}: 'primary' needs an ancient source")
            if not fn.get("verification_note"):
                errors.append(f"{where}: 'primary' needs a verification_note")
            if not rec.get("verified_at"):
                errors.append(f"{where}: 'primary' only allowed after verification (verified_at is null)")
        if fn.get("confidence") == "secondary" and not (ancient or modern):
            errors.append(f"{where}: 'secondary' needs at least one source")

    for i, top in enumerate(rec.get("toponymic") or []):
        where = f"{path.name}: toponymic[{i}]"
        if check_fields(top, {"epithet": str, "place": (str, type(None)), "sources": list}, where, errors):
            if isinstance(top.get("sources"), list) and not strings(top["sources"]):
                errors.append(f"{where}: 'sources' must contain non-empty strings")

    for i, rej in enumerate(rec.get("rejected") or []):
        where = f"{path.name}: rejected[{i}]"
        if check_fields(rej, {"claim": str, "seen_at": list, "reason": str}, where, errors):
            if not rej.get("reason", "").strip():
                errors.append(f"{where}: empty 'reason'")

    return errors


def main(args):
    if args:
        paths = [Path(a) if a.endswith(".json") else DATA / f"{a}.json" for a in args]
    else:
        paths = sorted(DATA.glob("*.json"))
    if not paths:
        print("No records to validate.")
        return 0
    failed = 0
    for path in paths:
        if not path.exists():
            print(f"FAIL {path}: file not found")
            failed += 1
            continue
        errors = validate(path)
        if errors:
            failed += 1
            print(f"FAIL {path.name}")
            for err in errors:
                print(f"  - {err}")
        else:
            print(f"ok   {path.name}")
    print(f"\n{len(paths) - failed}/{len(paths)} records valid")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
