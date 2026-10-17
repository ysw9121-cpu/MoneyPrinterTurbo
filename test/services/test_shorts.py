import json

import shorts


def test_parse_keywords_skips_comments_and_splits_prompt():
    lines = [
        "# 주석\n",
        "\n",
        "신차 할부 | 30초 분량\n",
        "  보험료 아끼기  \n",
        " | 주제 없는 줄\n",
    ]

    topics = shorts.parse_keywords(lines)

    assert [(t.line_index, t.subject, t.script_prompt) for t in topics] == [
        (2, "신차 할부", "30초 분량"),
        (3, "보험료 아끼기", ""),
    ]


def test_build_manifest_entries_only_sets_prompt_when_given():
    topics = shorts.parse_keywords(["A | 요청\n", "B\n"])

    assert shorts.build_manifest_entries(topics) == [
        {"video_subject": "A", "video_script_prompt": "요청"},
        {"video_subject": "B"},
    ]


def test_build_cli_command_defaults_to_korean_unless_overridden():
    command = shorts.build_cli_command("m.jsonl", ["--video-count", "2"])
    assert command[-4:] == ["--video-language", "ko-KR", "--video-count", "2"]

    command = shorts.build_cli_command("m.jsonl", ["--video-language=en-US"])
    assert command.count("--video-language") == 0
    assert command[-1] == "--video-language=en-US"


def test_main_removes_succeeded_topics_and_keeps_failed(tmp_path, monkeypatch):
    keywords = tmp_path / "keywords.txt"
    keywords.write_text("# 목록\n성공 주제\n실패 주제 | 요청\n남은 주제\n", encoding="utf-8")
    monkeypatch.setattr(shorts, "ROOT_DIR", str(tmp_path))
    manifests = []

    def fake_run_chunk(manifest_path, cli_args):
        with open(manifest_path, encoding="utf-8") as file:
            manifests.append([json.loads(line) for line in file])
        return {
            "tasks": [
                {"index": 1, "status": "succeeded", "result": {"videos": ["/v/1.mp4"]}},
                {"index": 2, "status": "failed", "error": "boom"},
            ]
        }

    monkeypatch.setattr(shorts, "_run_chunk", fake_run_chunk)

    exit_code = shorts.main(["--keywords", str(keywords), "--limit", "2"])

    assert exit_code == 1
    assert manifests == [
        [
            {"video_subject": "성공 주제"},
            {"video_subject": "실패 주제", "video_script_prompt": "요청"},
        ]
    ]
    assert keywords.read_text(encoding="utf-8") == "# 목록\n실패 주제 | 요청\n남은 주제\n"
    done = (tmp_path / "done.txt").read_text(encoding="utf-8")
    assert "\t성공 주제\t/v/1.mp4\n" in done


def test_main_dry_run_does_not_touch_files(tmp_path, monkeypatch):
    keywords = tmp_path / "keywords.txt"
    keywords.write_text("주제\n", encoding="utf-8")
    monkeypatch.setattr(
        shorts, "_run_chunk", lambda *_: (_ for _ in ()).throw(AssertionError)
    )

    assert shorts.main(["--keywords", str(keywords), "--dry-run"]) == 0
    assert keywords.read_text(encoding="utf-8") == "주제\n"
    assert not (tmp_path / "done.txt").exists()
