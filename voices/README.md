# Voice references

Chatterbox clones a voice from a short reference clip. Each file here should be a
clean, silence-compacted, 24 kHz mono PCM WAV of 10-15 seconds of continuous speech
(no music, no room rumble, no long pauses).

Naming is `<voice>_voice_ref_continuous.wav`, where `<voice>` matches the first word
of the narrator name lowercased (`Eli C. Tric` -> `eli`). The pipeline resolves
`voices/<voice>_voice_ref_continuous.wav`, then `voices/<voice>_voice_ref.wav`.

```bash
./scripts/audiobook/prepare_voice_ref.sh ~/recording.m4a voices/eli_voice_ref_continuous.wav
```

Reference WAVs are git-ignored (`voices/*.wav`) because they are large personal
recordings. Supply your own; the pipeline reports a clear error when one is missing.
