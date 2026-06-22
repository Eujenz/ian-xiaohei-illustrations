import copy
import json
from pathlib import Path

from conftest import load_script


ROOT = Path(__file__).resolve().parents[1]
qa_text = load_script("qa_text")


def valid_overlay():
    return json.loads((ROOT / "examples" / "overlays" / "01.overlay.json").read_text(encoding="utf-8"))


def test_qa_text_passes_valid_overlay_json():
    assert qa_text.qa_overlay(valid_overlay()).passed


def test_qa_text_fails_empty_text():
    data = valid_overlay()
    data["labels"][0]["text"] = ""
    report = qa_text.qa_overlay(data)
    assert not report.passed
    assert not report.checks["all_text_non_empty"]


def test_qa_text_fails_out_of_bounds_labels():
    data = valid_overlay()
    data["labels"][0]["x"] = 2000
    report = qa_text.qa_overlay(data)
    assert not report.passed
    assert not report.checks["text_in_bounds"]
