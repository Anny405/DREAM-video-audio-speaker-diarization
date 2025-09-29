from pathlib import Path
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
from yt_dlp import YoutubeDL
from faster_whisper import WhisperModel
import ffmpeg
import os


BASE_DIR = Path(__file__).resolve().parent
OUT_DIR = BASE_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def out(name: str) -> str:
    return str(OUT_DIR / name)


def sanitize_url(u: str) -> str:
    p = urlparse(u)
    qs = dict(parse_qsl(p.query))
    qs.pop("t", None)
    return urlunparse(p._replace(query=urlencode(qs)))

def to_srt_timestamp(t: float) -> str:
    ms = int(t * 1000)
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


# ---------- Core ----------
def download_audio(youtube_url: str) -> str:
    """
    Download best audio from YouTube using browser cookies (if available),
    extract to WAV, then resample to 16k mono.
    Returns the final WAV path.
    """
    url = sanitize_url(youtube_url)

    ydl_opts = {
        # Download best audio, then extract wav via ffmpeg postprocessor
        "format": "bestaudio/best",
        "outtmpl": out("audio.%(ext)s"), 
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "wav",
            "preferredquality": "0",
        }],
        "noprogress": True,
        "quiet": False,
        "cookiesfrombrowser": ("chrome",),   # ("safari",)
        "extractor_args": {"youtube": {"player_client": ["web"]}},
        "concurrent_fragment_downloads": 1,
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Safari"
        },
        "retries": 10,
        "fragment_retries": 10,}

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    src = out("audio.wav")
    final_wav = out("audio.wav")
    ffmpeg.input(src).output(final_wav, ac=1, ar=16000).overwrite_output().run()
    print(f"[✓] Audio saved: {final_wav}")
    return final_wav


def transcribe_wav(
    wav_path: str,
    txt_path: str,
    srt_path: str,
    model_size: str = "medium",
    use_vad: bool = False,
    beam_size: int = 5,
):
    model = WhisperModel(model_size, device="auto")
    segments, _ = model.transcribe(wav_path, vad_filter=use_vad, beam_size=beam_size)

    with open(txt_path, "w", encoding="utf-8") as f_txt, open(srt_path, "w", encoding="utf-8") as f_srt:
        for i, seg in enumerate(segments, start=1):
            text = seg.text.strip()
            f_txt.write(text + "\n")

            start_ts = to_srt_timestamp(seg.start)
            end_ts = to_srt_timestamp(seg.end)
            f_srt.write(f"{i}\n{start_ts} --> {end_ts}\n{text}\n\n")

    print(f"[✓] Transcript: {txt_path}")
    print(f"[✓] Subtitles : {srt_path}")


def transcribe_local_file(
    input_media_path: str,
    txt_path: str = None,
    srt_path: str = None,
    model_size: str = "medium",
):
    """
    Transcribe a local video/audio file:
    - If video, extract audio first.
    - Always convert to 16k mono WAV for Whisper.
    """
    input_media_path = str(Path(input_media_path).expanduser())
    converted_wav = out("converted.wav")
    (
        ffmpeg
        .input(input_media_path)
        .output(converted_wav, ac=1, ar=16000)
        .overwrite_output()
        .run()
    )

    if txt_path is None:
        txt_path = out("local_transcript.txt")
    if srt_path is None:
        srt_path = out("local_subtitle.srt")

    transcribe_wav(converted_wav, txt_path, srt_path, model_size=model_size)












if __name__ == "__main__":
    print("Choose mode:")
    print("  1) YouTube → transcript")
    print("  2) Local file (video/audio) → transcript")
    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        url = input("Enter YouTube video URL: ").strip()
        wav = download_audio(url)
        transcribe_wav(
            wav_path=wav,
            txt_path=out("transcript.txt"),
            srt_path=out("subtitle.srt"),
            model_size="medium",
            use_vad=False,#this is the filter i talked about ;)
        )

    elif choice == "2":
        local_path = input("Enter path to local video/audio file: ").strip()
        transcribe_local_file(local_path, model_size="medium")

    else:
        print("Invalid choice")
