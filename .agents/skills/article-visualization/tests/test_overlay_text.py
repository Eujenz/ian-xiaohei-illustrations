from pathlib import Path

from PIL import Image

from conftest import load_script


overlay_text = load_script("overlay_text")


def test_overlay_text_creates_output_png(tmp_path):
    image_path = tmp_path / "textless.png"
    output_path = tmp_path / "final.png"
    Image.new("RGB", (400, 240), "white").save(image_path)
    overlay_json = {
        "shot_id": "x",
        "canvas": {"width": 400, "height": 240},
        "labels": [{"id": "a", "text": "測試", "x": 10, "y": 10, "box_width": 120, "box_height": 50, "font_size": 20}]
    }
    font = overlay_text.find_system_cjk_font() or "C:/Windows/Fonts/arial.ttf"
    overlay_text.overlay(str(image_path), overlay_json, str(output_path), font)
    assert output_path.exists()


def test_overlay_text_does_not_alter_coordinates_or_infer_positions(tmp_path):
    image_path = tmp_path / "textless.png"
    output_path = tmp_path / "final.png"
    Image.new("RGB", (400, 240), "white").save(image_path)
    label = {"id": "a", "text": "測試", "x": 10, "y": 10, "box_width": 120, "box_height": 50, "font_size": 20}
    overlay_json = {"shot_id": "x", "canvas": {"width": 400, "height": 240}, "labels": [label.copy()]}
    font = overlay_text.find_system_cjk_font() or "C:/Windows/Fonts/arial.ttf"
    overlay_text.overlay(str(image_path), overlay_json, str(output_path), font)
    assert overlay_json["labels"][0] == label
