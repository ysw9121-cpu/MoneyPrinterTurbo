import subprocess
from unittest.mock import patch

import imageio_ffmpeg
import pytest

from app.config import config
from app.services import voice as vs


class _Response:
    def __init__(self, status_code, content=b"", json_data=None):
        self.status_code = status_code
        self.content = content
        self.text = content.decode("utf-8", errors="replace")
        self._json = json_data

    def json(self):
        return self._json

    def close(self):
        pass


@pytest.fixture
def typecast_config(monkeypatch):
    for key, value in {"api_key": "tc-key", "model_id": "ssfm-v30", "emotion": "normal"}.items():
        monkeypatch.setitem(config.typecast, key, value)


def _mp3_bytes(tmp_path, seconds):
    path = tmp_path / f"tone-{seconds}.mp3"
    subprocess.run(
        [
            imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error",
            "-f", "lavfi", "-i", f"sine=frequency=440:duration={seconds}",
            "-ac", "1", "-ar", "24000", str(path),
        ],
        check=True,
    )
    return path.read_bytes()


def test_split_typecast_text_keeps_short_text_whole():
    assert vs.split_typecast_text("  안녕하세요.  ") == ["안녕하세요."]
    assert vs.split_typecast_text("") == []


def test_split_typecast_text_respects_limit_and_sentences():
    text = "첫 문장입니다. " * 300
    chunks = vs.split_typecast_text(text, max_chars=200)

    assert len(chunks) > 1
    assert all(len(chunk) <= 200 for chunk in chunks)
    assert all(chunk.endswith(".") for chunk in chunks)
    assert "".join(chunks).replace(" ", "") == text.replace(" ", "")


def test_split_typecast_text_breaks_overlong_sentence():
    chunks = vs.split_typecast_text("가" * 450, max_chars=200)

    assert [len(chunk) for chunk in chunks] == [200, 200, 50]


def test_get_typecast_voices_formats_korean_names(typecast_config):
    payload = [
        {"voice_id": "tc_b", "voice_name": {"eng": "Bora", "kor": "보라"}, "gender": "female"},
        {"voice_id": "tc_a", "voice_name": {"eng": "Minsu", "kor": "민수"}, "gender": "male"},
        {"voice_id": "tc_a", "voice_name": {"kor": "중복"}},
        {"voice_name": {"kor": "아이디 없음"}},
    ]
    with patch.object(vs.requests, "get", return_value=_Response(200, json_data=payload)) as get:
        voices = vs.get_typecast_voices("tc-key")

    assert voices == ["typecast:tc_a:민수-Male", "typecast:tc_b:보라-Female"]
    assert get.call_args.kwargs["headers"] == {"X-API-KEY": "tc-key"}
    assert get.call_args.kwargs["params"] == {"model": "ssfm-v30"}


def test_get_typecast_voices_returns_empty_on_error(typecast_config):
    assert vs.get_typecast_voices("") == []
    with patch.object(vs.requests, "get", return_value=_Response(401, b"denied")):
        assert vs.get_typecast_voices("bad") == []


def test_typecast_voice_dispatch_and_subtitle_routing():
    assert vs.is_typecast_voice("typecast:tc_a:민수")
    assert not vs.is_typecast_voice("elevenlabs:x:y")
    with patch.object(vs, "typecast_tts", return_value="ok") as tts:
        assert vs.tts("본문", "typecast:tc_a:민수-Male", 1.2, "out.mp3") == "ok"
    tts.assert_called_once_with("본문", "tc_a", "out.mp3", 1.2)


def test_typecast_tts_writes_audio_and_sends_preset(tmp_path, typecast_config):
    audio = _mp3_bytes(tmp_path, 1)
    voice_file = tmp_path / "audio.mp3"
    with patch.object(vs.requests, "post", return_value=_Response(200, audio)) as post:
        sub_maker = vs.typecast_tts("안녕하세요. 반갑습니다.", "tc_a", str(voice_file), 1.1)

    assert sub_maker is not None
    assert voice_file.stat().st_size > 0
    payload = post.call_args.kwargs["json"]
    assert payload["voice_id"] == "tc_a"
    assert payload["model"] == "ssfm-v30"
    assert payload["prompt"] == {
        "emotion_type": "preset", "emotion_preset": "normal", "emotion_intensity": 1.0,
    }
    assert payload["output"] == {"audio_format": "mp3", "audio_tempo": 1.1}
    assert post.call_args.kwargs["headers"]["X-API-KEY"] == "tc-key"
    assert not list(tmp_path.glob(".typecast-tts-*"))


def test_typecast_tts_joins_chunks_with_smart_context(tmp_path, typecast_config, monkeypatch):
    monkeypatch.setitem(config.typecast, "emotion", "smart")
    monkeypatch.setattr(vs, "_TYPECAST_MAX_CHARS", 15)
    audio = _mp3_bytes(tmp_path, 1)
    voice_file = tmp_path / "audio.mp3"
    text = "첫째 문장입니다. 둘째 문장입니다. 셋째 문장입니다."
    with patch.object(vs.requests, "post", return_value=_Response(200, audio)) as post:
        sub_maker = vs.typecast_tts(text, "tc_a", str(voice_file))

    assert sub_maker is not None
    assert post.call_count == 3
    prompts = [call.kwargs["json"]["prompt"] for call in post.call_args_list]
    assert prompts[0] == {"emotion_type": "smart", "next_text": "둘째 문장입니다."}
    assert prompts[1]["previous_text"] == "첫째 문장입니다."
    assert "next_text" not in prompts[2]
    clip = vs.AudioFileClip(str(voice_file))
    try:
        assert clip.duration == pytest.approx(3, abs=0.3)
    finally:
        clip.close()
    assert not list(tmp_path.glob(".typecast-tts-*"))


def test_typecast_tts_stops_on_auth_error(tmp_path, typecast_config):
    with patch.object(vs.requests, "post", return_value=_Response(403, b"plan")) as post:
        assert vs.typecast_tts("안녕", "tc_a", str(tmp_path / "a.mp3")) is None
    assert post.call_count == 1


def test_typecast_tts_requires_key_and_valid_speed(tmp_path, typecast_config, monkeypatch):
    with patch.object(vs.requests, "post") as post:
        assert vs.typecast_tts("안녕", "tc_a", str(tmp_path / "a.mp3"), 3.0) is None
        monkeypatch.setitem(config.typecast, "api_key", "")
        monkeypatch.delenv("TYPECAST_API_KEY", raising=False)
        assert vs.typecast_tts("안녕", "tc_a", str(tmp_path / "a.mp3")) is None
    post.assert_not_called()
