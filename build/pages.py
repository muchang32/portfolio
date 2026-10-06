#!/usr/bin/env python3
"""把 writing/*.md 與兩則案例 md 轉成與首頁同調性的內頁。"""
import re, pathlib, html

ROOT = pathlib.Path('.')
PAL = dict(bg='#FAF7F0', ink='#14110F', card='#FFFFFF', accent='#FFD34E',
           violet='#6D4AFF', soft='#FFF6D9', line='#14110F')

_PLAY = ('<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
         '<path d="M7 4.5v15l13-7.5z"/></svg>')
_PAUSE = ('<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
          '<rect x="6" y="4.5" width="4" height="15" rx="1.3"/>'
          '<rect x="14" y="4.5" width="4" height="15" rx="1.3"/></svg>')

CASE_CSS = """
.kicker{{display:inline-block;font-family:'IBM Plex Mono',monospace;font-size:11.5px;
 letter-spacing:.14em;background:{ink};color:{bg};padding:6px 14px;border-radius:999px;
 margin:0 0 18px}}
h2 span{{box-shadow:inset 0 -.34em 0 {accent}}}
h3{{padding-left:13px;border-left:4px solid {accent}}}
/* 摘要：無框，左邊一條亮黃直條 */
blockquote.summary{{margin:0 0 26px;padding:4px 0 4px 22px;border-left:0;position:relative;
 font-size:16px;color:#2C2620}}
blockquote.summary::before{{content:'';position:absolute;left:0;top:2px;bottom:2px;width:7px;
 background:{accent};border-radius:3px}}
/* 其餘引言維持首頁那種卡片 */
blockquote:not(.summary){{margin:30px 0;padding:clamp(20px,2.6vw,28px);background:{soft};
 border:2px solid {ink};border-radius:20px;box-shadow:5px 5px 0 {ink};color:#2C2620}}
/* 角色／類型：白底圓角框加陰影 */
dl.meta{{display:grid;grid-template-columns:auto 1fr;gap:9px 18px;margin:0 0 34px;
 padding:clamp(20px,2.4vw,26px);background:{card};border:2px solid {ink};border-radius:20px;
 box-shadow:5px 5px 0 {ink}}}
dl.meta dt{{font-family:'IBM Plex Mono',monospace;font-size:12px;letter-spacing:.1em;
 color:#6E6A85;white-space:nowrap;padding-top:4px}}
dl.meta dd{{margin:0;font-size:15px;line-height:1.75}}
@media (max-width:480px){{dl.meta{{grid-template-columns:1fr;gap:3px 0}}
 dl.meta dd{{margin-bottom:10px}}}}
th{{background:{accent};font-weight:700;border-bottom:2px solid {ink}}}
table{{border:2px solid {ink};border-radius:14px;overflow:hidden;border-collapse:separate;
 border-spacing:0}}
td{{border-bottom:1px solid rgba(20,17,15,.12)}}
tbody tr:last-child td{{border-bottom:0}}
main ul{{list-style:none;padding-left:0}}
main ul li{{position:relative;padding-left:24px}}
main ul li::before{{content:'';position:absolute;left:3px;top:.62em;width:9px;height:9px;
 background:{accent};border:1.5px solid {ink};border-radius:3px}}
/* YouTube 嵌入維持 16:9 */
.yt{{position:relative;width:100%;aspect-ratio:16/9;margin:32px 0;border-radius:14px;
 overflow:hidden;background:{ink}}}
.yt iframe{{position:absolute;inset:0;width:100%;height:100%;border:0}}
.yt-poster{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block}}
/* 擋住播放器本身的點擊，控制權只留給下面那顆按鈕 */
.yt-shield{{position:absolute;inset:0;cursor:default}}
/* 還沒播放時按鈕置中當主要入口，播放後縮到左下角當控制鍵 */
.yt-btn{{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);z-index:2;
 width:72px;height:72px;border-radius:50%;
 border:2.5px solid {ink};background:{accent};color:{ink};cursor:pointer;display:grid;
 place-items:center;padding:0;box-shadow:3px 3px 0 {ink};
 transition:transform .15s ease,box-shadow .15s ease}}
.yt-btn:hover{{transform:translate(-50%,-50%) scale(1.08)}}
.yt[data-playing] .yt-btn{{left:14px;top:auto;bottom:14px;transform:none;width:46px;height:46px}}
.yt-btn svg{{width:30px;height:30px}}
.yt[data-playing] .yt-btn svg{{width:20px;height:20px}}
.yt[data-playing] .yt-btn:hover{{transform:translate(-2px,-2px);box-shadow:5px 5px 0 {ink}}}
"""

