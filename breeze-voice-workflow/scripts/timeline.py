"""Portable voice preparation; sequential or explicitly beat-aligned placement."""
import argparse
import json
import math
from pathlib import Path
import re
import subprocess


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lines', type=Path, required=True)
    p.add_argument('--input', type=Path, required=True, help='Directory of L01_s42.wav takes')
    p.add_argument('--out', type=Path, required=True, help='New output directory')
    p.add_argument('--seed', type=int, default=42)
    p.add_argument('--speed', type=float, default=1.25)
    p.add_argument('--gap', type=float, default=0.25)
    p.add_argument('--bpm', type=float, help='Optional: place each line at the next beat')
    p.add_argument('--bgm', type=Path, help='Your own licensed music; optional')
    p.add_argument('--ffmpeg', default='ffmpeg')
    a = p.parse_args()
    if not math.isfinite(a.speed) or not 0.5 <= a.speed <= 2:
        p.error('--speed must be between 0.5 and 2')
    if not math.isfinite(a.gap) or a.gap < 0 or (a.bpm is not None and (not math.isfinite(a.bpm) or a.bpm <= 0)):
        p.error('Check --gap / --bpm')
    import numpy as np
    import soundfile as sf
    lines = json.loads(a.lines.read_text(encoding='utf-8-sig'))
    if not isinstance(lines, list) or not lines:
        p.error('Need a non-empty line array')
    ids = [line.get('id', '') for line in lines]
    if len(ids) != len(set(ids)) or any(not re.fullmatch(r'[A-Za-z0-9_-]+', str(i)) for i in ids):
        p.error('Need unique ASCII file-safe line ids')
    sources = [a.input / f'{i}_s{a.seed}.wav' for i in ids]
    if any(not source.is_file() for source in sources) or (a.bgm and not a.bgm.is_file()):
        p.error('Missing take or background music file')
    if a.out.exists():
        p.error('--out must be a new directory, to preserve previous work')
    a.out.mkdir(parents=True)
    (a.out / 'vo').mkdir()
    events, cursor = [], 0.0
    for line, source in zip(lines, sources):
        result = subprocess.run([a.ffmpeg, '-v', 'error', '-i', str(source), '-af', f'atempo={a.speed}',
                                 '-ac', '1', '-ar', '24000', '-f', 'f32le', '-'], capture_output=True, check=True)
        audio = np.frombuffer(result.stdout, dtype='<f4').copy()
        index = np.flatnonzero(np.abs(audio) > 0.012)
        if not len(index) or not np.isfinite(audio).all():
            raise ValueError('Empty, silent or invalid take: ' + line['id'])
        audio = audio[max(0, index[0] - 480):min(len(audio), index[-1] + 1 + 1920)]
        if a.bpm:
            beat = 60 / a.bpm
            cursor = math.ceil((cursor - 1e-8) / beat) * beat
        filename = 'vo/' + line['id'] + '.wav'
        sf.write(a.out / filename, audio, 24000, subtype='PCM_16')
        duration = len(audio) / 24000
        events.append({'id': line['id'], 'file': filename, 'text': line.get('text', ''),
                       't': round(cursor, 6), 'dur': duration})
        cursor += duration + a.gap
    plan = {'total': cursor + 0.25, 'vo': events, 'duck_db': -7, 'lufs': -14,
            'tp': -1.5, 'tail_fade': 2.5}
    if a.bgm:
        plan['bgm'] = str(a.bgm.resolve())
    (a.out / 'plan.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Prepared', len(events), 'lines; plan.json written. No original project timing was reused.')


if __name__ == '__main__':
    main()
