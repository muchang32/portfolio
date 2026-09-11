#!/usr/bin/env python3
"""組裝 index.html：helmet + hover CSS + 修正 + body + app.js"""
import pathlib, re

parts = pathlib.Path('build/_parts.txt').read_text(encoding='utf-8').split('\n<!--SPLIT-->\n')
helmet, hover_css, body = parts
app = pathlib.Path('build/app.js').read_text(encoding='utf-8')

# ---- 連結修正 ----
LINKS = {
    'behance': 'https://www.behance.net/changmu',
    'resume':  './assets/resume.pdf',
}
# Behance：左欄整塊是一個 <a href="#" target="_blank">，用它獨有的 sticky 樣式定位
body = body.replace('<a href="#" target="_blank" rel="noopener" style="flex:0 1 400px',
                    f'<a href="{LINKS["behance"]}" target="_blank" rel="noopener" style="flex:0 1 400px', 1)
# 履歷下載
body = re.sub(r'href="#"([^>]*?)>(\s*)履歷下載',
              f'href="{LINKS["resume"]}" target="_blank" rel="noopener"\\1>\\2履歷下載', body)
# 案例內頁
body = re.sub(r'href="#"([^>]*?)>(\s*)閱讀完整案例', 'href="__CASE__"\\1>\\2閱讀完整案例', body)
cases = ['./case/aicast.html', './case/anfu.html']
for c in cases:
    body = body.replace('__CASE__', c, 1)
# 專欄五篇
arts = ['./writing/01-auto-image.html','./writing/02-50lan.html','./writing/03-ai-era.html',
        './writing/04-lovable.html','./writing/05-travel-app.html']
def wire_writing(m):
    wire_writing.i += 1
    return f'href="{arts[wire_writing.i-1]}"' if wire_writing.i <= len(arts) else m.group(0)
wire_writing.i = 0
w_start = body.index('id="writing"'); w_end = body.index('id="design"')
seg = body[w_start:w_end]
seg = re.sub(r'href="#"', wire_writing, seg)
body = body[:w_start] + seg + body[w_end:]

# ---- 移除「待補：Behance 網址」提示 ----
body = re.sub(r'<[^>]*>\s*待補：Behance 網址\s*</[^>]*>', '', body)

# ---- 職涯歷程容器寬度對齊其他區塊 ----
body = body.replace('max-width:940px', 'max-width:1240px')

# 靜態數字：JS 未執行時仍顯示正確值
for k, v in {'nYears':'10','nMvp':'1','nVoice':'30','nProduct':'8'}.items():
    body = body.replace(f'<span data-bind="{k}"></span>', f'<span data-bind="{k}">{v}</span>')

# ---- 標籤收進「詳細」：職涯歷程與精選案例的標籤預設不顯示 ----
# 兩處標籤容器的辨識特徵：裝著一排 border-radius:999px 的 span
def collapse_tags(m):
    inner = m.group(0)
    if inner.count('border-radius:999px') < 2:
        return inner
    return inner.replace('<div style="', '<div data-tags-group hidden style="', 1)

body = re.sub(r'<div style="[^"]*display:flex;flex-wrap:wrap[^"]*">(?:\s*<span style="[^"]*border-radius:999px[^"]*">[^<]*</span>)+\s*</div>',
              collapse_tags, body)

# ---- 專欄卡片封面：五張封面已備妥，換掉佔位框 ----
COVERS = ['assets/writing/01-auto-image/cover.jpg', 'assets/writing/02-50lan/cover.jpg',
          'assets/writing/03-ai-era/cover.jpg', 'assets/writing/04-lovable/cover.jpg',
          'assets/writing/05-travel-app/cover.jpg']
ALTS = ['自動配圖升級 專欄封面', '為了一杯 50 嵐 專欄封面', '大 AI 時代來了 專欄封面',
        '實測 Lovable 專欄封面', '保姆級旅遊 APP 教學 專欄封面']
_ph = re.compile(
    r'<div style="aspect-ratio:16/9;[^"]*">\s*<span[^>]*>素材待接入</span>\s*'
    r'<span[^>]*>writing/[^<]*</span>\s*</div>', re.S)
def _cover(m, _i=[0]):
    i = _i[0]; _i[0] += 1
    if i >= len(COVERS):
        return m.group(0)
    return (f'<img src="./{COVERS[i]}" alt="{ALTS[i]}" loading="lazy" decoding="async" '
            f'style="aspect-ratio:16/9;width:100%;object-fit:cover;border-radius:12px;display:block" />')
body = _ph.sub(_cover, body)

head_extra = """
<title>張詩沂 Shi-Yi Chang｜設計出身的 AI 產品人</title>
<meta name="description" content="10 年設計積累 × PM 實戰 × AI 工具應用。2025 iF 設計獎、iPAS AI 應用規劃師。從需求分析到原型實作，都能自己動手。" />
<meta name="author" content="張詩沂 Shi-Yi Chang" />
<link rel="canonical" href="https://miyu0603.github.io/portfolio/" />
<meta property="og:type" content="website" />
<meta property="og:title" content="張詩沂 Shi-Yi Chang｜設計出身的 AI 產品人" />
<meta property="og:description" content="10 年設計積累 × PM 實戰 × AI 工具應用。從需求分析到原型實作，都能自己動手。" />
<meta property="og:image" content="./assets/og-cover.jpg" />
<meta property="og:locale" content="zh_TW" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="theme-color" content="#FAF7F0" />
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='22' fill='%23FFD34E' stroke='%2314110F' stroke-width='8'/><text y='.9em' x='50' text-anchor='middle' font-size='58' font-family='sans-serif' font-weight='700'>詩</text></svg>" />
"""

doc = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
{head_extra}
{helmet}
<style>
{hover_css}
[hidden]{{display:none !important}}
:focus-visible{{outline:3px solid #6D4AFF;outline-offset:3px;border-radius:4px}}
.sr-only{{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}}
</style>
</head>
<body>
<a href="#about" class="sr-only">跳到主要內容</a>
{body}
<script>
{app}
</script>
</body>
</html>
"""
pathlib.Path('index.html').write_text(doc, encoding='utf-8')
print('index.html', len(doc), 'bytes')
