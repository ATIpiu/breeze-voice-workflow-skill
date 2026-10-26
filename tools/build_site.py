from pathlib import Path
import base64
import json
import re
import shutil

repo = Path(__file__).resolve().parents[1]
root = repo / 'website'
import subprocess, sys
subprocess.run([sys.executable, str(root / 'build.py')], check=True)
site = repo / 'docs'
base = 'https://atipiu.github.io/breeze-voice-workflow-skill'
prefix = '/breeze-voice-workflow-skill'
article = 'notes/breeze-tts-2-local-guide/index.html'
assets = ['editorial.css','theme.js','app.js','favicon.svg','cover.svg','start-breeze.cmd',
          'breeze-demo.wav','breeze-gentle.wav','breeze-bright.wav',
          'breeze-voice-workflow-20261025.zip','breeze-voice-workflow-skill-20261025.zip']
community_images = [group['file'] for group in json.loads((root / 'content/community.json').read_text(encoding='utf-8'))]
assets += community_images
site.mkdir(exist_ok=True)
(site / 'assets').mkdir(exist_ok=True)

def html_urls(text):
    text = text.replace('https://blog.atipiu.org', base)
    text = re.sub(r'((?:href|src|data-sample-src)=")(/(?!/)[^"]*)(")',
                  lambda m: m[1] + prefix + m[2] + m[3], text)
    return text.replace('</div><p class="skill-note">', '</div><p class="skill-note"><a href="' + prefix + '/breeze-tts-2-local-guide.html" download="breeze-tts-2-local-guide.html">下载独立 HTML</a> · ')

for page in ['archive/index.html', 'about/index.html', 'community/index.html', '404.html', article]:
    target = site / page
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html_urls((root / 'dist' / page).read_text(encoding='utf-8')), encoding='utf-8')
for name in assets:
    (site / 'assets' / name).parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(root / 'assets' / name, site / 'assets' / name)
app = (site / 'assets/app.js').read_text(encoding='utf-8')
app = app.replace("fetch('/search.json')", "fetch('" + prefix + "/search.json')")
(site / 'assets/app.js').write_text(app, encoding='utf-8')
for name in ['feed.xml', 'sitemap.xml', 'robots.txt']:
    (site / name).write_text((root / 'dist' / name).read_text(encoding='utf-8').replace('https://blog.atipiu.org', base), encoding='utf-8')
search = json.loads((root / 'dist/search.json').read_text(encoding='utf-8'))
for item in search:
    item['url'] = prefix + item['url']
(site / 'search.json').write_text(json.dumps(search, ensure_ascii=False), encoding='utf-8')
home = (site / article).read_text(encoding='utf-8')
home = home.replace(base + '/notes/breeze-tts-2-local-guide/', base + '/')
(site / 'index.html').write_text(home, encoding='utf-8')
(site / '.nojekyll').write_text('', encoding='utf-8')

# Single-file export: style, interaction, samples, packages and search index are embedded.
standalone = home
for name in ['favicon.svg','breeze-demo.wav','breeze-gentle.wav','breeze-bright.wav',
             'breeze-voice-workflow-20261025.zip','breeze-voice-workflow-skill-20261025.zip','start-breeze.cmd']:
    kind = 'audio/wav' if name.endswith('.wav') else ('application/zip' if name.endswith('.zip') else ('image/svg+xml' if name.endswith('.svg') else 'application/octet-stream'))
    uri = 'data:' + kind + ';base64,' + base64.b64encode((root / 'assets' / name).read_bytes()).decode()
    if name.endswith(('.zip', '.cmd')):
        standalone = re.sub(r'<a\b[^>]*href="' + re.escape(prefix + '/assets/' + name) + r'(?:\?[^\"]*)?"[^>]*>',
                            lambda m: re.sub(r'\sdownload(?:="[^"]*")?', '', m[0])[:-1] + ' download="' + name + '">', standalone)
    standalone = re.sub(re.escape(prefix + '/assets/' + name) + r'(?:\?[^"\s]*)?', lambda _: uri, standalone)
style = (root / 'assets/editorial.css').read_text(encoding='utf-8')
standalone = re.sub(r'<link rel="stylesheet"[^>]*>', lambda _: '<style>' + style + '</style>', standalone)
for filename in ['theme.js','app.js']:
    code = (root / 'assets' / filename).read_text(encoding='utf-8')
    if filename == 'app.js':
        code = code.replace("if(searchData)return searchData;", "if(searchData)return searchData;const embedded=document.getElementById('offline-search-index');if(embedded){searchData=JSON.parse(embedded.textContent);return searchData;}")
    standalone = re.sub(r'<script(?: defer)? src="[^"]*' + re.escape(filename) + r'[^\"]*"></script>', lambda _: '<script' + (' defer' if filename == 'app.js' else '') + '>' + code.replace('</script', '<\\/script') + '</script>', standalone)
# Inline app must run after its DOM exists; defer does not defer an inline script.
app_match = re.search(r'<script defer>(.*?)</script>', standalone, re.S)
assert app_match
standalone = standalone[:app_match.start()] + standalone[app_match.end():]
embedded = '<script type="application/json" id="offline-search-index">' + json.dumps(search, ensure_ascii=False).replace('<', '\\u003c') + '</script>'
standalone = standalone.replace('</body>', embedded + '<script>' + app_match[1] + '</script></body>')
standalone = re.sub(r'((?:href|src)=")(' + re.escape(prefix) + r'/[^\"]*)(")', lambda m: m[1] + 'https://atipiu.github.io' + m[2] + m[3], standalone)
(repo / 'breeze-tts-2-local-guide.html').write_text(standalone, encoding='utf-8')
(site / 'breeze-tts-2-local-guide.html').write_text(standalone, encoding='utf-8')


print('Built public Pages files and standalone HTML.')