CASE_JS = """<script>
(function () {
  document.querySelectorAll('.yt').forEach(function (box) {
    var btn = box.querySelector('[data-yt-toggle]');
    var vid = box.getAttribute('data-yt');
    if (!btn || !vid) return;
    var frame = null, playing = false;
    var paint = function () {
      box.querySelector('[data-yt-play]').hidden = playing;
      box.querySelector('[data-yt-pause]').hidden = !playing;
      btn.setAttribute('aria-label', playing ? '暫停' : '播放');
    };
    var send = function (fn) {
      if (!frame) return;
      frame.contentWindow.postMessage(
        JSON.stringify({ event: 'command', func: fn, args: [] }), '*');
    };
    btn.addEventListener('click', function () {
      if (!frame) {
        // 使用者點了才載入，所以可以帶聲音自動播放
        frame = document.createElement('iframe');
        frame.src = 'https://www.youtube-nocookie.com/embed/' + vid +
          '?autoplay=1&controls=0&disablekb=1&playsinline=1&rel=0&enablejsapi=1';
        frame.title = 'YouTube';
        frame.allow = 'autoplay; encrypted-media; picture-in-picture';
        box.insertBefore(frame, btn);
        var shield = document.createElement('span');
        shield.className = 'yt-shield';
        shield.addEventListener('click', function () { btn.click(); });
        box.insertBefore(shield, btn);
        var poster = box.querySelector('.yt-poster');
        if (poster) poster.remove();
        box.setAttribute('data-playing', '');
        playing = true; paint();
        return;
      }
      playing = !playing;
      send(playing ? 'playVideo' : 'pauseVideo');
      paint();
    });
  });
})();
</script>
"""

def md2html(md, depth):
    up = '../' * depth
    out, lines, i = [], md.split('\n'), 0
    def inline(t):
        t = html.escape(t)
        t = re.sub(r'!\[\]\((?:\.\./)*([^)]+)\)', lambda m: f'<img src="{up}{m.group(1)}" alt="" loading="lazy" />', t)
        # 站外連結另開分頁；rel="noopener" 不能省
        def _link(m):
            href, text = m.group(2), m.group(1)
            ext = ' target="_blank" rel="noopener"' if href.startswith('http') else ''
            return f'<a href="{href}"{ext}>{text}</a>'
        t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', _link, t)
        t = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', t)
        t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
        t = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', t)
        return t
    while i < len(lines):
        ln = lines[i]
        # 只有開頭第一塊可以變成規格表，避免內文的粗體被誤判
        if len(out) <= 1 and re.match(r'^\*\*[^*]+\*\*\u3000', ln):
            rows = []
            while i < len(lines) and re.match(r'^\*\*[^*]+\*\*\u3000', lines[i]):
                mm = re.match(r'^\*\*([^*]+)\*\*\u3000(.+)$', lines[i])
                rows.append((mm.group(1), mm.group(2))); i += 1
            out.append('<dl class="meta">' + ''.join(
                f'<dt>{inline(k)}</dt><dd>{inline(v)}</dd>' for k, v in rows) + '</dl>')
            continue
        my = re.match(r'^!youtube\[([^\]]*)\]\(([^)]+)\)$', ln.strip())
        if my:
            poster, url = my.group(1), my.group(2)
            vid = url.rsplit('/', 1)[-1].split('?')[0]
            # 先放自家封面，點了才載入 iframe：未播放時畫面上沒有 YouTube 的
            # 標題列、浮水印與紅色播放鍵，也省下第三方請求
            out.append(
                f'<div class="yt" data-yt="{vid}">'
                f'<img class="yt-poster" src="{up}{poster}" alt="" loading="lazy" decoding="async" />'
                f'<button type="button" class="yt-btn" data-yt-toggle aria-label="播放">'
                f'<span data-yt-play>{_PLAY}</span>'
                f'<span data-yt-pause hidden>{_PAUSE}</span>'
                f'</button></div>'); i += 1; continue
        mv = re.match(r'^!video\[([^\]]*)\]\(([^)]+)\)$', ln.strip())
        if mv:
            poster, src = mv.group(1), mv.group(2)
            # 螢幕錄影無聲，preload=metadata 讓手機不要一進頁就抓整支
            out.append(f'<figure><video src="{up}{src}" poster="{up}{poster}" controls '
                       f'preload="metadata" playsinline></video></figure>'); i += 1; continue
        if re.match(r'^!\[\]\(', ln.strip()):
            out.append('<figure>' + inline(ln.strip()) + '</figure>'); i += 1; continue
        if ln.startswith('```'):
            buf = []; i += 1
            while i < len(lines) and not lines[i].startswith('```'): buf.append(lines[i]); i += 1
            i += 1; out.append('<pre><code>' + html.escape('\n'.join(buf)) + '</code></pre>'); continue
        if ln.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')]); i += 1
            body_rows = [r for r in rows[1:] if not all(set(c) <= set('-: ') for c in r)]
            th = ''.join(f'<th>{inline(c)}</th>' for c in rows[0])
            tb = ''.join('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>' for r in body_rows)
            out.append(f'<div class="tw"><table><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table></div>'); continue
        m = re.match(r'^(#{1,4}) (.+)', ln)
        if m:
            lvl = len(m.group(1)); txt = inline(m.group(2))
            # h2 的黃色標示只能蓋在文字上，所以包一層 inline 的 span
            inner = f'<span>{txt}</span>' if lvl == 2 else txt
            out.append(f'<h{lvl}>{inner}</h{lvl}>'); i += 1; continue
        if ln.startswith('> '):
            buf = []
            while i < len(lines) and lines[i].startswith('> '): buf.append(lines[i][2:]); i += 1
            out.append('<blockquote>' + ''.join(f'<p>{inline(b)}</p>' for b in buf if b.strip()) + '</blockquote>'); continue
        if re.match(r'^[-・*] ', ln) or re.match(r'^\d+\. ', ln):
            ordered = bool(re.match(r'^\d+\. ', ln)); tag = 'ol' if ordered else 'ul'; buf = []
            while i < len(lines) and (re.match(r'^[-・*] ', lines[i]) or re.match(r'^\d+\. ', lines[i])):
                buf.append(re.sub(r'^([-・*]|\d+\.) ', '', lines[i])); i += 1
            out.append(f'<{tag}>' + ''.join(f'<li>{inline(b)}</li>' for b in buf) + f'</{tag}>'); continue
        if ln.strip() == '---': out.append('<hr />'); i += 1; continue
        if ln.strip():
            buf = []
            while i < len(lines) and lines[i].strip() and not re.match(r'^(#{1,4} |> |[-・*] |\d+\. |\||```|---|!\[|!video\[|!youtube\()', lines[i]):
                buf.append(lines[i]); i += 1
            out.append('<p>' + inline(' '.join(buf)) + '</p>'); continue
        i += 1
    return '\n'.join(out)

