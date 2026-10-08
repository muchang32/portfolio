(() => {
  'use strict';
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const EMAIL = 'mu.chang32@gmail.com';

  const state = {
    menuOpen: false, careerOpen: false, designOpen: false, showTop: false, narrow: false,
    copied: false, lab: null, labMore: false,
    n: { years: 10, mvp: 1, voice: 30, product: 8 }
  };
  const TARGETS = { years: 10, mvp: 1, voice: 30, product: 8 };
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  const derive = () => ({
    menuOpen: state.menuOpen,
    careerOpen: state.careerOpen,
    designOpen: state.designOpen,
    showTop: state.showTop,
    showLinks: !state.narrow,
    showBurger: state.narrow,
    showLabMore: !state.labMore,
    labOpen: !!state.lab,
    labTitle: state.lab ? state.lab.title : '',
    labDesc: state.lab ? state.lab.desc : '',
    labLink: state.lab ? state.lab.link : '',
    labHref: state.lab ? state.lab.href : '#',
    labHasLink: !!(state.lab && state.lab.href && state.lab.href !== '#'),
    labImg: state.lab && !state.lab.video ? state.lab.img : '',
    labVideo: state.lab ? (state.lab.video || '') : '',
    labVPoster: state.lab ? (state.lab.vposter || '') : '',
    labVCap: state.lab ? (state.lab.vcap || '') : '',
    labHasVCap: !!(state.lab && state.lab.vcap),
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
    // 彈窗封面：沒有截圖的專案不顯示圖片區
    $$('[data-video-bind]').forEach(el => {
      const src = v[el.dataset.videoBind];
      if (src) {
        if (el.getAttribute('src') !== src) {
          el.setAttribute('src', src);
          el.setAttribute('poster', v.labVPoster);
        }
        el.hidden = false;
      } else {
        el.pause();
        el.removeAttribute('src');
        el.removeAttribute('poster');
        el.load();            // 關掉彈窗要停掉下載與播放
        el.hidden = true;
      }
    });
    $$('[data-img-bind]').forEach(el => {
      const src = v[el.dataset.imgBind];
      if (src) { el.setAttribute('src', src); el.hidden = false; }
      else { el.removeAttribute('src'); el.hidden = true; }
    });
    // 複製 Email：成功後短暫改顯示打勾
    $$('[data-copy-idle]').forEach(el => { el.hidden = state.copied; });
    $$('[data-copy-done]').forEach(el => { el.hidden = !state.copied; });
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
    const labGrid = $('[data-lab-grid]');
    if (labGrid) labGrid.toggleAttribute('data-expanded', state.labMore);
    const dBtn = $('[data-on="toggleDesign"]');
    if (dBtn) dBtn.setAttribute('aria-expanded', String(v.designOpen));
    document.body.style.overflow = v.labOpen || (v.menuOpen && state.narrow) ? 'hidden' : '';
  }

  const actions = {
    toggleMenu: () => { state.menuOpen = !state.menuOpen; render(); },
    toggleCareer: () => { state.careerOpen = !state.careerOpen; render(); },
    toggleDesign: () => { state.designOpen = !state.designOpen; render(); },
    toggleLabMore: () => { state.labMore = true; render(); },
    closeDesign: () => { state.designOpen = false; render(); },
    scrollTop: () => scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' }),
    writingNext: () => scrollWriting(1),
    writingPrev: () => scrollWriting(-1),
    openLab: e => {
      const d = e.currentTarget.dataset;
      state.lab = { title: d.title, desc: d.desc, href: d.href, link: d.link,
                   video: d.video, vposter: d.vposter, vcap: d.vcap,
                    img: d.img || '', tags: (d.tags || '').split('|').filter(Boolean) };
      render();
      // 上一次捲到哪裡不該帶到下一張卡
      const box = $('[data-modal-scroll]');
      if (box) box.scrollTop = 0;
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
    // 若實際點到的是真正的連結（例如 modal 內的「開啟網頁」），不要擋掉它的預設行為
    const realLink = e.target.closest('a[href]:not([href="#"])');
    if (!realLink && (t.tagName !== 'A' || t.getAttribute('href') === '#')) e.preventDefault();
    fn({ currentTarget: t, target: e.target });
  });
  document.addEventListener('click', e => {
    if (state.designOpen && !e.target.closest('[data-dropdown]')) { state.designOpen = false; render(); }
  });
  document.addEventListener('click', e => {
    const a = e.target.closest('a[href^="#"]:not([data-on])');
    if (a && state.menuOpen) { state.menuOpen = false; render(); }
  });
  addEventListener('keydown', e => {
    if (e.key !== 'Escape') return;
    if (state.lab) { state.lab = null; render(); }
    else if (state.designOpen) { state.designOpen = false; render(); }
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

  // ---- 轉職鏈：兩顆膠囊輪流亮起 hover 樣式 ----
  // 捲到看得見才開始，每顆 2 秒、共約 8 秒，之後恢復成沒有 hover 的樣子。
  // 使用者一碰膠囊就停手，不跟人搶。
  function arcCue() {
    const row = $('[data-arc]');
    if (!row) return;
    const chips = $$('.tip-link', row);
    if (chips.length < 2) return;

    const clear = () => chips.forEach(c => c.classList.remove('cued'));
    let timer = null, stopped = false;
    const stop = () => { stopped = true; clearTimeout(timer); clear(); };
    chips.forEach(c => ['pointerenter', 'focus'].forEach(ev => c.addEventListener(ev, stop)));

    if (reduce) return;   // 關掉動態效果時就不播

    const SEQ = [0, 1, 0, 1, 0, 1, 0, 1];   // 1 秒一顆，共 8 秒
    let step = 0;
    const run = () => {
      if (stopped) return;
      clear();
      if (step >= SEQ.length) { stopped = true; return; }
      chips[SEQ[step]].classList.add('cued');
      step += 1;
      timer = setTimeout(run, 1000);
    };

    // IntersectionObserver 與 scroll 事件在部分內嵌／預覽環境收不到，
    // 開頭先輪詢 30 秒，之後再交給 scroll 事件。
    let ticks = 0, poll = null;
    const maybeStart = () => {
      if (step > 0 || stopped) return;
      const b = row.getBoundingClientRect();
      if (b.bottom < 80 || b.top > innerHeight - 40) return;
      clearInterval(poll);
      removeEventListener('scroll', maybeStart);
      run();
    };
    poll = setInterval(() => { if (++ticks > 100) clearInterval(poll); maybeStart(); }, 300);
    addEventListener('scroll', maybeStart, { passive: true });
    maybeStart();
  }

  // ---- 手機版的收合元件 ----
  // 桌機不顯示這些按鈕，所以不必判斷斷點；展開狀態以 class 表示
  function initMobileToggles() {
    const about = $('[data-about-toggle]');
    if (about) {
      about.addEventListener('click', () => {
        const open = about.getAttribute('aria-expanded') !== 'true';
        $$('[data-about-more]').forEach(el => el.classList.toggle('open', open));
        about.setAttribute('aria-expanded', String(open));
        about.textContent = open ? '收合 ↑' : '繼續閱讀 ↓';
      });
    }
    // 職涯手風琴：一次只開一張，桌機不受影響（CSS 只在 ≤640px 收合）
    const jobs = $$('[data-job]');
    jobs.forEach(card => {
      const head = $('[data-job-head]', card);
      if (!head) return;
      head.setAttribute('role', 'button');
      head.setAttribute('tabindex', '0');
      head.setAttribute('aria-expanded', 'false');
      const toggle = () => {
        const open = !card.classList.contains('open');
        jobs.forEach(c => {
          c.classList.toggle('open', c === card && open);
          const h = $('[data-job-head]', c);
          if (h) h.setAttribute('aria-expanded', String(c === card && open));
        });
      };
      head.addEventListener('click', toggle);
      head.addEventListener('keydown', e => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(); }
      });
    });
    if (jobs[0]) {
      jobs[0].classList.add('open');
      const h0 = $('[data-job-head]', jobs[0]);
      if (h0) h0.setAttribute('aria-expanded', 'true');
    }

    // What I Do 01–03：一次只開一張，預設全部收合
    const skills = $$('[data-skill-head]');
    skills.forEach(head => {
      head.setAttribute('role', 'button');
      head.setAttribute('tabindex', '0');
      head.setAttribute('aria-expanded', 'false');
      const card = head.closest('[data-skill]');
      const toggle = () => {
        const open = !card.classList.contains('open');
        skills.forEach(h => {
          const c = h.closest('[data-skill]');
          c.classList.toggle('open', c === card && open);
          h.setAttribute('aria-expanded', String(c === card && open));
        });
      };
      head.addEventListener('click', toggle);
      head.addEventListener('keydown', e => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(); }
      });
    });

    // Credentials 頁籤：手機才看得到，桌機四欄照舊
    const tabs = $$('[data-cred-tab]');
    const panels = $$('[data-cred]');
    const pick = key => {
      tabs.forEach(t => t.setAttribute('aria-selected', String(t.dataset.credTab === key)));
      panels.forEach(pn => pn.classList.toggle('active', pn.dataset.cred === key));
    };
    tabs.forEach(t => t.addEventListener('click', () => pick(t.dataset.credTab)));
    if (tabs.length) pick(tabs[0].dataset.credTab);

    const quote = $('[data-quote]');
    const qBtn = quote && $('[data-quote-toggle]', quote);
    if (qBtn) {
      qBtn.addEventListener('click', () => {
        const open = qBtn.getAttribute('aria-expanded') !== 'true';
        quote.classList.toggle('open', open);
        qBtn.setAttribute('aria-expanded', String(open));
        qBtn.setAttribute('aria-label', open ? '收合說明' : '展開說明');
      });
    }
  }

  collapseTagGroups();
  initMobileToggles();
  arcCue();
  measure(); render(); countUp(); markActive();
})();
