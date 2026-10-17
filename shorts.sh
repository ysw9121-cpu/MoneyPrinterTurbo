#!/usr/bin/env sh
# 찐숏폼 일괄 제작: shortform/keywords.txt 의 주제를 한 줄에 한 편씩 만듭니다.
# 예) sh shorts.sh --limit 3
CURRENT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$CURRENT_DIR" || exit 1
export PYTHONPATH="$CURRENT_DIR${PYTHONPATH:+:$PYTHONPATH}"
if [ -x .venv/bin/python ]; then
  exec .venv/bin/python shorts.py "$@"
fi
exec uv run python shorts.py "$@"
