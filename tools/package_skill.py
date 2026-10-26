"""Package the current skill without rewriting its sources."""
import argparse
from datetime import date
import hashlib
from pathlib import Path
import zipfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--date', type=date.fromisoformat, required=True)
args = parser.parse_args()
repo = Path(__file__).resolve().parents[1]
skill = repo / 'breeze-voice-workflow'
files = sorted(p for p in skill.rglob('*') if p.is_file()
               and p.name != 'SHA256SUMS.txt' and p.suffix != '.pyc'
               and '__pycache__' not in p.parts)
manifest = skill / 'SHA256SUMS.txt'
def payload(path):
    data = path.read_bytes()
    return data.replace(b'\r\n', b'\n') if path.suffix in {'.md', '.txt', '.py', '.json', '.yaml', '.yml'} else data

manifest.write_text(''.join(hashlib.sha256(payload(p)).hexdigest() + '  '
                           + p.relative_to(skill).as_posix() + '\n' for p in files),
                    encoding='utf-8', newline='\n')
archive = repo / 'website/assets' / ('breeze-voice-workflow-skill-' + args.date.strftime('%Y%m%d') + '.zip')
with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as output:
    for path in sorted([*files, manifest]):
        info = zipfile.ZipInfo('breeze-voice-workflow/' + path.relative_to(skill).as_posix(),
                               date_time=(args.date.year, args.date.month, args.date.day, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        output.writestr(info, payload(path))
with zipfile.ZipFile(archive) as output:
    assert output.testzip() is None
    for line in output.read('breeze-voice-workflow/SHA256SUMS.txt').decode().splitlines():
        digest, name = line.split('  ', 1)
        assert hashlib.sha256(output.read('breeze-voice-workflow/' + name)).hexdigest() == digest
print(archive.name, hashlib.sha256(archive.read_bytes()).hexdigest())