SHELL = """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{title}｜張詩沂</title>
<meta name="description" content="{desc}" />
<meta property="og:title" content="{title}｜張詩沂" />
<meta property="og:type" content="article" />
<meta property="og:image" content="https://muchang32.github.io/portfolio/assets/og-cover.jpg" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta name="twitter:card" content="summary_large_image" />
<link rel="icon" type="image/png" sizes="64x64" href="{up}assets/favicon.png" />
<link rel="apple-touch-icon" href="{up}assets/apple-touch-icon.png" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous" />
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;900&family=Space+Grotesk:wght@500;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet" />
<style>
*{{box-sizing:border-box}}
body{{margin:0;background:{bg};color:{ink};font-family:"Noto Sans TC","Space Grotesk",sans-serif;line-height:1.85;-webkit-font-smoothing:antialiased}}
a{{color:{violet}}}
header.bar{{position:sticky;top:0;z-index:20;background:rgba(250,247,240,.94);backdrop-filter:blur(10px)}}
header.bar div{{max-width:{wrap};margin:0 auto;padding:14px clamp(16px,4vw,28px);display:flex;align-items:center}}
.back{{font-weight:700;font-size:15px;color:{ink};text-decoration:none}}
.back:hover{{color:{violet}}}
main{{max-width:{wrap};margin:0 auto;padding:clamp(24px,4vw,48px) clamp(16px,4vw,28px) 88px}}
.wrap{{max-width:100%;text-align:left}}
h1{{font-size:clamp(28px,4.6vw,44px);line-height:1.25;letter-spacing:-.02em;margin:0 0 18px}}
h2{{font-size:clamp(20px,2.6vw,27px);margin:52px 0 14px;line-height:1.35}}
h1+p+h2,h1+h2{{margin-top:34px}}
h3{{font-size:clamp(17px,2vw,20px);margin:36px 0 10px}}
p,li{{font-size:16.5px}}
blockquote{{margin:26px 0;padding:2px 0 2px 20px;border-left:3px solid {accent};color:#3E3932}}
blockquote p{{margin:6px 0}}
figure{{margin:32px 0}}
figure img{{width:100%;height:auto;border-radius:14px;display:block}}
figure video{{width:100%;height:auto;border-radius:14px;display:block;background:#14110F}}
figure+p em{{display:block;text-align:left;color:#6E6A85;font-size:14px;margin-top:-22px}}
code{{font-family:'IBM Plex Mono',monospace;font-size:14px;background:{soft};padding:2px 6px;border-radius:5px}}
pre{{background:{ink};color:{bg};padding:18px 20px;border-radius:14px;overflow-x:auto}}
pre code{{background:none;color:inherit;font-size:13.5px;line-height:1.7}}
.tw{{overflow-x:auto;margin:24px 0}}
table{{border-collapse:collapse;width:100%;min-width:420px}}
th,td{{border-bottom:1px solid #E3DEF2;padding:10px 12px;text-align:left;font-size:15px;vertical-align:top}}
th{{background:{soft};font-weight:700}}
hr{{border:0;border-top:1px solid #E3DEF2;margin:44px 0}}
.foot{{max-width:{wrap};margin:64px auto 0;padding-top:26px;border-top:1px solid #E3DEF2;display:flex;flex-wrap:wrap;gap:14px;justify-content:space-between;font-size:15px}}
.foot a{{font-weight:700;text-decoration:none;color:{ink}}}
.foot a:hover{{color:{violet}}}
:focus-visible{{outline:3px solid {violet};outline-offset:3px;border-radius:4px}}
@media (max-width:640px){{p,li{{font-size:16px}}main{{padding-bottom:64px}}}}
{extra_css}
</style>
</head>
<body>
<header class="bar"><div>
  <a class="back" href="{up}index.html#{back_anchor}">← {back_label}</a>
</div></header>
<main><div class="wrap">
{kicker_html}<h1>{h1}</h1>
{content}
</div>
<nav class="foot">
  <a href="{prev_href}">{prev_label}</a>
  <a href="{next_href}">{next_label}</a>
</nav>
</main>
{extra_js}
</body>
</html>
"""

