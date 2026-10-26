import { useEffect, useState } from 'react';

const STATES = { online: '在线', awaiting: '等待首次采集', stale: '连接延迟', error: '连接异常', disabled: '未启用' };
const MODES = { demo: '测试模式', production: '正式运行' };
const ago = s => (s < 60 ? `${s} 秒前` : s < 3600 ? `${Math.floor(s / 60)} 分钟前` : `${Math.floor(s / 3600)} 小时前`);

// Reads the subscribe site's public status endpoint (same origin, under /codex-reset/).
export function useCodexStatus() {
  const [status, setStatus] = useState(null);
  const [now, setNow] = useState(Date.now());
  useEffect(() => {
    let dead = false;
    const load = () => fetch('https://blog.atipiu.org/codex-reset/api/status', { headers: { Accept: 'application/json' }, credentials:'omit' })
      .then(r => (r.ok ? r.json() : Promise.reject()))
      .then(s => !dead && setStatus(s))
      .catch(() => !dead && setStatus(false));
    load();
    const poll = setInterval(load, 30000), tick = setInterval(() => setNow(Date.now()), 1000);
    return () => { dead = true; clearInterval(poll); clearInterval(tick); };
  }, []);
  return { status, now };
}

export function StatusChip() {
  const { status } = useCodexStatus();
  const state = status ? status.sourceConnection : status === false ? 'offline' : 'loading';
  const label = status ? STATES[state] || state : status === false ? '状态暂不可用' : '读取中…';
  return <span className={'rw-chip rw-' + state}><i />{label}</span>;
}

export default function CodexStatus() {
  const { status, now } = useCodexStatus();
  const state = status ? status.sourceConnection : 'unknown';
  const rows = [
    ['采集连接', status ? STATES[state] || state : status === false ? '暂不可用' : '读取中…'],
    ['上次检查', status ? (status.lastSourceSuccess ? ago(Math.max(0, Math.round((now - status.lastSourceSuccess) / 1000))) : '暂无') : '—'],
    ['检查间隔', status ? `每 ${status.pollSeconds} 秒` : '—'],
    ['已识别重置', status ? `${status.resetsDetected ?? 0} 次` : '—'],
  ];
  return (
    <div className="codex-hero-card" data-reveal>
      <div className="codex-hero-copy">
        <p className="eyebrow">PROJECT / CODEX RESET WATCH</p>
        <p className="codex-hero-lead">额度重置那一刻，<br />你的邮箱<em>先知道</em>。</p>
        <p>免费邮件订阅：盯着 <a href="https://x.com/thsottiaux" target="_blank" rel="noopener noreferrer">@thsottiaux</a> 的推文，确认是 Codex 额度重置，才发一封邮件提醒你。</p>
        <div className="codex-actions">
          <a className="codex-primary" href="https://blog.atipiu.org/codex-reset/" data-astro-prefetch="false">免费订阅 <span aria-hidden="true">↗</span></a>
          <a className="codex-secondary" href="#how">先看看怎么运作</a>
        </div>
      </div>
      <div className={'codex-status rw-' + state} aria-live="polite">
        <div className="codex-radar" aria-hidden="true"><i /><b /><b /><b /><span /></div>
        <dl>{rows.map(([k, v]) => <div key={k}><dt>{k}</dt><dd>{v}</dd></div>)}</dl>
        <p className="codex-status-note">{status ? `实时读取订阅站的公开状态 · ${MODES[status.mode] || status.mode}` : status === false ? '暂时连不上订阅站，稍后会自动重试。' : '正在连接订阅站…'}</p>
      </div>
    </div>
  );
}
