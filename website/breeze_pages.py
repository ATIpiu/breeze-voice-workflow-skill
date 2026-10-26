"""Build focused reading pages from the maintained Breeze article source."""
from html import escape
from html.parser import HTMLParser
import json
import re

CHAPTERS = [
    ('breeze-tts-2-voicestudio', '图形版安装', 'Win / Mac · VoiceStudio 0.5.7 Beta，未实测', '不想处理命令行，从应用安装、模型下载到第一段声音。', 6),
    ('breeze-tts-2-portable', '便携版安装', 'Windows · NVIDIA 实测，AMD / CPU 未实测', '独立程序，按硬件查看下载、启动和排错步骤。', 8),
    ('breeze-tts-2-voices', '声音与 Prompt', '样音试听 · 11 份片中声音描述', '试听本地样音，复制旁白、角色与情绪的音色 Prompt。', 5),
    ('breeze-tts-2-workflow', '进阶配音与脚本', '原版 PyTorch · 声音克隆与后期', '参考音、逐句生成、加速、排句和混音，以及可下载的 Skill。', 7),
]

class Elements(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.text = text
        self.offsets = [0]
        for line in text.splitlines(keepends=True): self.offsets.append(self.offsets[-1] + len(line))
        self.stack, self.nodes = [], []
        self.feed(text)
    def source_position(self):
        line, column = self.getpos()
        return self.offsets[line - 1] + column
    def handle_starttag(self, tag, attrs):
        node = [tag, dict(attrs), self.source_position(), self.source_position() + len(self.get_starttag_text())]
        self.nodes.append(node)
        if tag not in {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}: self.stack.append(node)
    def handle_startendtag(self, tag, attrs):
        self.nodes.append([tag, dict(attrs), self.source_position(), self.source_position() + len(self.get_starttag_text())])
    def handle_endtag(self, tag):
        for index in range(len(self.stack)-1, -1, -1):
            if self.stack[index][0] == tag:
                self.stack[index][3] = self.text.index('>', self.source_position()) + 1
                del self.stack[index:]
                break
    def find(self, *, ident=None, cls=None):
        for node in self.nodes:
            if (ident is not None and node[1].get('id') == ident) or (cls and cls in node[1].get('class','').split()):
                return self.text[node[2]:node[3]]
        raise ValueError('Missing Breeze source element: ' + str(ident or cls))

def page_url(slug): return '/notes/' + slug + '/'

def expand(post, source):
    tree = Elements(source)
    take = lambda ident: tree.find(ident=ident)
    tabs = tree.find(cls='platform-switch').replace('<span>图形版 / 便携实测</span>', '<span>VoiceStudio 图形版</span>')
    gui = tabs + '<div id="panel-windows" data-platform-panel="windows" data-route-anchor="windows-studio">' + take('windows-studio') + '<!-- offline-portable --></div><div id="panel-mac" data-platform-panel="mac">' + take('mac') + take('mac-help') + '</div>'
    gui = gui.replace('下面的图形版与后面的便携版', '本篇图形版与<a href="/notes/breeze-tts-2-portable/">便携版教程</a>')
    gui = gui.replace('这个安装包不是下面的便携 ZIP', '这里下载的是应用安装包；便携 ZIP 另见便携版教程')
    gui = gui.replace('下方便携教程', '便携版教程')
    gui = gui.replace('Windows 也能直接用 VoiceStudio：装好应用后，在界面中安装 Breeze-TTS-2 和运行时即可，不必先手动搭建 Conda 环境。本篇图形版与<a href="/notes/breeze-tts-2-portable/">便携版教程</a><strong>任选一条</strong>，不用重复安装。', '通过应用安装 Breeze 模型与运行时，无需手动配置 Python 环境。也可选择<a href="/notes/breeze-tts-2-portable/">便携版教程</a>。')
    gui = gui.replace('Mac 推荐 VoiceStudio v0.5.7-beta.2 图形版，属于 0.5.7 系列预发行版。Win / Mac 的 VoiceStudio 可用同一套 audio.cpp 路线；本文另一条 Windows 便携方案的引擎和模型文件则不同。', '适用 Apple Silicon（M 系列芯片）。下方为图形化安装步骤，尚未实测。')
    gui = re.sub(r'<p class="notice">(截至 2026.10.26.*?)</p>', r'<details class="version-note"><summary>版本说明：v0.5.7-beta.2 为预发行版</summary><p>\1</p></details>', gui, count=1)
    portable = '<p class="lede">只看适合自己硬件的步骤。</p>' + tree.find(cls='hardware-switch')
    portable += ''.join(take(ident) for ident in ['hardware-nvidia','hardware-amd','hardware-cpu','generate'])
    portable += '<div data-hardware-only="nvidia">' + take('tested') + '</div>'
    portable += ''.join(take(ident) for ident in ['experience','versions','faq'])
    voices = '<section id="samples"><h2>先听三段本地样音</h2><p class="caption">这是此前生成的测试样音；下面的片中音色包另列原始描述，不将这三段试听冒充片中音色。</p><div class="sample-preview">' + tree.find(cls='voice-sculpture') + '</div></section>' + take('voice-pack')
    voices = voices.replace('<svg class="sample-wave" viewBox="0 0 324 160"', '<svg class="sample-wave" viewBox="0 0 324 160" preserveAspectRatio="none"')
    voices = voices.replace('本页开头的 Skill 下载包', '<a href="/notes/breeze-tts-2-workflow/#skill-download">Skill 下载包</a>')
    workflow = take('skill-download') + '<p class="lede">把声音做成可以剪辑的素材。</p>' + take('clone-workflow')
    workflow = workflow.replace('简洁的 Skill，内含配音、排句和混音脚本，以及旁白、角色与情绪的音色包。按需调用，自由调整参数，无需遵循固定流程。', '按需调用的配音、排句与混音脚本，含音色包。')
    license_note = '<p class="caption">本地模型与自托管输出限研究和非商业用途，商用请核对官方授权。各路线的实测范围已在正文注明。</p>'
    docs = 'https://github.com/debpalash/VoiceStudio/blob/v0.5.7-beta.2/docs/'
    source_blocks = [
        '<section id="sources"><h2>版本与说明</h2><p><a href="'+docs+'install/windows.md">Windows 安装文档</a> · <a href="'+docs+'install/macos.md">Mac 安装文档</a> · <a href="'+docs+'engines/audio-cpp.md">audio.cpp 引擎说明</a></p>'+license_note+'</section>',
        take('sources'),
        '<section id="sources"><h2>音色包与说明</h2><p><a href="https://github.com/ATIpiu/breeze-voice-workflow-skill/blob/main/breeze-voice-workflow/references/voice-pack.md">片中音色包原始记录</a> · <a href="/notes/breeze-tts-2-workflow/">Skill 与生成脚本</a></p>'+license_note+'</section>',
        '<section id="sources"><h2>脚本与说明</h2><p><a href="https://github.com/ATIpiu/breeze-voice-workflow-skill">公开 Skill 与脚本</a> · <a href="https://github.com/breezeblue-ai/breeze-tts">Breeze 原版模型源码</a></p>'+license_note+'</section>'
    ]
    bodies = [gui, portable, voices, workflow]
    pages = []
    for chapter, body, sources in zip(CHAPTERS, bodies, source_blocks):
        slug, label, subtitle, description, minutes = chapter
        pages.append(post | {'slug':slug,'title':'Breeze TTS 2 · ' + label,'subtitle':subtitle,'description':description,'minutes':minutes,'html':body + sources,'chapter':label})
    owners = {}
    for p in pages:
        for ident in re.findall(r'\bid="([^"]+)"', p['html']):
            if ident != 'sources': owners.setdefault(ident, page_url(p['slug']) + '#' + ident)
    owners['official'] = page_url(post['slug']) + '#official'
    owners['sources'] = page_url(pages[0]['slug']) + '#sources'
    cards = ''.join(f'<a class="guide-card" href="{page_url(slug)}"><span class="guide-number">0{i} / 04 <b aria-hidden="true">↗</b></span><h2>{label}</h2><p>{description}</p><small>{subtitle}</small></a>' for i,(slug,label,subtitle,description,_) in enumerate(CHAPTERS,1))
    hub = f'''<div class="guide-hero"><div class="guide-intro"><p class="eyebrow">BREEZE TTS 2 / 使用指南</p><h1>把文字，变成声音。</h1><p>从安装到配音，按你需要的部分开始。</p><div id="skill-download" class="guide-actions"><a href="/assets/breeze-voice-workflow-skill-20261026.zip" download>下载 Skill ↓</a><a href="/breeze-tts-2-local-guide.html" download>完整离线 HTML ↓</a></div></div><section id="official" class="guide-official"><p class="eyebrow">BREEZEBLUE / 官方</p><h2>先体验官方，商用支持正版。</h2><p>官方提供体验额度。初创团队不容易，持续支持和真实反馈，能让产品继续变好。</p><div class="official-entry-actions"><a class="official-primary" href="https://breezeblue.ai/?code=R6T8B7" target="_blank" rel="noopener noreferrer">前往官方体验 <span aria-hidden="true">↗</span></a><a class="official-secondary" href="https://breezeblue.ai/pricing" target="_blank" rel="noopener noreferrer">商用正版方案 ↗</a></div><small>体验额度及商用权益以官网为准；本地模型及自托管输出限研究和非商业用途。</small></section></div><div class="guide-section-heading"><h2>选择你要做的事</h2><span>4 篇指南 · 按需阅读</span></div><div class="guide-grid">{cards}</div><p class="guide-bottom">想一起讨论？<a href="/community/">加入 AI 主题社群 ↗</a></p>'''
    routes = {key:value.lstrip('/') for key,value in owners.items() if key not in {'official','skill-download'}}
    hub += '<script type="application/json" id="legacy-series-routes">' + json.dumps(routes,ensure_ascii=False).replace('<','\\u003c') + '</script>'
    hub_post = post | {'title':'Breeze TTS 2 · 使用指南','subtitle':'按用途选择，轻装开始。','description':'图形版安装、便携版实测、音色 Prompt 与进阶配音，按需阅读。','minutes':1,'html':hub,'hub':True}
    return [hub_post, *pages], owners

def resolve_links(body, owners):
    local = set(re.findall(r'\bid="([^"]+)"', body))
    return re.sub(r'href="#([^\"]+)"', lambda m: 'href="' + owners[m[1]] + '"' if m[1] not in local and m[1] in owners else m[0], body)

def series_nav(current):
    links = '<a href="/notes/breeze-tts-2-local-guide/">总览</a>'
    short_labels = ['图形安装','便携安装','音色 Prompt','配音脚本']
    for (slug,label,_,_,_),short in zip(CHAPTERS,short_labels):
        links += '<a href="' + page_url(slug) + '" aria-label="' + escape(label) + '"' + (' aria-current="page"' if slug == current else '') + '><span class="chapter-label-full">' + escape(label) + '</span><span class="chapter-label-short" aria-hidden="true">' + short + '</span></a>'
    return '<nav class="series-nav" aria-label="Breeze 教程章节">' + links + '</nav>'
