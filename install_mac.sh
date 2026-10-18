#!/bin/bash
# 찐숏폼 맥 설치기: 터미널에 아래 한 줄을 붙여넣으면 설치부터 실행까지 끝납니다.
#   curl -fsSL https://raw.githubusercontent.com/ysw9121-cpu/MoneyPrinterTurbo/main/install_mac.sh | bash
# 다시 실행하면 최신 버전으로 업데이트합니다. config.toml(키 설정)과 keywords.txt는 그대로 둡니다.
set -e

APP_DIR="${MPT_APP_DIR:-$HOME/MoneyPrinterTurbo}"
REPO_TARBALL="https://github.com/ysw9121-cpu/MoneyPrinterTurbo/archive/refs/heads/main.tar.gz"
export PATH="$HOME/.local/bin:$PATH"

# curl ... | bash 로 실행하면 표준입력이 스크립트라서 질문은 터미널에서 직접 읽는다.
ask() {
  printf '%s' "$1" > /dev/tty
  read -r REPLY < /dev/tty || REPLY=""
}

# BSD(맥)와 GNU sed 모두에서 동작하도록 백업 파일을 만들고 지운다.
replace_line() {
  sed -i.bak "$1" "$2" && rm -f "$2.bak"
}

echo "[1/6] 설치 도구(uv) 확인"
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi

echo "[2/6] 프로그램 내려받기: $APP_DIR"
mkdir -p "$APP_DIR"
backup_dir="$(mktemp -d)"
if [ -f "$APP_DIR/shortform/keywords.txt" ]; then
  cp "$APP_DIR/shortform/keywords.txt" "$backup_dir/keywords.txt"
fi
curl -fsSL "$REPO_TARBALL" | tar -xz -C "$APP_DIR" --strip-components 1
if [ -f "$backup_dir/keywords.txt" ]; then
  cp "$backup_dir/keywords.txt" "$APP_DIR/shortform/keywords.txt"
fi
rm -rf "$backup_dir"
cd "$APP_DIR"

echo "[3/6] 파이썬과 필요한 부품 설치 (처음엔 5~10분 걸립니다)"
uv python install 3.11
uv sync --frozen

echo "[4/6] 설정 파일 준비"
if [ ! -f config.toml ]; then
  cp config.example.toml config.toml
  # 대본은 Claude 구독(Claude Code)으로 쓴다. API 키를 쓰려면 웹 화면에서 바꾸면 된다.
  replace_line 's/^llm_provider = "anthropic"/llm_provider = "claude_code"/' config.toml
fi
if grep -q '^pexels_api_keys = \[\]' config.toml; then
  ask "Pexels API 키를 붙여넣고 엔터 (나중에 넣으려면 그냥 엔터): "
  pexels_key="$(printf '%s' "$REPLY" | tr -cd 'A-Za-z0-9')"
  if [ -n "$pexels_key" ]; then
    replace_line "s/^pexels_api_keys = \[\]/pexels_api_keys = [\"$pexels_key\"]/" config.toml
    echo "Pexels 키를 저장했습니다."
  fi
fi

echo "[5/6] Claude Code 확인"
if ! command -v claude >/dev/null 2>&1; then
  curl -fsSL https://claude.ai/install.sh | bash
fi
ask "Claude 구독 계정으로 로그인할까요? 처음이면 y, 이미 했으면 n: "
case "$REPLY" in
  y|Y|ㅛ)
    echo "브라우저에서 로그인한 뒤, 터미널에 /exit 를 입력하면 설치가 이어집니다."
    claude < /dev/tty > /dev/tty || true
    ;;
esac

echo "[6/6] 설치 완료! 웹 화면을 엽니다."
echo "다음부터는 터미널에서:  cd ~/MoneyPrinterTurbo && sh webui.sh"
exec sh webui.sh
