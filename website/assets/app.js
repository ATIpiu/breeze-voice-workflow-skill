(() => {
  'use strict';
  const $ = (s, p=document) => p.querySelector(s);
  const $$ = (s, p=document) => [...p.querySelectorAll(s)];
  const legacyRoutes=document.getElementById('legacy-series-routes');
  function followLegacyAnchor(){
    if(!legacyRoutes)return false;
    let key;try{key=decodeURIComponent(location.hash.slice(1));}catch(_){return false;}
    const route=JSON.parse(legacyRoutes.textContent)[key],script=document.querySelector('script[src*="/assets/app.js"]');
    if(!route||!script)return false;
    location.replace(new URL(route,new URL('../',script.src)).href);return true;
  }
  if(followLegacyAnchor())return;
  if(legacyRoutes)window.addEventListener('hashchange',followLegacyAnchor);
  const store = {get(k){try{return localStorage.getItem(k);}catch(_){return null;}},set(k,v){try{localStorage.setItem(k,v);}catch(_){}}};
  let toastTimer;
  function toast(message){const box=$('#toast');box.textContent=message;box.classList.add('visible');clearTimeout(toastTimer);toastTimer=setTimeout(()=>box.classList.remove('visible'),2600);}
  const themeButton=$('[data-theme-toggle]');
  function updateThemeButton(){const dark=document.documentElement.dataset.theme==='dark';themeButton?.setAttribute('aria-pressed',String(dark));themeButton?.setAttribute('aria-label',dark?'切换浅色模式':'切换深色模式');}
  updateThemeButton();
  const community=$('[data-community]');
  if(community){
    let qrPlatform='wechat',qrTopic='all';
    const platformButtons=$$('[data-qr-select]',community),topicButtons=$$('[data-qr-topic]',community);
    function renderGroups(){
      let count=0;
      $$('[data-qr-section]',community).forEach(section=>{
        const topicMatches=qrTopic==='all'||section.dataset.qrSection===qrTopic;
        section.hidden=!topicMatches;
        $$('[data-qr-platform]',section).forEach(card=>{
          card.hidden=card.dataset.qrPlatform!==qrPlatform;
          if(topicMatches&&!card.hidden)count++;
        });
      });
      platformButtons.forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.qrSelect===qrPlatform)));
      topicButtons.forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.qrTopic===qrTopic)));
      $('[data-qr-count]',community).textContent=count+' 个'+(qrPlatform==='wechat'?'微信':'QQ')+'群聊二维码';
      $('[data-qr-expiry]',community).hidden=qrPlatform!=='wechat';
    }
    platformButtons.forEach(button=>button.addEventListener('click',()=>{qrPlatform=button.dataset.qrSelect;renderGroups();}));
    topicButtons.forEach(button=>button.addEventListener('click',()=>{qrTopic=button.dataset.qrTopic;renderGroups();}));
    $('[data-qr-controls]',community).hidden=false;
    renderGroups();
  }
  themeButton?.addEventListener('click',()=>{const next=document.documentElement.dataset.theme==='dark'?'light':'dark';document.documentElement.dataset.theme=next;store.set('atipiu-theme',next);updateThemeButton();});
  async function copy(text,button){try{if(navigator.clipboard?.writeText){await navigator.clipboard.writeText(text);}else{const field=document.createElement('textarea');field.value=text;field.style.position='fixed';field.style.opacity='0';document.body.append(field);field.select();const ok=document.execCommand('copy');field.remove();if(!ok)throw new Error('copy unavailable');}if(button){const original=button.textContent;button.textContent='已复制 ✓';setTimeout(()=>button.textContent=original,1800);}toast('已复制到剪贴板');}catch(_){toast('当前浏览器无法自动复制，请选中文字手动复制。');}}
  $$('[data-copy]').forEach(button=>button.addEventListener('click',()=>{const target=document.getElementById(button.dataset.copy);if(target)copy(target.textContent,button);}));
  $$('[data-share]').forEach(button=>button.addEventListener('click',()=>copy($('link[rel=canonical]')?.href || location.href,button)));
  $$('[data-filter]').forEach(button=>button.addEventListener('click',()=>{$$('[data-filter]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));let found=0;$$('[data-note]').forEach(note=>{const match=!button.dataset.filter || note.dataset.terms.includes(button.dataset.filter);note.hidden=!match;if(match)found++;});const empty=$('.empty-message');if(empty)empty.hidden=found>0;}));
  const dialog=$('#search-dialog'),searchInput=$('#search-input'),results=$('#search-results');let searchData=null,searchLoad=null;
  async function loadSearch(){if(searchData)return searchData;if(!searchLoad)searchLoad=fetch('/search.json').then(r=>{if(!r.ok)throw new Error('Search unavailable');return r.json();}).then(data=>searchData=data).catch(error=>{searchLoad=null;throw error;});return searchLoad;}
  function renderSearch(data){const term=searchInput.value.trim().toLocaleLowerCase();results.replaceChildren();const matches=data.filter(post=>[post.title,post.subtitle,post.description,post.category,...post.tags].join(' ').toLocaleLowerCase().includes(term));if(!matches.length){const p=document.createElement('p');p.textContent='没有找到这条笔记，换个关键词试试。';results.append(p);return;}for(const post of matches){const link=document.createElement('a');link.className='search-result';link.href=post.url;const title=document.createElement('strong');title.textContent=post.title;const text=document.createElement('span');text.textContent=post.subtitle+' · '+post.date;link.append(title,text);results.append(link);}}
  async function refreshSearch(){try{renderSearch(await loadSearch());}catch(_){results.textContent='搜索索引暂时无法加载，可以先到“全部文章”浏览。';}}
  function openSearch(){if(dialog.open)return;dialog.showModal();searchInput.focus();refreshSearch();}
  $$('[data-open-search]').forEach(button=>button.addEventListener('click',openSearch));searchInput?.addEventListener('input',refreshSearch);
  dialog?.addEventListener('click',event=>{if(event.target!==dialog)return;const r=dialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)dialog.close();});
  document.addEventListener('keydown',event=>{if((event.metaKey||event.ctrlKey)&&event.key.toLowerCase()==='k'){event.preventDefault();openSearch();}});

  const article=$('.article-page'),sections=$$('.article-page section');
  let readingMeter,readingFrame,tocCursor;
  const panels=$$('[data-platform-panel]'),tabs=$$('[data-platform]'),switcher=$('.platform-switch');
  const hardwarePanels=$$('[data-hardware-panel]'),hardwareTabs=$$('[data-hardware]'),hardwareSwitcher=$('.hardware-switch');
  const motion=matchMedia('(prefers-reduced-motion: reduce)');
  let panelAnimation,activePlatform='windows',activeHardware='nvidia';
  function hashTarget(){try{return document.getElementById(decodeURIComponent(location.hash.slice(1)));}catch(_){return null;}}
  function hiddenByRoute(element){return !!element?.closest('[data-platform-panel][hidden],[data-hardware-panel][hidden],[data-hardware-only][hidden]');}
  function routeForTarget(target){return {platform:target?.closest('[data-platform-panel]')?.dataset.platformPanel,hardware:target?.closest('[data-hardware-panel]')?.dataset.hardwarePanel||target?.closest('[data-hardware-only]')?.dataset.hardwareOnly};}
  function refreshToc(){let index=0;$$('.article-toc a').forEach(link=>{const target=document.getElementById(link.hash.slice(1));link.hidden=hiddenByRoute(target);if(!link.hidden)$('span',link).textContent=String(++index).padStart(2,'0');else link.removeAttribute('aria-current');});}
  function selectRoute({platform=activePlatform,hardware=activeHardware},{animate=false,updateUrl=false,scrollToPanel=false}={}){
    if(!panels.some(p=>p.dataset.platformPanel===platform))platform='windows';
    if(!hardwarePanels.some(p=>p.dataset.hardwarePanel===hardware))hardware='nvidia';
    const changedPlatform=platform!==activePlatform,changedHardware=hardware!==activeHardware;
    activePlatform=platform;activeHardware=hardware;
    panelAnimation?.cancel();
    panels.forEach(panel=>{panel.hidden=panel.dataset.platformPanel!==platform;panel.setAttribute('role','tabpanel');panel.setAttribute('aria-labelledby','tab-'+panel.dataset.platformPanel);});
    tabs.forEach(tab=>{const active=tab.dataset.platform===platform;tab.setAttribute('aria-selected',String(active));tab.tabIndex=active?0:-1;});
    const platformTabs=$('.platform-tabs');if(platformTabs)platformTabs.dataset.active=platform;
    hardwarePanels.forEach(panel=>{panel.hidden=panel.dataset.hardwarePanel!==hardware;panel.setAttribute('role','tabpanel');panel.setAttribute('aria-labelledby','tab-'+panel.dataset.hardwarePanel);});
    $$('[data-hardware-only]').forEach(block=>block.hidden=block.dataset.hardwareOnly!==hardware);
    hardwareTabs.forEach(tab=>{const active=tab.dataset.hardware===hardware;tab.setAttribute('aria-selected',String(active));tab.tabIndex=active?0:-1;});
    if(hardwareSwitcher){$('.hardware-tabs').dataset.active=hardware;$('.hardware-status').textContent={nvidia:'NVIDIA：Windows 11 / RTX 5090 D 已实测。',amd:'AMD：未实测，按 v0.1.3 文档整理。',cpu:'CPU：运行与编译均未实测，按 v0.1.3 文档整理。'}[hardware];}
    refreshToc();
    store.set('atipiu-platform',platform);
    store.set('atipiu-hardware',hardware);
    if(updateUrl){const panel=panels.find(p=>p.dataset.platformPanel===platform);history.replaceState(null,'','#'+(panel?.dataset.routeAnchor||(platform==='mac'?'mac':{nvidia:'windows',amd:'amd',cpu:'cpu'}[hardware])));}
    const selected=changedPlatform?panels.find(p=>p.dataset.platformPanel===platform):hardwarePanels.find(p=>p.dataset.hardwarePanel===hardware);
    if(animate&&(changedPlatform||changedHardware)&&!motion.matches)panelAnimation=selected?.animate([{opacity:.45,transform:'translateY(7px)'},{opacity:1,transform:'translateY(0)'}],{duration:280,easing:'cubic-bezier(.22,1,.36,1)'});
    if(scrollToPanel&&changedHardware&&hardwareSwitcher?.getBoundingClientRect().top<=16)selected?.scrollIntoView({block:'start',behavior:motion.matches?'instant':'smooth'});
    updateReading();
  }
  if((panels.length&&switcher)||(hardwarePanels.length&&hardwareSwitcher)){
    if(switcher)switcher.hidden=false;
    if(hardwareSwitcher)hardwareSwitcher.hidden=false;
    const fromHash=routeForTarget(hashTarget());
    selectRoute({platform:fromHash.platform||store.get('atipiu-platform')||'windows',hardware:fromHash.hardware||store.get('atipiu-hardware')||'nvidia'});
    function wireTabs(group,activate){group.forEach((tab,index)=>{tab.addEventListener('click',()=>activate(tab));tab.addEventListener('keydown',event=>{let next;if(event.key==='ArrowRight')next=(index+1)%group.length;else if(event.key==='ArrowLeft')next=(index+group.length-1)%group.length;else if(event.key==='Home')next=0;else if(event.key==='End')next=group.length-1;else return;event.preventDefault();group[next].focus();activate(group[next]);});});}
    wireTabs(tabs,tab=>selectRoute({platform:tab.dataset.platform},{animate:true,updateUrl:true}));
    wireTabs(hardwareTabs,tab=>selectRoute({platform:'windows',hardware:tab.dataset.hardware},{animate:true,updateUrl:true,scrollToPanel:true}));
    window.addEventListener('hashchange',()=>{const target=hashTarget();if(hiddenByRoute(target)){selectRoute(routeForTarget(target));target?.scrollIntoView();}});
    // Reveal the platform and hardware before restoring a deep link.
    if(fromHash.platform)requestAnimationFrame(()=>hashTarget()?.scrollIntoView());
  }
  const toc=$('.article-toc'),mobile=matchMedia('(max-width:980px)');
  if(toc){toc.open=!mobile.matches;mobile.addEventListener('change',event=>toc.open=!event.matches);}
  function updateReading(){
    if(!readingMeter||!article)return;
    const bounds=article.getBoundingClientRect(),distance=bounds.height-innerHeight;
    readingMeter.style.transform='scaleX('+Math.max(0,Math.min(1,-bounds.top/Math.max(1,distance)))+')';
    const visible=sections.filter(section=>!hiddenByRoute(section));
    const current=[...visible].reverse().find(section=>section.getBoundingClientRect().top<=160)||visible[0];
    $$('.article-toc a').forEach(link=>{if(current&&link.hash==='#'+current.id){link.setAttribute('aria-current','location');if(tocCursor)tocCursor.style.transform='translateY('+(link.offsetTop+(link.offsetHeight-16)/2)+'px)';}else link.removeAttribute('aria-current');});
  }
  if(article&&sections.length){readingMeter=document.createElement('div');readingMeter.className='reading-meter';readingMeter.setAttribute('aria-hidden','true');document.body.append(readingMeter);if(toc){tocCursor=document.createElement('span');tocCursor.className='toc-cursor';tocCursor.setAttribute('aria-hidden','true');$('nav',toc).append(tocCursor);}const schedule=()=>{if(readingFrame)return;readingFrame=requestAnimationFrame(()=>{readingFrame=null;updateReading();});};window.addEventListener('scroll',schedule,{passive:true});window.addEventListener('resize',schedule,{passive:true});updateReading();}

  const sample=$('#official-sample'),sampleButton=$('[data-sample-play]'),sculpture=$('.voice-sculpture');
  if(sample&&sampleButton&&sculpture){
    let sampleFrame,sampleDuration=6.08;
    const clock=seconds=>'00:'+String(Math.floor(Number.isFinite(seconds)?seconds:0)).padStart(2,'0');
    function paintSample(){const duration=Number.isFinite(sample.duration)?sample.duration:sampleDuration;sculpture.style.setProperty('--playhead',(sample.currentTime/duration*100)+'%');$('[data-sample-time]').textContent=clock(sample.currentTime)+' / '+clock(duration);if(!sample.paused&&!sample.ended)sampleFrame=requestAnimationFrame(paintSample);}
    function syncSample(){cancelAnimationFrame(sampleFrame);const playing=!sample.paused&&!sample.ended;sculpture.dataset.playing=String(playing);sampleButton.setAttribute('aria-label',playing?'暂停本机样音':sample.ended?'重播本机样音':'播放本机样音');paintSample();}
    sample.hidden=true;sampleButton.hidden=false;
    const playError=error=>{if(error.name!=='AbortError')toast('样音暂时无法播放，请稍后重试。');};
    sampleButton.addEventListener('click',()=>{if(sample.paused){if(sample.ended)sample.currentTime=0;sample.play().catch(playError);}else sample.pause();});
    const choices=$('.sample-choices'),voices=$$('[data-sample]');
    if(choices&&voices.length){choices.hidden=false;voices.forEach(button=>button.addEventListener('click',()=>{
      sample.pause();cancelAnimationFrame(sampleFrame);
      const heights=button.dataset.sampleHeights.split(',').map(Number);
      $$('.sample-wave rect').forEach((bar,index)=>{const height=heights[index%heights.length],current=Number(bar.getAttribute('height'))*new DOMMatrix(getComputedStyle(bar).transform).d;bar.getAnimations().forEach(animation=>animation.cancel());bar.setAttribute('y',String(80-height/2));bar.setAttribute('height',String(height));if(!motion.matches)bar.animate([{transform:'scaleY('+current/height+')'},{transform:'scaleY(1)'}],{duration:420,easing:'cubic-bezier(.22,1,.36,1)'});});
      sculpture.dataset.voice=button.dataset.sample;
      voices.forEach(voice=>voice.setAttribute('aria-pressed',String(voice===button)));
      const quote=$('[data-sample-quote]');quote.textContent='“'+button.dataset.sampleText+'”';if(!motion.matches)quote.animate([{opacity:.35},{opacity:1}],{duration:250});
      $('[data-sample-index-label]').textContent=button.dataset.sampleIndex+' / LOCAL SAMPLE';
      const voicePrompt=$('#sample-voice-prompt'),sampleConfig=$('[data-sample-config]');
      if(voicePrompt)voicePrompt.textContent=button.dataset.samplePrompt;
      if(sampleConfig)sampleConfig.textContent='CFG '+button.dataset.sampleCfg+' / Seed '+button.dataset.sampleSeed;
      sampleDuration=Number(button.dataset.sampleDuration);sample.src=button.dataset.sampleSrc;sample.load();syncSample();sample.play().catch(playError);
    }));}
    ['play','pause','ended','loadedmetadata','seeked'].forEach(event=>sample.addEventListener(event,syncSample));
    sample.addEventListener('error',()=>{sampleButton.hidden=true;sample.hidden=false;toast('样音暂时无法加载，请稍后重试。');});
    document.addEventListener('play',event=>{if(event.target instanceof HTMLMediaElement)$$('audio').forEach(audio=>{if(audio!==event.target)audio.pause();});},true);
    syncSample();
  }
  if(!motion.matches&&!document.querySelector('.chapter-page')&&'IntersectionObserver' in window){
    const reveal=new IntersectionObserver(entries=>{for(const entry of entries){if(!entry.isIntersecting)continue;const element=entry.target;reveal.unobserve(element);element.animate([{opacity:.45,transform:'translateY(14px)'},{opacity:1,transform:'translateY(0)'}],{duration:550,easing:'cubic-bezier(.22,1,.36,1)'});if(element.classList.contains('voice-sculpture'))$$('.wave-base rect',element).forEach((bar,index)=>bar.animate([{transform:'scaleY(.12)'},{transform:'scaleY(1)'}],{duration:600,delay:index*5,easing:'cubic-bezier(.22,1,.36,1)'}));}},{threshold:.15});
    $$('.official-copy,.voice-sculpture,.prose .step-heading,.prose section > h2').forEach(element=>reveal.observe(element));
  }
})();
