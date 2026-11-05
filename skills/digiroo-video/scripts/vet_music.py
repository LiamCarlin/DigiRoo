#!/usr/bin/env python3
"""
vet_music.py — check a music track BEFORE it goes under a cut, so a bed that fights her voice never gets that far.

    python3 vet_music.py bed.mp3 [other.mp3 ...] [--no-whisper]

For each track: length, loudness and range, how long the intro takes to start, how much of its energy sits in the
1-4 kHz band where speech lives (a busy bed there masks her consonants), and whether it has singing in it (Whisper
hears words in it; a sung bed never goes under a voice-over). Prints a verdict per track. It never decides the
licence: that is read on the track's own page, then written into edit.json as "license" and "source".
"""
import argparse, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dvlib as L


def vocals(path):
    """Words Whisper can hear in the track, or None when faster-whisper isn't installed."""
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return None
    try:
        segs, _ = WhisperModel("base", device="cpu", compute_type="int8").transcribe(
            path, vad_filter=True, language="en", condition_on_previous_text=False)
        heard = [s for s in segs if s.no_speech_prob < 0.5 and s.avg_logprob > -1.0 and len(s.text.split()) >= 2]
        return " / ".join(s.text.strip() for s in heard)[:120]
    except Exception as e:  # model download blocked, odd codec
        return f"not checked ({e.__class__.__name__})"


def vet(path, whisper=True):
    info = L.probe(path); ld = L.loudness(path)
    lv = L.level_series(path); band = L.level_series(path, pre=L.SPEECH_BAND)
    full_db, band_db = L._power_mean([v for _, v in lv]), L._power_mean([v for _, v in band])
    share = round(band_db - full_db, 1) if full_db is not None and band_db is not None else None
    start = next((t for t, v in lv if v > (full_db or -60) - 20), 0.0)
    sung = vocals(path) if whisper else None
    notes, verdict = [], "use"
    if info["duration"] < 20:
        notes.append(f"only {info['duration']:.0f}s: it will loop under a 30 s cut")
    if start > 1.0:
        notes.append(f"takes {start:.1f}s to start: set \"start\": {start:.1f} in the music block")
    if ld["lra"] is not None and ld["lra"] > 10:
        notes.append(f"big swings in level (LRA {ld['lra']} LU): pick a steady stretch with \"start\"")
    if share is not None and share > -6:
        notes.append(f"busy in the voice range (1-4 kHz only {abs(share)} dB under the whole track): talking cuts need under_voice_db 15+")
        verdict = "use with care"
    if sung and not sung.startswith("not checked"):
        notes.append(f"has singing (\"{sung[:50]}…\"): text-story cuts only, never under a voice")
        verdict = "no voice-overs"
    return {"track": os.path.basename(path), "length": f"{info['duration']:.0f}s", "lufs": ld["lufs"], "lra": ld["lra"],
            "speech_band_db": share, "vocals": "none heard" if sung == "" else (sung or "not checked"), "verdict": verdict,
            "notes": notes}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tracks", nargs="+"); ap.add_argument("--no-whisper", action="store_true")
    a = ap.parse_args()
    print("| Track | Verdict | Length | LUFS | LRA | 1-4 kHz vs whole | Vocals | Notes |\n|---|---|---|---|---|---|---|---|")
    for t in a.tracks:
        r = vet(t, not a.no_whisper)
        print(f"| {r['track']} | **{r['verdict']}** | {r['length']} | {r['lufs']} | {r['lra']} | {r['speech_band_db']} dB | "
              f"{r['vocals']} | {'; '.join(r['notes']) or 'steady, clear of the voice range'} |")


if __name__ == "__main__":
    main()
