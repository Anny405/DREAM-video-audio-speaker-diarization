# DREAM-AI: Video-Transcript Tool

This repository contains the **video-transcript** submodule of the DREAM-AI project.  
It supports both downloading YouTube videos for transcription and transcribing local video/audio files.  
All transcription is performed using [Whisper](https://github.com/openai/whisper).

---

## Features

### From YouTube
- Download audio (`.wav`) from YouTube videos using [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- Convert audio with [ffmpeg](https://ffmpeg.org/)
- Transcribe audio into plain text with Whisper
- Generate `.srt` subtitles for easy video integration

### From Local Files
- Extract audio from local video files (e.g., `.mp4`, `.mov`, `.mkv`)
- Directly transcribe local audio files (`.wav`, `.mp3`, etc.)
- Save transcript (`.txt`) and subtitles (`.srt`) into the `output/` folder

---
## Usage
1. YouTube Transcription

- Run the script and enter a YouTube URL:

- python video-transcript/main.py

2. Local File Transcription

- Run the script and enter a local video/audio file path:

- python video-transcript/main.py
- Example: /Users/annyqi/Downloads/video.mp4

## Note:
- Always activate the venv/ before running.
- YouTube troubleshooting: Update yt-dlp