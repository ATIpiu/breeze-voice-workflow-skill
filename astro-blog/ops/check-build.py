"""Check generated local navigation, fragments, metadata, and feeds."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json
import re
import xml.etree.ElementTree as ET
import sys

root=Path(__file__).resolve().parents[1]/('dist-pages' if '--pages' in sys.argv else 'dist')
prefix='/breeze-voice-workflow-skill' if '--pages' in sys.argv else ''
def local_path(value):
    if prefix and value==prefix:return '/'
    return value[len(prefix):] if prefix and value.startswith(prefix+'/') else value
class Parser(HTMLParser):
    def __init__(self): super().__init__(); self.ids=set(); self.refs=[]; self.h1=0; self.title=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:
            assert a['id'] not in self.ids, f'Duplicate id {a["id"]}'
            self.ids.add(a['id'])
        if tag=='h1': self.h1+=1
        if tag=='title': self.title=True
        for key in ['href','src']:
            if a.get(key): self.refs.append(a[key])
pages={}
for path in root.rglob('*.html'):
    parser=Parser(); parser.feed(path.read_text(encoding='utf-8')); pages[path]=parser
    assert parser.h1==1 and parser.title, f'Missing page title or one h1: {path}'
for page,p in pages.items():
    for ref in p.refs:
        parsed=urlsplit(ref)
        if parsed.scheme or parsed.netloc: continue
        path=local_path(unquote(parsed.path))
        if path.startswith('/codex-reset/'): continue  # served by the Codex Reset Watch app, not this build
        target=(root/path.lstrip('/')) if path.startswith('/') else page.parent/path
        if not path: target=page
        if target.is_dir(): target=target/'index.html'
        assert target.is_file(), f'Broken local URL {ref} in {page}'
        if parsed.fragment and target in pages:
            assert unquote(parsed.fragment) in pages[target].ids, f'Missing fragment {ref} in {page}'
ET.parse(root/'feed.xml'); ET.parse(root/'sitemap.xml')
assert len(json.loads((root/'search.json').read_text(encoding='utf-8')))>0
hub=(root/'notes/breeze-tts-2-local-guide/index.html').read_text(encoding='utf-8')
legacy=re.search(r'<script type="application/json" id="legacy-series-routes">(.*?)</script>',hub,re.S)
if legacy:
    routes=json.loads(legacy[1])
    for anchor,route in routes.items():
        parsed=urlsplit(route)
        target=root/local_path(parsed.path).lstrip('/')/'index.html'
        assert target in pages and parsed.fragment in pages[target].ids, f'Broken legacy anchor {anchor}: {route}'
    for anchor in ['mac','windows-studio','windows','amd','cpu','voice-pack','clone-workflow']:
        assert anchor in routes, f'Missing previously shared anchor {anchor}'
    print(f'PASS: {len(routes)} legacy anchors resolve to published pages.')
print(f'PASS: {len(pages)} HTML pages, internal links and fragments, RSS, sitemap, search index.')
home=(root/'index.html').read_text(encoding='utf-8')
assert 'https://blog.atipiu.org/codex-reset/' in home
if prefix: assert not re.search(r'(?:href|src)="/(?!breeze-voice-workflow-skill/|/)',home)
else: assert '/breeze-voice-workflow-skill/' not in home
assert all(item['url'].startswith(prefix+'/') for item in json.loads((root/'search.json').read_text(encoding='utf-8')))
assert '<link rel="canonical" href="https://blog.atipiu.org/"' in home
print('PASS: Hosting paths, canonical domain and live service links.')
