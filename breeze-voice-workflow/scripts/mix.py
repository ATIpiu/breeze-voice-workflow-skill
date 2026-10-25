"""Portable voice/BGM mixer: active-sample RMS, ducking and final loudnorm."""
import argparse
import json
import math
from pathlib import Path
import subprocess
import tempfile


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--ffmpeg', default='ffmpeg')
    a = p.parse_args()
    import numpy as np
    plan = json.loads(a.plan.read_text(encoding='utf-8-sig'))
    rate = 48000
    total = float(plan['total'])
    if not math.isfinite(total) or not 0 < total <= 3600:
        p.error('Total duration must be finite, positive and at most one hour')
    frames = math.ceil(total * rate)
    if a.out.exists():
        p.error('Output exists; choose a new name')
    a.out.parent.mkdir(parents=True, exist_ok=True)

    def load(name, channels):
        path = Path(name)
        if not path.is_absolute():
            path = a.plan.resolve().parent / path
        result = subprocess.run([a.ffmpeg, '-v', 'error', '-i', str(path), '-ac', str(channels),
                                 '-ar', str(rate), '-f', 'f32le', '-'], capture_output=True, check=True)
        data = np.frombuffer(result.stdout, dtype='<f4').copy().reshape(-1, channels)
        if not len(data) or not np.isfinite(data).all():
            raise ValueError('Empty or invalid audio input')
        return data

    voice = np.zeros((frames, 2), dtype=np.float32)
    active = np.zeros(frames, dtype=bool)
    for event in plan['vo']:
        t = float(event['t'])
        if not math.isfinite(t) or t < 0:
            raise ValueError('Voice start times must be finite and non-negative')
        data = load(event['file'], 1)[:, 0]
        non_silent = data[np.abs(data) > 0.01]
        if not len(non_silent):
            raise ValueError('Silent voice take')
        data *= 0.12 / (float(np.sqrt(np.mean(non_silent ** 2))) + 1e-9)
        start = round(t * rate)
        end = start + len(data)
        if end > frames:
            raise ValueError('Voice extends beyond plan.total; increase total instead of truncating')
        voice[start:end] += data[:, None]
        active[start:end] = True
    mix = voice
    if plan.get('bgm'):
        bgm = load(plan['bgm'], 2)
        if len(bgm) < frames:
            bgm = np.tile(bgm, (math.ceil(frames / len(bgm)), 1))
        bgm = bgm[:frames]
        bgm *= 0.05 / (float(np.sqrt(np.mean(bgm ** 2))) + 1e-9)
        duck_db = float(plan.get('duck_db', -7))
        if not math.isfinite(duck_db) or not -60 <= duck_db <= 0:
            raise ValueError('duck_db must be between -60 and 0')
        gain, current = np.ones(frames, dtype=np.float32), 1.0
        low = 10 ** (duck_db / 20)
        attack = 1 - math.exp(-480 / (0.08 * rate))
        release = 1 - math.exp(-480 / (0.4 * rate))
        for n in range(0, frames, 480):
            target = low if active[n:n + 480].any() else 1.0
            current += (target - current) * (attack if target < current else release)
            gain[n:n + 480] = current
        fade_in = min(frames, 480)
        fade_seconds = float(plan.get('tail_fade', 2.5))
        if not math.isfinite(fade_seconds) or fade_seconds < 0:
            raise ValueError('tail_fade must be finite and non-negative')
        fade_out = min(frames, round(fade_seconds * rate))
        gain[:fade_in] *= np.linspace(0, 1, fade_in)
        if fade_out:
            gain[-fade_out:] *= np.linspace(1, 0, fade_out)
        mix = voice + bgm * gain[:, None]
    loudness, peak = float(plan.get('lufs', -14)), float(plan.get('tp', -1.5))
    if not math.isfinite(loudness) or not -70 <= loudness <= -5 or not math.isfinite(peak) or not -9 <= peak <= 0:
        raise ValueError('Invalid loudnorm target')
    with tempfile.TemporaryDirectory(prefix='breeze-mix-') as tmp:
        raw = Path(tmp) / 'mix.f32'
        mix.astype('<f4').tofile(raw)
        subprocess.run([a.ffmpeg, '-v', 'error', '-n', '-f', 'f32le', '-ar', str(rate), '-ac', '2',
                        '-i', str(raw), '-af', f'loudnorm=I={loudness}:TP={peak}:LRA=11',
                        '-ar', str(rate), '-c:a', 'pcm_s16le', str(a.out)], check=True)
    print('Mixed audio written. Measure and listen to the result before use.')


if __name__ == '__main__':
    main()
