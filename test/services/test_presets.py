import toml

import presets


def _write_config(path, app=None):
    path.write_text(
        toml.dumps({"app": app or {"video_source": "pexels"}, "ui": {"hide_log": False}}),
        encoding="utf-8",
    )


def test_folktale_preset_switches_to_ai_images_and_saves_key(tmp_path, monkeypatch):
    config_path = tmp_path / "config.toml"
    _write_config(config_path)
    monkeypatch.setattr(presets, "CONFIG_PATH", str(config_path))
    monkeypatch.setattr(presets.getpass, "getpass", lambda _prompt: " sk-test ")

    assert presets.main(["folktale"]) == 0

    config = toml.loads(config_path.read_text(encoding="utf-8"))
    assert config["app"]["video_source"] == "openai_image"
    assert config["app"]["openai_image_base_url"] == "https://api.openai.com/v1"
    assert "{term}" in config["app"]["openai_image_prompt_template"]
    assert config["app"]["openai_image_api_keys"] == ["sk-test"]
    assert config["app"]["match_materials_to_script"] is True
    assert config["ui"]["paragraph_number"] == 4
    assert config["ui"]["video_aspect_openai_image"] == "9:16"
    assert config["ui"]["hide_log"] is False


def test_folktale_preset_keeps_existing_key_without_asking(tmp_path, monkeypatch):
    config_path = tmp_path / "config.toml"
    _write_config(config_path, {"openai_image_api_keys": ["sk-old"]})
    monkeypatch.setattr(presets, "CONFIG_PATH", str(config_path))

    def fail(_prompt):
        raise AssertionError("should not ask for a key")

    monkeypatch.setattr(presets.getpass, "getpass", fail)

    assert presets.main(["folktale"]) == 0
    config = toml.loads(config_path.read_text(encoding="utf-8"))
    assert config["app"]["openai_image_api_keys"] == ["sk-old"]


def test_unknown_preset_or_missing_config_fails(tmp_path, monkeypatch):
    monkeypatch.setattr(presets, "CONFIG_PATH", str(tmp_path / "missing.toml"))
    assert presets.main(["nope"]) == 2
    assert presets.main(["folktale"]) == 2
