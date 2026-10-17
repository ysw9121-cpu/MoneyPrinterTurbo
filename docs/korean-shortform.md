# 찐숏폼 한국어 설정 안내

이 저장소는 MoneyPrinterTurbo를 한국어 숏폼 제작용으로 맞춘 버전입니다.

## 기본으로 바뀐 것

| 항목 | 원본 | 이 버전 |
|---|---|---|
| 화면 언어 | 중국어 | 한국어 (`language = "ko"`) |
| 대본 언어 | 자동 감지 | 한국어 (`video_language = "ko-KR"`) |
| 대본 AI | Moonshot (중국) | Anthropic Claude (`llm_provider = "anthropic"`) |
| 음성 | 중국어 여성 | 한국어 여성 SunHi (무료 Edge TTS) |
| 자막 글꼴 | 중국어 글꼴 (한글 깨짐) | Noto Sans KR Bold |

원본에 들어 있던 글꼴은 모두 한글을 지원하지 않아 한국어 자막이 □□□로 깨졌습니다.
`resource/fonts/NotoSansKR-Bold.ttf`(SIL OFL 1.1, 상업적 사용 가능)를 추가해서 해결했습니다.

## 처음 실행할 때

1. `config.example.toml`이 `config.toml`로 자동 복사됩니다.
2. `config.toml`에서 아래 두 가지를 채웁니다.
   - `anthropic_api_key`: https://platform.claude.com/settings/keys 에서 발급
   - `pexels_api_keys`: https://www.pexels.com/api/ 에서 무료 발급 (영상 소스)
3. 웹 화면 실행: `webui.bat`(윈도우) 또는 `sh webui.sh`(맥/리눅스)

Claude 구독(Pro/Max)이 있다면 API 키 대신 `llm_provider = "claude_code"`를 쓸 수 있습니다.
이 경우 컴퓨터에 `claude` 명령어가 설치되어 있고 로그인되어 있어야 합니다.

## 음성 바꾸기

무료 Edge TTS 한국어 음성은 세 가지입니다.

- `ko-KR-SunHiNeural-Female` (여성, 기본값)
- `ko-KR-InJoonNeural-Male` (남성)
- `ko-KR-HyunsuMultilingualNeural-Male` (남성)

더 자연스러운 목소리가 필요하면 웹 화면에서 ElevenLabs를 선택하고 API 키를 넣으세요.

## 키워드 목록으로 여러 편 한 번에 만들기

1. `shortform/keywords.txt`를 메모장으로 엽니다.
2. 한 줄에 주제 하나씩 적습니다. 대본에 바라는 점이 있으면 `|` 뒤에 적습니다.
   ```
   신차 살 때 할부와 리스 중 뭐가 유리할까 | 30초 분량, 첫 문장은 질문으로 시작
   자동차 보험료 아끼는 3가지 방법
   ```
3. 실행합니다.
   - 윈도우: `shorts.bat` 더블클릭 (하루 3편만: 명령창에서 `shorts.bat --limit 3`)
   - 맥/리눅스: `sh shorts.sh --limit 3`
4. 제작에 성공한 주제는 `keywords.txt`에서 지워지고 `shortform/done.txt`에
   날짜와 영상 파일 위치가 기록됩니다. 실패한 주제는 남아 있다가 다음 실행 때 다시 만듭니다.

자주 쓰는 옵션

| 하고 싶은 것 | 명령 |
|---|---|
| 만들지 않고 목록만 확인 | `shorts.bat --dry-run` |
| 위에서부터 3편만 | `shorts.bat --limit 3` |
| 남성 목소리로 | `shorts.bat -- --voice-name ko-KR-InJoonNeural-Male` |
| 주제 하나로 2개 버전 | `shorts.bat -- --video-count 2` |

`--` 뒤에는 `cli.py`의 옵션을 그대로 쓸 수 있습니다 (`uv run python cli.py --help`).
