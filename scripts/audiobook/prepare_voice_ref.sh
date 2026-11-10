#!/usr/bin/env bash
set -euo pipefail

# Extract a clean, silence-compacted, 24 kHz mono PCM WAV from any raw voice
# recording. Chatterbox uses the first 10-15 seconds of the reference prompt to
# lock timbre, prosody, and pacing, so dead air and room rumble must go first.
#
# Usage: ./scripts/audiobook/prepare_voice_ref.sh <input_audio> <output_wav> [start_sec] [end_sec]
# Example: ./scripts/audiobook/prepare_voice_ref.sh ~/recording.m4a voices/eli_voice_ref_continuous.wav

INPUT="${1:?Usage: $0 <input_audio> <output_wav> [start_sec] [end_sec]}"
OUTPUT="${2:?Usage: $0 <input_audio> <output_wav> [start_sec] [end_sec]}"
START="${3:-0}"
END="${4:-25}"

command -v ffmpeg >/dev/null || { echo "ffmpeg is required" >&2; exit 1; }
mkdir -p "$(dirname "$OUTPUT")"

ffmpeg -y -loglevel error \
  -ss "$START" -to "$END" -i "$INPUT" \
  -af "highpass=f=85,silenceremove=stop_periods=-1:stop_duration=0.35:stop_threshold=-38dB" \
  -t 14.5 -ar 24000 -ac 1 -c:a pcm_s16le "$OUTPUT"

echo "Created clean 24kHz mono continuous voice reference: $OUTPUT"
ffprobe -hide_banner "$OUTPUT" 2>&1 | grep -E "Duration|Stream"
