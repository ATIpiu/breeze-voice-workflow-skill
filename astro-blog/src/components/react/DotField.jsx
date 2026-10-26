import { useEffect, useRef } from 'react';

// A quiet dot matrix that swells into ripples around the pointer and breathes on its own.
export default function DotField() {
  const ref = useRef(null);
  useEffect(() => {
    const canvas = ref.current, ctx = canvas.getContext('2d');
    const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
    let w = 0, h = 0, dpr = 1, raf = 0, visible = true, t = 0;
    const pointer = { x: -9999, y: -9999, tx: -9999, ty: -9999 };
    const ripples = [];
    let colors = {};
    const readColors = () => {
      const cs = getComputedStyle(document.documentElement);
      colors = { ink: cs.getPropertyValue('--ink').trim() || '#242424', accent: cs.getPropertyValue('--accent').trim() || '#b34d36' };
    };
    const resize = () => {
      const r = canvas.getBoundingClientRect();
      dpr = Math.min(devicePixelRatio || 1, 2); w = r.width; h = r.height;
      canvas.width = w * dpr; canvas.height = h * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    const move = e => { const r = canvas.getBoundingClientRect(); pointer.tx = e.clientX - r.left; pointer.ty = e.clientY - r.top; };
    const leave = () => { pointer.tx = pointer.ty = -9999; };
    const click = e => { const r = canvas.getBoundingClientRect(); const x = e.clientX - r.left, y = e.clientY - r.top; if (y >= 0 && y <= h) ripples.push({ x, y, born: t }); };
    const draw = () => {
      ctx.clearRect(0, 0, w, h);
      pointer.x += (pointer.tx - pointer.x) * 0.12; pointer.y += (pointer.ty - pointer.y) * 0.12;
      const gap = w < 600 ? 22 : 26;
      for (let y = gap / 2; y < h; y += gap) for (let x = gap / 2; x < w; x += gap) {
        const dx = x - pointer.x, dy = y - pointer.y, d = Math.hypot(dx, dy);
        let s = 0.9 + 0.35 * Math.sin(x * 0.02 + y * 0.015 + t * 1.2);
        let a = 0.16, hot = 0;
        if (d < 160) { const k = 1 - d / 160; s += k * 2.6; a += k * 0.55; hot = k; }
        for (const rp of ripples) { const age = t - rp.born, rr = age * 420, dd = Math.abs(Math.hypot(x - rp.x, y - rp.y) - rr); if (dd < 30) { const k = (1 - dd / 30) * Math.max(0, 1 - age / 1.6); s += k * 3; a += k * 0.6; hot = Math.max(hot, k); } }
        const push = d < 160 ? (1 - d / 160) * 8 : 0;
        ctx.globalAlpha = Math.min(1, a);
        ctx.fillStyle = hot > 0.35 ? colors.accent : colors.ink;
        ctx.beginPath(); ctx.arc(x + (d ? (dx / d) * push : 0), y + (d ? (dy / d) * push : 0), s, 0, 6.283); ctx.fill();
      }
      ctx.globalAlpha = 1;
      while (ripples.length && t - ripples[0].born > 1.6) ripples.shift();
    };
    let last = performance.now();
    const loop = now => { raf = requestAnimationFrame(loop); if (!visible) { last = now; return; } t += Math.min((now - last) / 1000, 0.05); last = now; draw(); };
    readColors(); resize();
    if (reduce) draw(); else raf = requestAnimationFrame(loop);
    const io = new IntersectionObserver(([e]) => { visible = e.isIntersecting; }); io.observe(canvas);
    const mo = new MutationObserver(() => { readColors(); if (reduce) draw(); }); mo.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
    window.addEventListener('resize', resize); window.addEventListener('pointermove', move, { passive: true });
    document.addEventListener('pointerleave', leave); window.addEventListener('pointerdown', click);
    return () => { cancelAnimationFrame(raf); io.disconnect(); mo.disconnect(); window.removeEventListener('resize', resize); window.removeEventListener('pointermove', move); document.removeEventListener('pointerleave', leave); window.removeEventListener('pointerdown', click); };
  }, []);
  return <canvas className="dot-field" ref={ref} aria-hidden="true" />;
}
