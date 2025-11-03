# merge_segments.py
import json
import csv
import argparse
from pathlib import Path


def load_transcript(json_path):
    """load Whisper output的 transcript.json"""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    segments = []
    for seg in data:
        segments.append({
            "start": float(seg.get("start", 0)),
            "end": float(seg.get("end", 0)),
            "text": seg.get("text", "").strip(),
        })
    return segments


def load_diarization_rttm(rttm_path):
    """load RTTM file"""
    diar_segments = []
    with open(rttm_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.startswith("SPEAKER"):
                continue
            parts = line.strip().split()
            if len(parts) < 8:
                continue
            start = float(parts[3])
            dur = float(parts[4])
            speaker = parts[7]
            diar_segments.append({
                "speaker": speaker,
                "start": start,
                "end": start + dur,
            })
    return diar_segments


def align_segments(transcript, diarization):
    """把说话人标签和文字按时间匹配"""
    merged = []
    for t in transcript:
        # find the speaker interval that overlaps with the text segment
        candidates = [d for d in diarization if not (t["end"] < d["start"] or t["start"] > d["end"])]
        speaker = candidates[0]["speaker"] if candidates else "Unknown"
        merged.append({
            "start": t["start"],
            "end": t["end"],
            "speaker": speaker,
            "text": t["text"],
        })
    return merged


def write_csv(segments, out_path):
    """write to CSV"""
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["start", "end", "speaker", "text"])
        writer.writeheader()
        writer.writerows(segments)
    print(f"[✓] Wrote merged segments to {out_path}")


def main():
    ap = argparse.ArgumentParser(description="Merge Whisper transcript and Pyannote diarization.")
    ap.add_argument("--transcript", type=str, default="output/transcript.json")
    ap.add_argument("--diarization", type=str, default="output/diarization.rttm")
    ap.add_argument("--out", type=str, default="output/final_segments.csv")
    args = ap.parse_args()

    transcript = load_transcript(args.transcript)
    diarization = load_diarization_rttm(args.diarization)
    merged = align_segments(transcript, diarization)
    write_csv(merged, args.out)


if __name__ == "__main__":
    main()
