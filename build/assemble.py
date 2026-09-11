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

# ---- AI Lab 第一張卡：接上實際截圖 ----
_lab_ph = re.compile(
    r'(<div data-href="https://muchang32\.github\.io/udn-order/"[^>]*>\s*)'
    r'<div style="position:relative;aspect-ratio:16/10;[^"]*"[^>]*>.*?</div>', re.S)
body = _lab_ph.sub(
    r'\1<img src="./assets/ai-lab/01-udn-order.jpg" alt="要不要來一杯 點餐系統畫面" '
    r'loading="lazy" decoding="async" '
    r'style="aspect-ratio:16/10;width:100%;object-fit:cover;border-radius:16px;display:block" />',
    body, count=1)

# ---- 首頁也不出現刊物名稱 ----
body = body.replace('《聯8達》', '企業內部刊物').replace('「聯8達」', '企業內部刊物')
body = body.replace('企業內部刊物企業內部刊物', '企業內部刊物')

# ---- AI Lab 首張卡改用新截圖 ----
body = body.replace('./assets/ai-lab/01-udn-order.jpg', './assets/ai-lab/01-udn-order-2.jpg')

# ---- Design Background 右欄：接上 19 張平面作品 ----
# 設計已排好 7 個 2:1 寬格與 12 個 1:1 方格；依比例對應填入，保留原本的排列節奏
WIDE   = ['01', '03', '10', '18', '19']
SQUARE = ['02', '04', '05', '07', '11', '13', '14', '15', '16', '17']
_w, _sq = iter(WIDE), iter(SQUARE)
_order = []

def _tile(m):
    span, ratio = m.group(1) or '', m.group(2)
    if ratio == '2/1':
        n = next(_w, None)
    elif ratio == '1/1':
        n = next(_sq, None)
    else:
        return m.group(0)          # 4/5 是左欄 UI/UX 佔位，不動
    if n is None:
        return ''          # 圖不夠時直接移除該格，不要留下灰色佔位框
    idx = len(_order); _order.append(n)
    return (f'<button type="button" data-lb="{idx}" aria-label="放大檢視平面設計作品 {idx+1}" '
            f'style="{span}aspect-ratio:{ratio};padding:0;border:0;background:none;cursor:zoom-in;'
            f'border-radius:12px;overflow:hidden;display:block">'
            f'<img src="./assets/design/graphic/_selected/thumb/{n}.jpg" alt="平面設計作品 {idx+1}" '
            f'loading="lazy" decoding="async" '
            f'style="width:100%;height:100%;object-fit:cover;display:block" /></button>')

_grid_tile = re.compile(
    r'<div style="(grid-column:span 2;)?aspect-ratio:(\d/\d);border-radius:12px;background:#F1ECE1;[^"]*">.*?</div>',
    re.S)
body = _grid_tile.sub(_tile, body)
LB_ORDER = _order

# ---- 燈箱 ----
_full = ','.join(f"'./assets/design/graphic/_selected/full/{n}.jpg'" for n in LB_ORDER)
lightbox = """
<div id="lb" hidden role="dialog" aria-modal="true" aria-label="作品放大檢視"
     style="position:fixed;inset:0;z-index:200;background:rgba(20,17,15,.92);display:flex;align-items:center;justify-content:center;padding:clamp(12px,4vw,48px)">
  <img id="lb-img" alt="" style="max-width:100%;max-height:100%;object-fit:contain;border-radius:8px;display:block" />
  <div style="position:absolute;left:0;right:0;bottom:clamp(10px,2vw,20px);text-align:center;color:#FAF7F0;font-family:'IBM Plex Mono',monospace;font-size:13px">
    <span id="lb-count"></span>
  </div>
  <button id="lb-prev" type="button" aria-label="上一張" style="position:absolute;left:clamp(6px,2vw,20px);top:50%;transform:translateY(-50%);width:46px;height:46px;border-radius:999px;border:2px solid #FAF7F0;background:rgba(20,17,15,.5);color:#FAF7F0;font-size:20px;cursor:pointer">‹</button>
  <button id="lb-next" type="button" aria-label="下一張" style="position:absolute;right:clamp(6px,2vw,20px);top:50%;transform:translateY(-50%);width:46px;height:46px;border-radius:999px;border:2px solid #FAF7F0;background:rgba(20,17,15,.5);color:#FAF7F0;font-size:20px;cursor:pointer">›</button>
  <button id="lb-close" type="button" aria-label="關閉" style="position:absolute;top:clamp(8px,2vw,18px);right:clamp(8px,2vw,18px);width:44px;height:44px;border-radius:999px;border:2px solid #FAF7F0;background:rgba(20,17,15,.5);color:#FAF7F0;font-size:22px;cursor:pointer">×</button>
</div>
<script>window.LB_FULL=[""" + _full + """];</script>
"""
body = body + lightbox

head_extra = """
<title>張詩沂 Shi-Yi Chang｜設計出身的 AI 產品人</title>
<meta name="description" content="10 年設計積累 × PM 實戰 × AI 工具應用。2025 iF 設計獎、iPAS AI 應用規劃師。從需求分析到原型實作，都能自己動手。" />
<meta name="author" content="張詩沂 Shi-Yi Chang" />
<link rel="canonical" href="https://muchang32.github.io/portfolio/" />
<meta property="og:type" content="website" />
<meta property="og:title" content="張詩沂 Shi-Yi Chang｜設計出身的 AI 產品人" />
<meta property="og:description" content="10 年設計積累 × PM 實戰 × AI 工具應用。從需求分析到原型實作，都能自己動手。" />
<meta property="og:locale" content="zh_TW" />
<meta name="twitter:card" content="summary" />
<meta name="theme-color" content="#FAF7F0" />
<script>
// 帶 #anchor 進站時直接定位到該區塊，不播放捲動動畫
if (location.hash) {
  var de = document.documentElement;
  de.style.scrollBehavior = 'auto';
  addEventListener('load', function () {
    var t = document.querySelector(location.hash);
    if (t) t.scrollIntoView({ block: 'start', behavior: 'auto' });
    setTimeout(function () { de.style.scrollBehavior = ''; }, 60);
  });
}
</script>
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
