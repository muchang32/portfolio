(() => {
  'use strict';
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const EMAIL = 'mu.chang32@gmail.com';

  const state = {
    menuOpen: false, careerOpen: false, showTop: false, narrow: false,
    copied: false, lab: null,
    n: { years: 10, mvp: 1, voice: 30, product: 8 }
  };
  const TARGETS = { years: 10, mvp: 1, voice: 30, product: 8 };
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  const derive = () => ({
    menuOpen: state.menuOpen,
    careerOpen: state.careerOpen,
    showTop: state.showTop,
    showLinks: !state.narrow,
    showBurger: state.narrow,
    labOpen: !!state.lab,
    labTitle: state.lab ? state.lab.title : '',
    labDesc: state.lab ? state.lab.desc : '',
    labLink: state.lab ? state.lab.link : '',
    labHref: state.lab ? state.lab.href : '#',
    labTags: state.lab ? state.lab.tags : [],
    careerBtnLabel: state.careerOpen ? '收合早期經歷 ↑' : '展開完整經歷 ↓',
    copyLabel: state.copied ? '已複製 ✓' : '複製 Email',
    nYears: state.n.years, nMvp: state.n.mvp, nVoice: state.n.voice, nProduct: state.n.product
  });

  function render() {
    const v = derive();
    $$('[data-if]').forEach(el => { el.hidden = !v[el.dataset.if]; });
    $$('[data-bind]').forEach(el => {
      const val = v[el.dataset.bind];
      if (val !== undefined) el.textContent = val;
    });
    $$('[data-href-bind]').forEach(el => el.setAttribute('href', v[el.dataset.hrefBind] || '#'));
    const tpl = $('[data-for="labTags"]');
    if (tpl) {
      const host = tpl.parentElement;
      $$('[data-tag-item]', host).forEach(n => n.remove());
      v.labTags.forEach(t => {
        const node = tpl.content.cloneNode(true);
        const el = node.firstElementChild;
        if (!el) return;
        el.setAttribute('data-tag-item', '');
        const slot = el.matches('[data-bind]') ? el : $('[data-bind]', el);
        if (slot) slot.textContent = t;
        host.insertBefore(node, tpl);
      });
    }
    document.body.style.overflow = v.labOpen || (v.menuOpen && state.narrow) ? 'hidden' : '';
  }

  const actions = {
    toggleMenu: () => { state.menuOpen = !state.menuOpen; render(); },
    toggleCareer: () => { state.careerOpen = !state.careerOpen; render(); },
    scrollTop: () => scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' }),
    writingNext: () => scrollWriting(1),
    writingPrev: () => scrollWriting(-1),
    openLab: e => {
      const d = e.currentTarget.dataset;
      state.lab = { title: d.title, desc: d.desc, href: d.href, link: d.link, tags: (d.tags || '').split('|').filter(Boolean) };
      render();
      const close = $('[data-on="closeLab"]');
      if (close) close.focus();
    },
    closeLab: e => {
      if (e && e.target !== e.currentTarget && e.currentTarget.tagName !== 'BUTTON') return;
      state.lab = null; render();
    },
    copyEmail: () => {
      const done = () => { state.copied = true; render(); setTimeout(() => { state.copied = false; render(); }, 1800); };
      if (navigator.clipboard) navigator.clipboard.writeText(EMAIL).then(done, done); else done();
    }
  };

  function scrollWriting(dir) {
    const el = $('[data-ref="writingRef"]');
    if (!el) return;
    const card = el.firstElementChild;
    const step = card ? card.getBoundingClientRect().width + 20 : el.clientWidth * 0.9;
    const max = el.scrollWidth - el.clientWidth;
    let next = el.scrollLeft + dir * step;
    if (dir > 0 && el.scrollLeft >= max - 4) next = 0;          // 循環：尾 → 首
    else if (dir < 0 && el.scrollLeft <= 4) next = max;          // 循環：首 → 尾
    else next = Math.max(0, Math.min(next, max));
    el.scrollTo({ left: next, behavior: reduce ? 'auto' : 'smooth' });
  }

  function measure() {
    const narrow = innerWidth < 1120;
    if (narrow !== state.narrow) {
      state.narrow = narrow;
      if (!narrow) state.menuOpen = false;
      render();
    }
  }

  function markActive() {
    const secs = $$('section[id], div[id]').filter(s => ['about','career','case','ai-lab','writing','design','skills','learning','contact'].includes(s.id));
    let cur = '';
    for (const s of secs) { if (s.getBoundingClientRect().top <= 120) cur = s.id; }
    $$('[data-sec]').forEach(a => a.style.borderBottomColor = a.dataset.sec === cur ? 'currentColor' : 'transparent');
  }

  function countUp() {
    if (reduce) { state.n = { ...TARGETS }; render(); return; }
    const host = $('[data-ref="statsRef"]');
    if (!host) { state.n = { ...TARGETS }; render(); return; }
    let done = false;
    const io = new IntersectionObserver(es => es.forEach(e => {
      if (!e.isIntersecting || done) return;
      done = true;
      Object.keys(TARGETS).forEach(k => { state.n[k] = 0; });
      const t0 = performance.now(), dur = 1100;
      const tick = t => {
        const p = Math.min(1, (t - t0) / dur), e2 = 1 - Math.pow(1 - p, 3);
        Object.keys(TARGETS).forEach(k => { state.n[k] = Math.round(TARGETS[k] * e2); });
        render();
        if (p < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    }), { threshold: 0.35 });
    io.observe(host);
  }

  document.addEventListener('click', e => {
    const t = e.target.closest('[data-on]');
    if (!t) return;
    const fn = actions[t.dataset.on];
    if (!fn) return;
    if (t.tagName !== 'A' || t.getAttribute('href') === '#') e.preventDefault();
    fn({ currentTarget: t, target: e.target });
  });
  document.addEventListener('click', e => {
    const a = e.target.closest('a[href^="#"]:not([data-on])');
    if (a && state.menuOpen) { state.menuOpen = false; render(); }
  });
  addEventListener('keydown', e => {
    if (e.key !== 'Escape') return;
    if (state.lab) { state.lab = null; render(); }
    else if (state.menuOpen) { state.menuOpen = false; render(); }
  });
  addEventListener('resize', measure, { passive: true });
  addEventListener('scroll', () => {
    const st = scrollY || document.documentElement.scrollTop;
    const should = st > innerHeight * 0.8;
    if (should !== state.showTop) { state.showTop = should; render(); }
    markActive();
  }, { passive: true });

  // 標籤收進「點開看詳細」：職涯歷程與精選案例的標籤不顯示在頁面上
  // （AI Lab 的標籤已在 modal 內；學習與認證的證照屬於內容，保留）
  function collapseTagGroups() {
    ['career', 'case'].forEach(id => {
      const sec = document.getElementById(id);
      if (!sec) return;
      $$('div', sec).forEach(d => {
        const pills = [...d.children].filter(k => k.tagName === 'SPAN' && /999px/.test(k.getAttribute('style') || ''));
        if (pills.length < 2) return;
        // 只隱藏膠囊本身，容器內其他元素（例如「閱讀完整案例」連結）保留
        pills.forEach(p => { p.hidden = true; p.setAttribute('data-tag-pill', ''); });
      });
    });
  }

  // ---- 平面作品燈箱 ----
  function initLightbox() {
    const box = document.getElementById('lb');
    const imgs = window.LB_FULL || [];
    if (!box || !imgs.length) return;
    const el = { img: $('#lb-img'), count: $('#lb-count'), prev: $('#lb-prev'), next: $('#lb-next'), close: $('#lb-close') };
    let idx = 0, opener = null;
    const show = i => {
      idx = (i + imgs.length) % imgs.length;
      el.img.src = imgs[idx];
      el.img.alt = '平面設計作品 ' + (idx + 1);
      el.count.textContent = (idx + 1) + ' / ' + imgs.length;
    };
    const open = i => {
      opener = document.activeElement;
      show(i); box.hidden = false;
      document.body.style.overflow = 'hidden';
      el.close.focus();
    };
    const close = () => {
      box.hidden = true; document.body.style.overflow = '';
      if (opener) opener.focus();
    };
    $$('[data-lb]').forEach(b => b.addEventListener('click', () => open(+b.dataset.lb)));
    el.prev.addEventListener('click', () => show(idx - 1));
    el.next.addEventListener('click', () => show(idx + 1));
    el.close.addEventListener('click', close);
    box.addEventListener('click', e => { if (e.target === box) close(); });
    addEventListener('keydown', e => {
      if (box.hidden) return;
      if (e.key === 'Escape') { e.stopPropagation(); close(); }
      else if (e.key === 'ArrowLeft') show(idx - 1);
      else if (e.key === 'ArrowRight') show(idx + 1);
    });
    // 手機左右滑動切換
    let x0 = null;
    box.addEventListener('touchstart', e => { x0 = e.touches[0].clientX; }, { passive: true });
    box.addEventListener('touchend', e => {
      if (x0 === null) return;
      const dx = e.changedTouches[0].clientX - x0;
      if (Math.abs(dx) > 44) show(idx + (dx < 0 ? 1 : -1));
      x0 = null;
    }, { passive: true });
  }

  // 「更多作品」自動填滿最後一列剩下的格子：CSS Grid 算不出剩幾格，這裡用 JS 補
  function fitMoreTile() {
    const grid = $('[data-grid="works"]');
    if (!grid) return;
    const more = $('a[href*="cakeresume"]', grid);
    if (!more) return;
    const cols = getComputedStyle(grid).gridTemplateColumns.split(' ').filter(Boolean).length;
    if (!cols) return;
    const used = $$('[data-lb]', grid)
      .reduce((n, t) => n + (/span 2/.test(t.getAttribute('style') || '') ? 2 : 1), 0);
    const left = (cols - (used % cols)) % cols;
    more.style.gridColumn = 'span ' + (left || cols);
  }

  addEventListener('resize', fitMoreTile, { passive: true });
  initLightbox();
  fitMoreTile();
  collapseTagGroups();
  measure(); render(); countUp(); markActive();
})();
