# diarization_only.py  (for 3.1)
import os
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "output"
AUDIO_IN = OUT_DIR / "audio.wav"
DIAR_JSON = OUT_DIR / "diarization.json"
DIAR_RTTM = OUT_DIR / "diarization.rttm"

def ensure_audio_exists(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"{path} not found. Please run main.py first to create output/audio.wav (16k mono).")

def write_rttm(segments, out_path: Path, file_id: str = "audio"):
    with out_path.open("w", encoding="utf-8") as f:
        for s in segments:
            start = s["start"]; dur = s["end"] - s["start"]; spk = s["speaker"]
            f.write(f"SPEAKER {file_id} 1 {start:.3f} {dur:.3f} <NA> <NA> {spk} <NA> <NA>\n")

def diarize(audio_path: Path) -> List[Dict[str, Any]]:
    from pyannote.audio import Pipeline

    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        raise RuntimeError("HF_TOKEN not set. Run:  export HF_TOKEN=your_hf_token")

    print("[INFO] Loading pyannote/speaker-diarization-3.1 ...")
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        use_auth_token=hf_token
    )

    print(f"[INFO] Running diarization on: {audio_path}")
    diarization = pipeline(str(audio_path))  # returns an Annotation

    #RTTM
    with open(DIAR_RTTM, "w", encoding="utf-8") as rttm:
        diarization.write_rttm(rttm)
    print(f"[✓] Wrote RTTM to {DIAR_RTTM}")

    segments: List[Dict[str, Any]] = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        segments.append({
            "speaker": speaker,
            "start": round(float(turn.start), 3),
            "end": round(float(turn.end), 3),
        })
    segments.sort(key=lambda x: (x["start"], x["end"]))
    return segments

def main():
    ap = argparse.ArgumentParser(description="Speaker diarization only (pyannote 3.1).")
    ap.add_argument("--audio", type=str, default=str(AUDIO_IN))
    ap.add_argument("--out_json", type=str, default=str(DIAR_JSON))
    ap.add_argument("--out_rttm", type=str, default=str(DIAR_RTTM))  # 保留参数名，但上面已写默认路径
    args = ap.parse_args()

    audio_path = Path(args.audio).resolve()
    ensure_audio_exists(audio_path)

    segments = diarize(audio_path)

    out_json = Path(args.out_json).resolve()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    with out_json.open("w", encoding="utf-8") as f:
        json.dump(segments, f, ensure_ascii=False, indent=2)
    print(f"[✓] Wrote diarization JSON to {out_json} ({len(segments)} segments)")

if __name__ == "__main__":
    main()