def build(md_path, out_path, kicker, back_anchor, back_label, prev, nxt, depth,
          wrap='880px', variant='plain'):
    md = pathlib.Path(md_path).read_text(encoding='utf-8')
    lines = md.split('\n')
    title = lines[0].lstrip('# ').strip()
    body_md = '\n'.join(lines[1:])
    desc = ''
    for ln in lines[1:]:
        if ln.startswith('> '): desc = ln[2:].strip(); break
    content = md2html(body_md, depth)
    extra_css, kicker_html, extra_js = '', '', ''
    if variant == 'case':
        extra_css = CASE_CSS.format(**PAL)
        extra_js = CASE_JS if 'class="yt"' in content else ''
        kicker_html = f'<p class="kicker">{html.escape(kicker)}</p>\n'
        # 開頭那句引言是摘要，樣式跟內文中的引言不同
        if content.startswith('<blockquote>'):
            content = content.replace('<blockquote>', '<blockquote class="summary">', 1)
    out = pathlib.Path(out_path); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(SHELL.format(title=html.escape(title), h1=html.escape(title), desc=html.escape(desc or title),
                                content=content, up='../' * depth, kicker=kicker,
                                wrap=wrap,
                                extra_css=extra_css, kicker_html=kicker_html,
                                extra_js=extra_js,
                                back_anchor=back_anchor, back_label=back_label,
                                prev_href=prev[0], prev_label=prev[1],
                                next_href=nxt[0], next_label=nxt[1], **PAL), encoding='utf-8')
    return title

ARTS = ['01-auto-image','02-50lan','03-ai-era','04-lovable','05-travel-app']
for i, a in enumerate(ARTS):
    prev = (f'./{ARTS[i-1]}.html' if i > 0 else f'./{ARTS[-1]}.html', '← 上一篇')
    nxt  = (f'./{ARTS[i+1]}.html' if i < len(ARTS)-1 else f'./{ARTS[0]}.html', '下一篇 →')
    t = build(f'writing/{a}.md', f'writing/{a}.html', '企業內部刊物專欄', 'writing', '回到專欄', prev, nxt, 1)
    print('writing/', a, '→', t)

CASES = [('aicast-case-study.md','case/aicast.html','Aicast'), ('anfu-case-study.md','case/anfu.html','安否通')]
for i,(src,dst,name) in enumerate(CASES):
    other = CASES[1-i]
    t = build(src, dst, '精選案例', 'case', '回到案例',
              ('../index.html#case','← 回到案例'), (f'../{other[1]}', f'{other[2]} →'), 1,
              variant='case')
    print(dst, '→', t)
