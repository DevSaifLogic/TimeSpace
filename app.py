import argparse
import os
import tempfile
import time
from pathlib import Path
from moviepy import VideoFileClip
from pynput import keyboard
import pygame

# Global variables for tracking timestamps and status
start_time_ms = None
entry_index = 1
file_handle = None
is_running = True
playback_start_time = 0


def format_timestamp(milliseconds):
    """Converts milliseconds into SRT time format (HH:MM:SS,mmm)."""
    hrs = int(milliseconds // 3600000)
    mins = int((milliseconds % 3600000) // 60000)
    secs = int((milliseconds % 60000) // 1000)
    ms = int(milliseconds % 1000)
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{ms:03d}"


def get_current_audio_ms():
    """Gets the current playback position in milliseconds."""
    if pygame.mixer.music.get_busy():
        return pygame.mixer.music.get_pos()
    return 0


def on_press(key):
    global start_time_ms, entry_index, file_handle, is_running

    try:
        # Detect Spacebar press
        if key == keyboard.Key.space:
            current_ms = get_current_audio_ms()
            formatted_time = format_timestamp(current_ms)

            if start_time_ms is None:
                # First press: Start entry 1
                start_time_ms = formatted_time
                print(f"[{entry_index}] Start: {start_time_ms}")
            else:
                # Subsequent presses: Register end timestamp and start next entry
                end_time = formatted_time
                print(f"[{entry_index}] End:   {end_time}")

                # Write to file in SRT format
                file_handle.write(f"{entry_index}\n")
                file_handle.write(f"{start_time_ms} --> {end_time}\n\n")
                file_handle.flush()

                # Chain to the next entry immediately
                entry_index += 1
                start_time_ms = formatted_time
                print(f"[{entry_index}] Start: {start_time_ms}")

        # Detect 'q' key press to quit
        elif hasattr(key, "char") and key.char == "q":
            print("\nStopping audio and saving file...")
            is_running = False
            return False  # Stop the keyboard listener

    except Exception as e:
        print(f"Error: {e}")


def mark_timestamps(video_path, output_txt_path):
    global file_handle, is_running

    video_path = Path(video_path)
    output_txt_path = Path(output_txt_path)
    if not video_path.is_file():
        raise FileNotFoundError(f"Input video not found: {video_path}")

    print("Extracting audio from video...")
    with VideoFileClip(str(video_path)) as clip:
        if clip.audio is None:
            raise ValueError(f"No audio track found in {video_path}")
        audio_fd, temp_audio = tempfile.mkstemp(suffix=".wav")
        os.close(audio_fd)
        clip.audio.write_audiofile(temp_audio, logger=None)

    try:
        pygame.mixer.init()
        pygame.mixer.music.load(temp_audio)

        file_handle = output_txt_path.open("w", encoding="utf-8")

        print("\n--- Audio Timestamp Tracker ---")
        print("SPACE : Register Start/End continuous timestamps")
        print("Q     : Quit and save file")
        print("Playing audio now...\n")

        pygame.mixer.music.play()

        listener = keyboard.Listener(on_press=on_press)
        listener.start()

        try:
            while is_running and pygame.mixer.music.get_busy():
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        finally:
            listener.stop()
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            file_handle.close()

        print(f"Saved timestamps to {output_txt_path}")
    finally:
        Path(temp_audio).unlink(missing_ok=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create SRT timestamps while listening to a video's audio.")
    parser.add_argument("video", type=Path, help="Path to the input video")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("timestamps.srt"),
        help="Output subtitle file (default: timestamps.srt)",
    )
    args = parser.parse_args()
    mark_timestamps(args.video, args.output)