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

## 맥 한 줄 설치

터미널에 아래 한 줄을 붙여넣으면 설치, Pexels 키 저장, Claude 구독 로그인, 웹 화면 실행까지 한 번에 진행됩니다.

```
curl -fsSL https://raw.githubusercontent.com/ysw9121-cpu/MoneyPrinterTurbo/main/install_mac.sh | bash
```

- 프로그램은 `~/MoneyPrinterTurbo`에 설치됩니다.
- 대본은 Claude 구독(Claude Code)으로 씁니다. API 키는 필요 없습니다.
- 영상 소스 키는 Pexels나 Pixabay 중 하나만 있으면 됩니다. Pexels가 새 키 발급을 멈춘 경우 https://pixabay.com/api/docs/ 에서 Pixabay 키를 받으세요. Pixabay 키만 넣으면 영상 소스가 Pixabay로 자동 설정됩니다.
- 같은 줄을 다시 실행하면 최신 버전으로 업데이트되고, `config.toml`과 `keywords.txt`는 그대로 남습니다.
- 다음부터 실행: `cd ~/MoneyPrinterTurbo && sh webui.sh`

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

## 쇼츠·릴스·틱톡 자동 업로드

원본에 들어 있는 Upload-Post 연동을 씁니다. 영상이 완성되면 바로 올라갑니다.

1. https://upload-post.com 에 가입하고 유튜브·인스타그램·틱톡 계정을 연결합니다.
2. Upload-Post에서 API 키와 사용자 이름(username)을 확인합니다.
3. `config.toml`에서 아래 값을 바꿉니다.
   ```toml
   upload_post_enabled = true
   upload_post_api_key = "발급받은 키"
   upload_post_username = "Upload-Post 사용자 이름"
   upload_post_platforms = ["youtube", "instagram", "tiktok"]
   upload_post_auto_upload = true
   upload_post_youtube_privacy_status = "public"   # 처음엔 "private"로 시험해 보세요
   ```

알아둘 점
- 업로드는 영상 제작이 끝난 뒤 진행되고, 업로드가 다 끝나야 실행 창이 닫힙니다.
- 한 번에 대기할 수 있는 업로드는 10개(`upload_post_max_pending_tasks`)입니다.
  하루에 많이 만들 때는 이 숫자를 늘리거나 `--limit`로 편수를 줄이세요.
- 업로드 결과는 `shortform\auto-run.log`(자동 실행) 또는 실행 창에서 확인합니다.

## 매일 정해진 시각에 자동 제작 (윈도우)

`schedule_shorts.bat`를 더블클릭하면 매일 오전 9시에 3편을 만드는 예약이 등록됩니다.
시각과 편수를 바꾸려면 명령창에서 실행합니다.

| 하고 싶은 것 | 명령 |
|---|---|
| 매일 09:00에 3편 | `schedule_shorts.bat` |
| 매일 20:30에 5편 | `schedule_shorts.bat 20:30 5` |
| 자동 제작 해제 | `schedule_shorts.bat off` |

- 예약 시각에 컴퓨터가 켜져 있어야 합니다.
- 결과는 `shortform\auto-run.log`와 `shortform\done.txt`에 남습니다.
- `keywords.txt`의 주제가 다 떨어지면 아무것도 만들지 않습니다. 주제를 미리 넉넉히 적어두세요.

맥/리눅스는 `crontab -e`에 다음 한 줄을 추가합니다 (매일 09:00, 3편).
```
0 9 * * * cd /설치경로/MoneyPrinterTurbo && sh shorts.sh --limit 3 >> shortform/auto-run.log 2>&1
```

## 민담·야담 AI 그림 설정 (한 번에 적용)

무료 영상 대신 대본 장면마다 AI 그림을 만들고 천천히 확대해 영상으로 씁니다.

1. 웹 화면을 끕니다 (프로그램 터미널에서 `Control + C`).
2. 터미널에서 실행합니다.
   ```
   cd ~/MoneyPrinterTurbo && uv run python presets.py folktale
   ```
   OpenAI API 키를 물으면 붙여넣습니다 (화면에는 보이지 않습니다).
3. 웹 화면을 다시 켭니다: `sh webui.sh`

바뀌는 것: 영상 소스 `openai_image`(gpt-image-1), 조선 민담 화풍 프롬프트,
대본 순서대로 장면 배치, 문단 4개(약 1분), 이야기꾼 말투 요청, 장면당 5초.
그림은 OpenAI API 요금이 장당 부과됩니다. 화풍은 설정 → 소재 소스 설정의
프롬프트 템플릿에서 바꿀 수 있습니다.
