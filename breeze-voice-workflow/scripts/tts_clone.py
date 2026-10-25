"""Portable adaptation of a project-specific Breeze-TTS-2 batch wrapper."""
import argparse
import json
import math
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', type=Path, required=True, help='Official PyTorch source directory')
    p.add_argument('--model', type=Path, required=True, help='Original checkpoint directory, not GGUF')
    p.add_argument('--lines', type=Path, required=True)
    p.add_argument('--ref', type=Path)
    p.add_argument('--ref-text', type=Path)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--seeds', default='42')
    p.add_argument('--only', nargs='*', default=[])
    p.add_argument('--instruction')
    p.add_argument('--cfg', type=float, default=1.0)
    p.add_argument('--eager', action='store_true', help='Disable fast stages; original project used this')
    p.add_argument('--work-dir', type=Path, required=True, help='Existing or new ASCII-only temporary directory')
    p.add_argument('--overwrite', action='store_true', help='Explicitly allow replacing existing takes')
    p.add_argument('--validate-only', action='store_true', help='Check inputs without importing/loading model')
    a = p.parse_args()
    if bool(a.ref) != bool(a.ref_text):
        p.error('--ref and --ref-text must be provided together')
    if not a.ref and not a.instruction:
        p.error('Provide a reference pair or a voice-design instruction')
    if not math.isfinite(a.cfg) or a.cfg <= 0:
        p.error('--cfg must be finite and positive')
    if not (a.repo / 'breeze_infer/runtime.py').is_file() or not a.model.is_dir():
        p.error('Check --repo and --model: original PyTorch source and checkpoint are required')
    lines = json.loads(a.lines.read_text(encoding='utf-8-sig'))
    if not isinstance(lines, list) or not lines:
        p.error('--lines must contain a non-empty JSON array')
    ids = set()
    for line in lines:
        if not isinstance(line, dict) or not re.fullmatch(r'[A-Za-z0-9_-]+', str(line.get('id', ''))):
            p.error('Each line needs an ASCII file-safe id')
        if line['id'] in ids or not isinstance(line.get('text'), str) or not line['text'].strip():
            p.error('Line ids must be unique and text must be non-empty')
        ids.add(line['id'])
    if not set(a.only).issubset(ids):
        p.error('--only contains an unknown line id')
    try:
        seeds = [int(s.strip()) for s in a.seeds.split(',')]
    except ValueError:
        p.error('--seeds must be comma-separated integers')
    if not seeds or len(seeds) != len(set(seeds)) or any(s < 0 or s > 2**32 - 1 for s in seeds):
        p.error('Seeds must be unique integers between 0 and 4294967295')
    ref_text = None
    if a.ref:
        if not a.ref.is_file():
            p.error('Reference audio is missing')
        ref_text = a.ref_text.read_text(encoding='utf-8-sig').strip()
        if not ref_text:
            p.error('Reference transcript cannot be empty')
    work = a.work_dir.resolve()
    if not str(work).isascii():
        p.error('--work-dir must be an ASCII-only path')
    selected = [line for line in lines if not a.only or line['id'] in a.only]
    for line in selected:
        for seed in seeds:
            if (a.out / f"{line['id']}_s{seed}.wav").exists() and not a.overwrite:
                p.error('A take already exists; use a new output directory or --overwrite')
    if a.validate_only:
        print(f'Inputs valid: {len(selected)} lines, {len(seeds)} seeds. Model not loaded.')
        return

    # Compatibility setting from the historical Windows project, before importing torch.
    os.environ.setdefault('TORCHINDUCTOR_USE_STATIC_CUDA_LAUNCHER', '0')
    sys.path.insert(0, str(a.repo.resolve()))
    import soundfile as sf
    from breeze_infer.runtime import load_runtime, resolve_device, set_all_seeds, update_generation_config_for_breeze
    from breeze_infer.templates import get_template, prepare_inputs, select_template_name
    from models.fast_streaming import FastBreezeStreamingRuntime, FastStreamingConfig

    a.out.mkdir(parents=True, exist_ok=True)
    work.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='breeze-', dir=work) as tmp:
        ref_path = None
        if a.ref:
            audio, rate = sf.read(a.ref, dtype='float32')
            if rate != 24000 or audio.ndim != 1 or audio.size == 0:
                p.error('Prepare a non-empty 24 kHz mono reference WAV first')
            ref_path = Path(tmp) / 'ref.wav'
            sf.write(ref_path, audio, rate, subtype='PCM_16')
        tok, model, atok = load_runtime(a.model.resolve(), device=resolve_device(), attn_implementation='eager')
        update_generation_config_for_breeze(model)
        config = FastStreamingConfig(max_new_tokens=1500, max_seq_len=2048,
                                     fast_all=not a.eager, repetition_penalty=1.1)
        runtime = FastBreezeStreamingRuntime(model, atok, config, tokenizer=tok)
        for line in selected:
            for seed in seeds:
                request = {'id': line['id'], 'text': line['text'], 'speaker': 'S0'}
                if ref_path:
                    request.update(ref_audio_path=str(ref_path), ref_text=ref_text)
                if a.instruction:
                    request['instruction'] = a.instruction
                set_all_seeds(seed)
                inputs = prepare_inputs(tok, atok, model, [request], get_template(select_template_name(request)),
                                        guidance_scale=a.cfg, guidance_scale_ref=None, guidance_scale_ins=None)
                name = f"{line['id']}_s{seed}.wav"
                stage = Path(tmp) / name
                with sf.SoundFile(stage, mode='w', samplerate=runtime.sample_rate, channels=1, subtype='PCM_16') as f:
                    for chunk in runtime.iter_audio_chunks(inputs, request_id=line['id'], seed=seed):
                        f.write(chunk.audio)
                if sf.info(stage).frames == 0:
                    raise RuntimeError('Model returned empty audio; no take published')
                shutil.copyfile(stage, a.out / name)
                print('saved', name, flush=True)


if __name__ == '__main__':
    main()
