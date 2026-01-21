# DREAM-AI: Video → Audio → Transcript with Speaker Diarization

## This project automatically processes video or audio files into:
- 1. 16 kHz mono WAV audio
- 2. Text transcription using Whisper (faster-whisper)
- 3. Speaker diarization (who-spoke-when) using pyannote 3.1
- 4. Merged transcript with speaker labels

### Prerequisites
- Python 3.12 for Whisper
- Python 3.11 for pyannote 3.1
- ffmpeg
    - brew install ffmpeg
- Hugging Face account IMPORTANT!! 
    - request and accept access for:
        - pyannote/speaker-diarization-3.1
        - pyannote/segmentation-3.0
    - Then copy the Access Token from: huggingface.co/settings/tokens

### ! Have to run this code step by step as the output from Transcription goes into diarization
### Setup -- Whisper Environment: 

- from terminal:

#### Bash
```bash
python3.12 -m venv venv_whisper
source venv_whisper/bin/activate
pip install -r requirements_whisper.txt
```

- Run Transcription
#### Bash
```bash
python main.py
```

- When prompted, provide a local video/audio path, e.g.:

#### Bash
```bash
/Users/annyqi/Downloads/video1.MP4
```

- Outputs (under output/):

    - audio.wav – extracted mono 16 kHz audio

    - transcript.json – list of {start, end, text}

    - transcript.txt

    - subtitle.srt


### Setup -- Pyannote 3.1 Environment (Speaker Diarization): 


- from terminal:

#### Bash
```bash
python3.11 -m venv venv_pyannote31
source venv_pyannote31/bin/activate
pip install -r requirements_pyannote31.txt
```

- Authenticate to Hugging Face
#### Bash
```bash
export HF_TOKEN=hfxxxxxxxxxxxx
python -c "from huggingface_hub import login; import os; login(token=os.environ['HF_TOKEN'])"

```

- Run Diarization
#### Bash
```bash
python diarization_only.py
```

- Outputs (under output/):
    - diarization.rttm 

    - standard RTTM format


### Merge Transcription + Speaker Labels

#### Bash
```bash
source venv_whisper/bin/activate

python merge_segments.py \
  --transcript output/transcript.json \
  --diarization output/diarization.rttm \
  --out output/final_segments.csv
```

- Output
  - output/final_segments.csv


### !Output folder should be empty every time before running a new video!

#### Bash
```bash
rm -rf output/*
mkdir -p output
```
