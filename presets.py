"""찐숏폼 설정 프리셋: config.toml에 장르별 설정을 한 번에 적용합니다.

사용법 (웹 화면을 끈 상태에서 실행하세요. 켜져 있으면 웹 화면이 이전 값으로 덮어씁니다)
    uv run python presets.py folktale

folktale: 민담·야담. 영상 소스를 AI 그림(openai_image)으로 바꾸고,
          조선 민담 화풍 프롬프트와 이야기꾼 대본 요청을 넣습니다.
          OpenAI API 키가 아직 없으면 물어봅니다.
"""

from __future__ import annotations

import getpass
import os
import sys
from typing import Sequence

import toml

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(ROOT_DIR, "config.toml")

PRESETS = {
    "folktale": {
        "description": "민담·야담 (AI 그림 + 이야기꾼 대본)",
        "app": {
            "video_source": "openai_image",
            "openai_image_base_url": "https://api.openai.com/v1",
            "openai_image_model": "gpt-image-1",
            # 비워 두면 세로 영상에 맞는 1024x1536을 자동으로 고릅니다.
            "openai_image_size": "",
            "openai_image_prompt_template": (
                "Korean Joseon dynasty folk tale illustration, {term}, "
                "traditional Korean ink painting style, muted colors, moody moonlight, "
                "cinematic composition, vertical frame, no text, no letters"
            ),
            "match_materials_to_script": True,
        },
        "ui": {
            "video_language": "ko-KR",
            "paragraph_number": 4,
            "video_script_prompt": (
                "옛이야기를 들려주는 이야기꾼 말투. 첫 문장은 궁금증을 자극하는 질문으로 시작. "
                "짧은 문장 위주로 긴장감 있게 전개하고 마지막 한 문장에서 반전. 50~60초 분량."
            ),
            "video_concat_mode": "sequential",
            "video_clip_duration": 5,
            "video_aspect_openai_image": "9:16",
        },
        "needs_key": "openai_image_api_keys",
    },
}


def apply_preset(config: dict, preset: dict) -> list[str]:
    """Merge a preset into config in place and return the changed keys."""
    changed = []
    for section in ("app", "ui"):
        target = config.setdefault(section, {})
        for key, value in preset.get(section, {}).items():
            if target.get(key) != value:
                target[key] = value
                changed.append(f"{section}.{key}")
    return changed


def has_key(config: dict, key_name: str) -> bool:
    keys = config.get("app", {}).get(key_name) or []
    return any(str(key).strip() for key in keys)


def main(argv: Sequence[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) != 1 or argv[0] not in PRESETS:
        print("사용법: uv run python presets.py <프리셋>")
        for name, preset in PRESETS.items():
            print(f"  {name}: {preset['description']}")
        return 2

    if not os.path.isfile(CONFIG_PATH):
        print(f"config.toml이 없습니다. 웹 화면을 한 번 실행한 뒤 다시 시도하세요: {CONFIG_PATH}")
        return 2

    preset = PRESETS[argv[0]]
    with open(CONFIG_PATH, encoding="utf-8-sig") as file:
        config = toml.load(file)

    changed = apply_preset(config, preset)

    key_name = preset.get("needs_key")
    if key_name and not has_key(config, key_name):
        api_key = getpass.getpass("OpenAI API 키를 붙여넣고 엔터 (화면에 보이지 않습니다): ").strip()
        if api_key:
            config["app"][key_name] = [api_key]
            changed.append(f"app.{key_name}")
        else:
            print("키 없이 저장합니다. 나중에 설정 → 소재 소스 설정에서 넣으세요.")

    with open(CONFIG_PATH, "w", encoding="utf-8") as file:
        toml.dump(config, file)

    print(f"'{preset['description']}' 설정을 적용했습니다. 바뀐 항목 {len(changed)}개:")
    for key in changed:
        print(f"  - {key}" if "api_keys" not in key else f"  - {key} (저장됨)")
    print("이제 웹 화면을 다시 켜세요: sh webui.sh")
    return 0


if __name__ == "__main__":
    sys.exit(main())
