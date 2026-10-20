# Audio Timestamp Marker

Plays the audio track from a video and writes SRT timestamp markers as you press the space bar.

## Run

Requires Python 3.10+ and a video file with an audio track.

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py path\to\video.mp4 --output timestamps.srt
```

Press `Space` to mark the start and end of each consecutive segment. Press `Q` to stop. The temporary extracted audio is deleted when the program exits.
