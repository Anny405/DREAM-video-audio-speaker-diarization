# main.py  —— local file -> transcription only (no diarization, no YouTube)
from pathlib import Path
from faster_whisper import WhisperModel
import ffmpeg
import json

BASE_DIR = Path(__file__).resolve().parent
OUT_DIR = BASE_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def out(name: str) -> str:
    return str(OUT_DIR / name)

def to_srt_timestamp(t: float) -> str:
    ms = int(t * 1000)
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def extract_to_16k_mono(input_media_path: str) -> str:
    """Extract audio from input media file and convert to 16kHz mono WAV.""" 
    converted_wav = out("audio.wav")
    (
        ffmpeg
        .input(str(Path(input_media_path).expanduser()))
        .output(converted_wav, ac=1, ar=16000)
        .overwrite_output()
        .run()
    )
    return converted_wav

def transcribe_wav(
    wav_path: str,
    txt_path: str,
    srt_path: str,
    json_path: str,
    model_size: str = "medium",
    use_vad: bool = False,
    beam_size: int = 5,
):
    model = WhisperModel(model_size, device="auto")
    segments, _ = model.transcribe(
        wav_path,
        vad_filter=use_vad,
        beam_size=beam_size,
        word_timestamps=False
    )

    # 写入 txt / srt / json
    seg_list = []
    with open(txt_path, "w", encoding="utf-8") as f_txt, open(srt_path, "w", encoding="utf-8") as f_srt:
        for i, seg in enumerate(segments, start=1):
            text = (seg.text or "").strip()
            f_txt.write(text + "\n")
            f_srt.write(f"{i}\n{to_srt_timestamp(seg.start)} --> {to_srt_timestamp(seg.end)}\n{text}\n\n")
            seg_list.append({
                "start": round(seg.start, 3),
                "end": round(seg.end, 3),
                "text": text,
                "confidence": 1.0 
            })

    with open(json_path, "w", encoding="utf-8") as f_json:
        json.dump(seg_list, f_json, ensure_ascii=False, indent=2)

    print(f"[✓] Audio       : {wav_path}")
    print(f"[✓] Transcript  : {txt_path}")
    print(f"[✓] Subtitles   : {srt_path}")
    print(f"[✓] JSON        : {json_path}")

if __name__ == "__main__":
    local_path = input("Enter path to local video/audio file: ").strip()
    wav = extract_to_16k_mono(local_path)
    transcribe_wav(
        wav_path=wav,
        txt_path=out("transcript.txt"),
        srt_path=out("subtitle.srt"),
        json_path=out("transcript.json"),
        model_size="medium",
        use_vad=False
    )