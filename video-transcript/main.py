from yt_dlp import YoutubeDL
from faster_whisper import WhisperModel
import ffmpeg
import os
#youtube video: video to transcript

def download_audio(youtube_url, output_path="output/audio.wav"):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'output/temp.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '0',
        }],
        'quiet': False,
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])
    ffmpeg.input("output/temp.wav").output(output_path, ac=1, ar=16000).overwrite_output().run()
    print(f"[✓] Audio saved as {output_path}")


def transcribe_audio(audio_path, output_txt="output/transcript.txt", output_srt="output/subtitle.srt", model_size="medium"):
    model = WhisperModel(model_size, device="auto")
   #segments, _ = model.transcribe(audio_path, vad_filter=True, beam_size=5)
    segments, _ = model.transcribe(audio_path, vad_filter=False, beam_size=5)

    with open(output_txt, "w", encoding="utf-8") as f_txt, open(output_srt, "w", encoding="utf-8") as f_srt:
        for i, segment in enumerate(segments, start=1):
            text = segment.text.strip()

            f_txt.write(text + "\n")
            def format_timestamp(t):
                ms = int(t * 1000)
                h, ms = divmod(ms, 3600000)
                m, ms = divmod(ms, 60000)
                s, ms = divmod(ms, 1000)
                return f"{h:02}:{m:02}:{s:02},{ms:03}"

            start_time = format_timestamp(segment.start)
            end_time = format_timestamp(segment.end)
            f_srt.write(f"{i}\n{start_time} --> {end_time}\n{text}\n\n")

    print(f"[✓] Transcription saved to {output_txt}")
    print(f"[✓] Subtitles saved to {output_srt}")


def transcribe_local_file(audio_path, output_txt="output/local_transcript.txt", output_srt="output/local_subtitle.srt", model_size="medium"):
    model = WhisperModel(model_size, device="auto")
    converted_path = "output/converted.wav"
    ffmpeg.input(audio_path).output(converted_path, ac=1, ar=16000).overwrite_output().run()
    segments, _ = model.transcribe(converted_path, vad_filter=True, beam_size=5)

    with open(output_txt, "w", encoding="utf-8") as f_txt, open(output_srt, "w", encoding="utf-8") as f_srt:
        for i, seg in enumerate(segments, 1):
            text = seg.text.strip()
            f_txt.write(text + "\n")

            def fmt(t):
                ms = int(t * 1000)
                h, ms = divmod(ms, 3600000)
                m, ms = divmod(ms, 60000)
                s, ms = divmod(ms, 1000)
                return f"{h:02}:{m:02}:{s:02},{ms:03}"
            
            f_srt.write(f"{i}\n{fmt(seg.start)} --> {fmt(seg.end)}\n{text}\n\n")
    print(f"[✓] Local audio transcription done!")
    print(f"    Text: {output_txt}")
    print(f"    Subtitles: {output_srt}")









if __name__ == "__main__":
    url = input("Enter YouTube video URL: ").strip()
    download_audio(url)
    transcribe_audio("output/audio.wav", "output/transcript.txt", "output/subtitle.srt")


''' local_path = input("Enter path to local audio file (e.g. local_audio/my.wav): ").strip()
    transcribe_local_file(local_path)'''
