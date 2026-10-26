import Lenis from 'lenis';

const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const root = document.documentElement;
root.classList.add('fx');

// Smooth, inertial scrolling; native scrolling stays inside dialogs, menus and wide tables/code.
let lenis = null;
if (!reduce) {
  lenis = new Lenis({
    lerp: 0.1,
    anchors: { offset: -100 },
    prevent: node => !!node.closest?.('dialog, .article-toc nav, pre, .table-wrap, [data-lenis-prevent]'),
  });
  const raf = time => { lenis.raf(time); requestAnimationFrame(raf); };
  requestAnimationFrame(raf);
  // The search dialog should freeze the page behind it.
  const dialog = document.getElementById('search-dialog');
  if (dialog) new MutationObserver(() => (dialog.open ? lenis.stop() : lenis.start())).observe(dialog, { attributes: true, attributeFilter: ['open'] });
}

// Reveal on scroll. Legacy guide pages get the same treatment for their cards.
const targets = document.querySelectorAll('[data-reveal], .guide-grid > *, .qr-card, .note-row, .chapter-heading, .guide-hero > *');
if (reduce || !('IntersectionObserver' in window)) targets.forEach(el => el.classList.add('in'));
else {
  const io = new IntersectionObserver(entries => {
    let delay = 0;
    for (const e of entries) {
      if (!e.isIntersecting) continue;
      e.target.style.transitionDelay = delay + 'ms';
      delay += 70;
      e.target.classList.add('in');
      io.unobserve(e.target);
    }
  }, { rootMargin: '0px 0px -8% 0px' });
  targets.forEach(el => { el.classList.add('reveal'); io.observe(el); });
}

// Pointer spotlight on cards.
document.querySelectorAll('[data-spotlight], .guide-grid > a').forEach(card => {
  card.classList.add('spot');
  card.addEventListener('pointermove', e => {
    const r = card.getBoundingClientRect();
    card.style.setProperty('--mx', e.clientX - r.left + 'px');
    card.style.setProperty('--my', e.clientY - r.top + 'px');
    if (!reduce && card.matches('[data-spotlight]')) {
      const rx = ((e.clientY - r.top) / r.height - 0.5) * -4, ry = ((e.clientX - r.left) / r.width - 0.5) * 6;
      card.style.setProperty('--rx', rx + 'deg'); card.style.setProperty('--ry', ry + 'deg');
    }
  });
  card.addEventListener('pointerleave', () => { card.style.setProperty('--rx', '0deg'); card.style.setProperty('--ry', '0deg'); });
});

// Header glass + reading progress.
const header = document.querySelector('[data-header]');
const bar = document.querySelector('.read-progress i');
const reading = !!document.querySelector('.article-page');
if (!reading) bar?.parentElement.remove();
const onScroll = () => {
  const y = scrollY;
  header?.classList.toggle('scrolled', y > 8);
  if (reading && bar) bar.style.transform = `scaleX(${Math.min(1, y / Math.max(1, document.documentElement.scrollHeight - innerHeight))})`;
};
onScroll();
(lenis ? lenis.on.bind(lenis, 'scroll') : cb => addEventListener('scroll', cb, { passive: true }))(onScroll);
