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
