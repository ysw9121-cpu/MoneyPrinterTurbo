"""찐숏폼 일괄 제작기: 키워드 목록 파일 한 줄 = 숏폼 한 편.

keywords.txt 형식
    # 으로 시작하는 줄과 빈 줄은 무시합니다.
    주제
    주제 | 대본에 바라는 점

사용 예
    uv run python shorts.py                     # 목록 전체 제작
    uv run python shorts.py --limit 3           # 위에서부터 3편만 제작
    uv run python shorts.py --dry-run           # 제작 없이 목록 확인만
    uv run python shorts.py -- --voice-name ko-KR-InJoonNeural-Male

`--` 뒤에 쓴 옵션은 cli.py로 그대로 넘어갑니다. 제작에 성공한 주제는
keywords.txt에서 지워지고 done.txt에 날짜·영상 경로와 함께 기록되므로,
매일 같은 명령을 돌려도 같은 주제를 다시 만들지 않습니다. 실패한 주제는
목록에 남아 다음 실행 때 다시 시도합니다.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from datetime import datetime
from typing import Sequence

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_KEYWORDS_FILE = os.path.join(ROOT_DIR, "shortform", "keywords.txt")
DEFAULT_LANGUAGE = "ko-KR"
# cli.py의 배치 한도(_BATCH_TASK_MAX_COUNT)와 같아야 한다.
BATCH_MAX_TASKS = 100


@dataclass
class Topic:
    line_index: int
    subject: str
    script_prompt: str = ""


def parse_keywords(lines: Sequence[str]) -> list[Topic]:
    topics = []
    for index, raw in enumerate(lines):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        subject, _, prompt = line.partition("|")
        subject = subject.strip()
        if subject:
            topics.append(Topic(index, subject, prompt.strip()))
    return topics


def build_manifest_entries(topics: Sequence[Topic]) -> list[dict]:
    entries = []
    for topic in topics:
        entry = {"video_subject": topic.subject}
        if topic.script_prompt:
            entry["video_script_prompt"] = topic.script_prompt
        entries.append(entry)
    return entries


def remove_done_lines(lines: Sequence[str], done_indexes: set[int]) -> list[str]:
    return [line for index, line in enumerate(lines) if index not in done_indexes]


def _has_option(args: Sequence[str], option: str) -> bool:
    return any(arg == option or arg.startswith(option + "=") for arg in args)


def build_cli_command(manifest_path: str, cli_args: Sequence[str]) -> list[str]:
    command = [
        sys.executable,
        os.path.join(ROOT_DIR, "cli.py"),
        "--batch-file",
        manifest_path,
    ]
    if not _has_option(cli_args, "--video-language"):
        command += ["--video-language", DEFAULT_LANGUAGE]
    # cli.py의 --video-source 기본값은 pexels로 고정이라 config.toml 설정을 직접 넘긴다.
    video_source = configured_video_source()
    if video_source and not _has_option(cli_args, "--video-source"):
        command += ["--video-source", video_source]
    return command + list(cli_args)


def configured_video_source() -> str:
    try:
        with open(os.path.join(ROOT_DIR, "config.toml"), "rb") as file:
            return str(tomllib.load(file).get("app", {}).get("video_source") or "")
    except (OSError, tomllib.TOMLDecodeError):
        return ""


def _read_lines(path: str) -> list[str]:
    with open(path, encoding="utf-8-sig") as file:
        return file.read().splitlines(keepends=True)


def _write_lines(path: str, lines: Sequence[str]) -> None:
    with open(path, "w", encoding="utf-8") as file:
        file.writelines(lines)


def _run_chunk(manifest_path: str, cli_args: Sequence[str]) -> dict | None:
    completed = subprocess.run(
        build_cli_command(manifest_path, cli_args),
        cwd=ROOT_DIR,
        stdout=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        # 윈도우에서 파이프 출력은 기본이 cp949라 한글 결과 JSON을 utf-8로 읽지 못한다.
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    try:
        return json.loads(completed.stdout.strip().splitlines()[-1])
    except (IndexError, json.JSONDecodeError):
        print(f"cli.py 결과를 읽지 못했습니다 (종료 코드 {completed.returncode})")
        return None


def parse_args(argv: Sequence[str] | None) -> tuple[argparse.Namespace, list[str]]:
    argv = list(sys.argv[1:] if argv is None else argv)
    cli_args: list[str] = []
    if "--" in argv:
        split = argv.index("--")
        argv, cli_args = argv[:split], argv[split + 1 :]

    parser = argparse.ArgumentParser(description="키워드 목록으로 숏폼을 일괄 제작합니다.")
    parser.add_argument(
        "--keywords", default=DEFAULT_KEYWORDS_FILE, help="키워드 목록 파일 경로"
    )
    parser.add_argument("--limit", type=int, default=0, help="이번에 만들 최대 편수 (0 = 전부)")
    parser.add_argument("--dry-run", action="store_true", help="제작하지 않고 목록만 확인")
    return parser.parse_args(argv), cli_args


def main(argv: Sequence[str] | None = None) -> int:
    args, cli_args = parse_args(argv)
    keywords_path = os.path.abspath(args.keywords)
    if not os.path.isfile(keywords_path):
        print(f"키워드 파일이 없습니다: {keywords_path}")
        return 2

    lines = _read_lines(keywords_path)
    topics = parse_keywords(lines)
    if args.limit > 0:
        topics = topics[: args.limit]
    if not topics:
        print("만들 주제가 없습니다. keywords.txt에 주제를 한 줄씩 적어주세요.")
        return 0

    print(f"제작할 숏폼 {len(topics)}편:")
    for number, topic in enumerate(topics, start=1):
        extra = f"  ({topic.script_prompt})" if topic.script_prompt else ""
        print(f"  {number}. {topic.subject}{extra}")
    if args.dry_run:
        return 0

    work_dir = os.path.join(ROOT_DIR, "storage", "shortform")
    os.makedirs(work_dir, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    done_path = os.path.join(os.path.dirname(keywords_path), "done.txt")
    done_indexes: set[int] = set()
    failed = 0

    for start in range(0, len(topics), BATCH_MAX_TASKS):
        chunk = topics[start : start + BATCH_MAX_TASKS]
        manifest_path = os.path.join(work_dir, f"batch-{stamp}-{start // BATCH_MAX_TASKS + 1}.jsonl")
        with open(manifest_path, "w", encoding="utf-8") as file:
            for entry in build_manifest_entries(chunk):
                file.write(json.dumps(entry, ensure_ascii=False) + "\n")

        summary = _run_chunk(manifest_path, cli_args)
        results = {task["index"]: task for task in (summary or {}).get("tasks", [])}
        done_records = []
        for position, topic in enumerate(chunk, start=1):
            task = results.get(position)
            if task and task.get("status") == "succeeded":
                done_indexes.add(topic.line_index)
                videos = (task.get("result") or {}).get("videos") or []
                done_records.append(
                    f"{datetime.now():%Y-%m-%d %H:%M}\t{topic.subject}\t{', '.join(videos)}\n"
                )
            else:
                failed += 1
                error = task.get("error") if task else "결과 없음"
                print(f"실패: {topic.subject} - {error}")
        if done_records:
            with open(done_path, "a", encoding="utf-8") as file:
                file.writelines(done_records)

    if done_indexes:
        # 시작할 때 읽은 줄 기준으로 지운다. 실행 중에 파일을 고치면 그 수정은 덮어써진다.
        _write_lines(keywords_path, remove_done_lines(lines, done_indexes))
    print(f"완료 {len(done_indexes)}편, 실패 {failed}편. 기록: {done_path}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
