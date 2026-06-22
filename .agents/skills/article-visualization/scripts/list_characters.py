from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from validate_character_profile import load_character, validate_character_profile
except ImportError:
    from .validate_character_profile import load_character, validate_character_profile


def list_characters(characters_dir: str) -> list[dict]:
    rows: list[dict] = []
    for character_path in sorted(Path(characters_dir).glob("*/character.json")):
        character = load_character(character_path)
        report = validate_character_profile(character)
        rows.append({
            "character_id": character.get("character_id", character_path.parent.name),
            "display_name": character.get("display_name", ""),
            "valid": report["passed"],
            "errors_count": len(report["errors"]),
            "actions_count": len(character.get("action_library", [])),
            "deformation_rules_count": len(character.get("deformation_rules", [])),
        })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--characters-dir", required=True)
    args = parser.parse_args()
    rows = list_characters(args.characters_dir)
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    return 0 if all(row["valid"] for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
