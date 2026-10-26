from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,re,xml.etree.ElementTree as ET

root=Path(__file__).resolve().parents[1]/'docs'
prefix='/breeze-voice-workflow-skill'
service='https://blog.atipiu.org/codex-reset/'
class Page(HTMLParser):
    def __init__(self,text):
        super().__init__();self.ids=set();self.refs=[];self.h1=0;self.feed(text)
    def handle_starttag(self,tag,attrs):
        values=dict(attrs)
        if values.get('id'):
            assert values['id'] not in self.ids,'Duplicate id';self.ids.add(values['id'])
        self.h1+=tag=='h1'
        for attr in ['href','src']:
            if values.get(attr):self.refs.append(values[attr])
pages={p:Page(p.read_text(encoding='utf-8')) for p in root.rglob('*.html')}
for path,page in pages.items():
    assert page.h1==1,str(path)
    for ref in page.refs:
        parsed=urlsplit(ref)
        if parsed.scheme or parsed.netloc:continue
        route=unquote(parsed.path)
        if route.startswith(prefix+'/'):route=route[len(prefix):]
        target=root/route.lstrip('/') if route.startswith('/') else path.parent/route
        if not route:target=path
        if target.is_dir():target=target/'index.html'
        assert target.is_file(),f'Broken URL {ref} in {path}'
        if parsed.fragment and target in pages:assert unquote(parsed.fragment) in pages[target].ids,f'Broken anchor {ref}'
home=(root/'index.html').read_text(encoding='utf-8')
assert service in pages[root/'index.html'].refs and 'Codex 重置提醒' in home
assert service in pages[root/'archive/index.html'].refs
assert not any('github.io/breeze-voice-workflow-skill/codex-reset' in p.read_text(encoding='utf-8') for p in pages)
search=json.loads((root/'search.json').read_text(encoding='utf-8'))
assert next(p for p in search if 'Codex' in p['title'])['url']==service
feed=ET.parse(root/'feed.xml');assert any(item.findtext('link')==service for item in feed.findall('./channel/item'))
ET.parse(root/'sitemap.xml')
offline=(root/'atipiu-blog.html').read_text(encoding='utf-8')
assert 'id="offline-search-index"' in offline and service in offline
assert not re.search(r'<(?:script[^>]+src|link[^>]+rel="stylesheet")',offline)
print(f'PASS: {len(pages)} pages, navigation, feeds, live service URLs and standalone homepage.')
