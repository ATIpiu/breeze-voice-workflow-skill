#!/usr/bin/env python3
"""Build ATIPIU's static blog with Python standard library only."""
from pathlib import Path
from html import escape as e
from datetime import datetime
import hashlib
import json
import re
import shutil
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'dist'
SITE=json.loads((ROOT/'site.json').read_text(encoding='utf-8'))
POSTS=sorted(json.loads((ROOT/'content/posts.json').read_text(encoding='utf-8')),key=lambda p:p['date'],reverse=True)
BASE=SITE['url'].rstrip('/')
ASSETS=('editorial.css','theme.js','app.js','favicon.svg','cover.svg','start-breeze.cmd','breeze-demo.wav','breeze-gentle.wav','breeze-bright.wav','breeze-voice-workflow-20261025.zip','breeze-voice-workflow-skill-20261025.zip')
REV=hashlib.sha256(b''.join((ROOT/'assets'/name).read_bytes() for name in ASSETS)).hexdigest()[:12]

def write(path,text):
    target=OUT/path; target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(text,encoding='utf-8')

def url(p): return '/notes/'+p['slug']+'/'

def frame(title,body,path='/',description=None,active='',post=None):
    desc=description or SITE['description']
    links=''.join(f'<a href="{href}"'+(' aria-current="page"' if active==name else '')+f'>{label}</a>' for href,name,label in [('/archive/','archive','文章'),('/about/','about','关于')])
    structured={'@context':'https://schema.org','@type':'BlogPosting' if post else 'WebSite','name':title,'url':BASE+path}
    if post: structured.update(headline=post['title'],datePublished=post['date']+'T09:00:00+08:00',author={'@type':'Person','name':SITE['author']},description=desc)
    ld=json.dumps(structured,ensure_ascii=False).replace('<','\\u003c')
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light dark"><title>{e(title)} · ATIPIU</title><meta name="description" content="{e(desc,quote=True)}"><link rel="canonical" href="{BASE+path}"><meta property="og:type" content="{'article' if post else 'website'}"><meta property="og:title" content="{e(title,quote=True)}"><meta property="og:description" content="{e(desc,quote=True)}"><meta property="og:url" content="{BASE+path}"><meta property="og:image" content="{BASE}/assets/cover.svg"><meta name="twitter:card" content="summary_large_image"><link rel="icon" type="image/svg+xml" href="/assets/favicon.svg"><link rel="alternate" type="application/rss+xml" title="ATIPIU RSS" href="/feed.xml"><link rel="stylesheet" href="/assets/editorial.css?v={REV}"><script src="/assets/theme.js?v={REV}"></script><script defer src="/assets/app.js?v={REV}"></script><script type="application/ld+json">{ld}</script></head><body><a class="skip" href="#main">跳到正文</a><header class="header"><a class="brand" href="/">ATIPIU<span>笔记</span></a><nav aria-label="主导航">{links}<button class="plain-button" type="button" data-open-search aria-label="搜索文章">搜索</button><button class="theme-button" type="button" data-theme-toggle aria-label="切换深色模式" aria-pressed="false"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 14.5A8.5 8.5 0 0 1 9.5 4 8.5 8.5 0 1 0 20 14.5Z"/></svg></button></nav></header>{body}<footer class="footer"><span>© 2026 ATIPIU</span><a href="/feed.xml">RSS</a></footer><dialog id="search-dialog" aria-labelledby="search-title"><form method="dialog"><span id="search-title">搜索文章</span><button class="plain-button" aria-label="关闭搜索">关闭</button></form><label class="sr-only" for="search-input">输入标题或关键词</label><input id="search-input" type="search" placeholder="标题、关键词…" autocomplete="off"><div id="search-results" aria-live="polite"></div></dialog><div id="toast" role="status" aria-live="polite"></div></body></html>'''

def row(p):
    terms=' '.join([p['title'],p['subtitle'],p['description'],p['category'],*p['tags']])
    return f'''<article class="note-row" data-note data-terms="{e(terms,quote=True)}"><div class="meta"><time datetime="{p['date']}">{p['date'].replace('-','.')}</time><span>{e(p['category'])}</span><span>{p['minutes']} 分钟</span></div><h2><a href="{url(p)}">{e(p['title'])}</a></h2><p>{e(p['description'])}</p><a class="read-link" href="{url(p)}">阅读全文 →</a></article>'''

