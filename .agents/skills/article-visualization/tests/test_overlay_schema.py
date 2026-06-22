import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]


def test_overlay_schema_accepts_coordinate_json():
    schema = json.loads((ROOT / "schemas" / "overlay.schema.json").read_text(encoding="utf-8"))
    data = json.loads((ROOT / "examples" / "overlays" / "01.overlay.json").read_text(encoding="utf-8"))
    assert list(Draft202012Validator(schema).iter_errors(data)) == []


def test_overlay_schema_rejects_missing_coordinates():
    schema = json.loads((ROOT / "schemas" / "overlay.schema.json").read_text(encoding="utf-8"))
    data = json.loads((ROOT / "examples" / "overlays" / "01.overlay.json").read_text(encoding="utf-8"))
    del data["labels"][0]["x"]
    assert list(Draft202012Validator(schema).iter_errors(data))
