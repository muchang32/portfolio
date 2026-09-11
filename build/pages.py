#!/usr/bin/env python3
"""把 writing/*.md 與兩則案例 md 轉成與首頁同調性的內頁。"""
import re, pathlib, html

ROOT = pathlib.Path('.')
PAL = dict(bg='#FAF7F0', ink='#14110F', card='#FFFFFF', accent='#FFD34E',
           violet='#6D4AFF', soft='#FFF6D9', line='#14110F')

def md2html(md, depth):
    up = '../' * depth
    out, lines, i = [], md.split('\n'), 0
    def inline(t):
        t = html.escape(t)
        t = re.sub(r'!\[\]\((?:\.\./)*([^)]+)\)', lambda m: f'<img src="{up}{m.group(1)}" alt="" loading="lazy" />', t)
        t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', t)
        t = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', t)
        t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
        t = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', t)
        return t
    while i < len(lines):
        ln = lines[i]
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
            lvl = len(m.group(1)); out.append(f'<h{lvl}>{inline(m.group(2))}</h{lvl}>'); i += 1; continue
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
            while i < len(lines) and lines[i].strip() and not re.match(r'^(#{1,4} |> |[-・*] |\d+\. |\||```|---|!\[)', lines[i]):
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
header.bar div{{max-width:760px;margin:0 auto;padding:14px clamp(16px,4vw,28px);display:flex;align-items:center}}
.back{{font-weight:700;font-size:15px;color:{ink};text-decoration:none}}
.back:hover{{color:{violet}}}
main{{max-width:760px;margin:0 auto;padding:clamp(24px,4vw,48px) clamp(16px,4vw,28px) 88px}}
.wrap{{max-width:100%;text-align:left}}
.kicker{{font-family:'IBM Plex Mono',monospace;font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:#6E6A85;margin-bottom:14px}}
h1{{font-size:clamp(28px,4.6vw,44px);line-height:1.25;letter-spacing:-.02em;margin:0 0 18px}}
h2{{font-size:clamp(20px,2.6vw,27px);margin:52px 0 14px;line-height:1.35}}
h1+p+h2,h1+h2{{margin-top:34px}}
h3{{font-size:clamp(17px,2vw,20px);margin:36px 0 10px}}
p,li{{font-size:16.5px}}
blockquote{{margin:26px 0;padding:2px 0 2px 20px;border-left:3px solid {accent};color:#3E3932}}
blockquote p{{margin:6px 0}}
figure{{margin:32px 0}}
figure img{{width:100%;height:auto;border-radius:14px;display:block}}
figure+p em{{display:block;text-align:center;color:#6E6A85;font-size:14px;margin-top:-22px}}
code{{font-family:'IBM Plex Mono',monospace;font-size:14px;background:{soft};padding:2px 6px;border-radius:5px}}
pre{{background:{ink};color:{bg};padding:18px 20px;border-radius:14px;overflow-x:auto}}
pre code{{background:none;color:inherit;font-size:13.5px;line-height:1.7}}
.tw{{overflow-x:auto;margin:24px 0}}
table{{border-collapse:collapse;width:100%;min-width:420px}}
th,td{{border-bottom:1px solid #E3DEF2;padding:10px 12px;text-align:left;font-size:15px;vertical-align:top}}
th{{background:{soft};font-weight:700}}
hr{{border:0;border-top:1px solid #E3DEF2;margin:44px 0}}
.foot{{max-width:760px;margin:64px auto 0;padding-top:26px;border-top:1px solid #E3DEF2;display:flex;flex-wrap:wrap;gap:14px;justify-content:space-between;font-size:15px}}
.foot a{{font-weight:700;text-decoration:none;color:{ink}}}
.foot a:hover{{color:{violet}}}
:focus-visible{{outline:3px solid {violet};outline-offset:3px;border-radius:4px}}
@media (max-width:640px){{p,li{{font-size:16px}}main{{padding-bottom:64px}}}}
</style>
</head>
<body>
<header class="bar"><div>
  <a class="back" href="{up}index.html#{back_anchor}">← {back_label}</a>
</div></header>
<main><div class="wrap">
<h1>{h1}</h1>
{content}
</div>
<nav class="foot">
  <a href="{prev_href}">{prev_label}</a>
  <a href="{next_href}">{next_label}</a>
</nav>
</main>
</body>
</html>
"""

def build(md_path, out_path, kicker, back_anchor, back_label, prev, nxt, depth):
    md = pathlib.Path(md_path).read_text(encoding='utf-8')
    lines = md.split('\n')
    title = lines[0].lstrip('# ').strip()
    body_md = '\n'.join(lines[1:])
    desc = ''
    for ln in lines[1:]:
        if ln.startswith('> '): desc = ln[2:].strip(); break
    content = md2html(body_md, depth)
    out = pathlib.Path(out_path); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(SHELL.format(title=html.escape(title), h1=html.escape(title), desc=html.escape(desc or title),
                                content=content, up='../' * depth, kicker=kicker,
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
              ('../index.html#case','← 回到案例'), (f'../{other[1]}', f'{other[2]} →'), 1)
    print(dst, '→', t)