def build():
    OUT.mkdir(exist_ok=True); (OUT/'assets').mkdir(exist_ok=True)
    for name in ASSETS: shutil.copyfile(ROOT/'assets'/name,OUT/'assets'/name)
    rows=''.join(row(p) for p in POSTS)
    write('index.html',frame('笔记',f'<main id="main" class="page"><div class="page-heading"><h1>笔记</h1><p>记录 AI、工具和动手实践。</p></div>{rows}</main>'))
    topics=list(dict.fromkeys(t for p in POSTS for t in [p['category'],*p['tags'][1:]]))
    filters='<div class="filters" role="group" aria-label="按主题筛选"><button data-filter="" aria-pressed="true">全部</button>'+''.join(f'<button data-filter="{e(t,quote=True)}" aria-pressed="false">{e(t)}</button>' for t in topics)+'</div>'
    write('archive/index.html',frame('全部文章',f'<main id="main" class="page"><div class="page-heading"><h1>全部文章 <small>{len(POSTS)}</small></h1></div>{filters}{rows}<p class="empty-message" hidden>暂无文章。</p></main>','/archive/',active='archive'))
    for p in POSTS:
        if not re.fullmatch(r'[a-z0-9-]+',p['slug']): raise ValueError('Invalid slug')
        body=(ROOT/'content'/p['body']).read_text(encoding='utf-8')
        headings=re.findall(r'<section id="([^"]+)"><h2>(.*?)</h2>',body)
        feature=''
        for feature_id,feature_class in [('skill-download','skill-feature'),('official','official-feature')]:
            section=re.search(r'<section id="'+feature_id+r'">.*?</section>',body,re.S)
            if section:
                feature+='<div class="'+feature_class+'">'+section.group(0)+'</div>'
                body=body[:section.start()]+body[section.end():]
        title_markup=re.sub(r'^(.*?) (本地安装指南)$',r'<span class="title-lead">\1</span> <span class="title-tail">\2</span>',e(p['title']))
        toc=''.join(f'<a href="#{anchor}"><span>{n:02d}</span>{title}</a>' for n,(anchor,title) in enumerate(headings,1))
        content=f'''<main id="main" class="page article-page"><a class="back" href="/archive/">← 全部文章</a><header class="post-header"><p class="eyebrow">FIELD NOTES <span> / </span> {e(p['category'])}</p><h1>{title_markup}</h1><p class="subtitle">{e(p['subtitle'])}</p><div class="meta"><time datetime="{p['date']}">{p['date'].replace('-','.')}</time><span>文 / ATIPIU</span><span>{p['minutes']} 分钟阅读</span></div></header>{feature}<div class="article-layout"><aside class="article-rail"><details class="article-toc" open><summary>本篇目录 <span>↗</span></summary><nav aria-label="文章目录">{toc}</nav></details></aside><article class="prose">{body}</article></div><div class="post-bottom"><a href="/archive/">← 全部文章</a><button class="plain-button" type="button" data-share>复制文章链接 ↗</button></div></main>'''
        write('notes/'+p['slug']+'/index.html',frame(p['title'],content,url(p),p['description'],post=p))
    about='''<main id="main" class="page"><div class="page-heading"><h1>关于</h1></div><div class="prose"><p>我是 ATIPIU。这里记录 AI、本地部署和创作工具的使用笔记。</p><p>文章会注明信息来源和验证范围。可以通过 <a href="/feed.xml">RSS</a> 订阅更新。</p></div></main>'''
    write('about/index.html',frame('关于',about,'/about/',active='about'))
    write('404.html',frame('页面不存在','<main id="main" class="page"><div class="page-heading"><h1>页面不存在</h1><p>这个地址没有文章。</p></div><a href="/">返回首页 →</a></main>','/404.html'))
    write('search.json',json.dumps([{k:p[k] for k in ['title','subtitle','description','category','tags','date']}|{'url':url(p)} for p in POSTS],ensure_ascii=False))
    rss=ET.Element('rss',version='2.0'); channel=ET.SubElement(rss,'channel')
    for k,v in [('title','ATIPIU 的笔记'),('link',BASE),('description',SITE['description']),('language','zh-cn')]: ET.SubElement(channel,k).text=v
    for p in POSTS:
        item=ET.SubElement(channel,'item')
        date=datetime.fromisoformat(p['date']+'T01:00:00+00:00').strftime('%a, %d %b %Y %H:%M:%S GMT')
        for k,v in [('title',p['title']),('link',BASE+url(p)),('guid',BASE+url(p)),('description',p['description']),('pubDate',date)]: ET.SubElement(item,k).text=v
    write('feed.xml','<?xml version="1.0" encoding="UTF-8"?>\n'+ET.tostring(rss,encoding='unicode'))
    sitemap=ET.Element('urlset',xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
    for path in ['/','/archive/','/about/',*[url(p) for p in POSTS]]:
        item=ET.SubElement(sitemap,'url'); ET.SubElement(item,'loc').text=BASE+path
    write('sitemap.xml','<?xml version="1.0" encoding="UTF-8"?>\n'+ET.tostring(sitemap,encoding='unicode'))
    write('robots.txt','User-agent: *\nAllow: /\nSitemap: '+BASE+'/sitemap.xml\n')
    print(f'Built {len(POSTS)} post(s) into {OUT}')

if __name__=='__main__': build()
