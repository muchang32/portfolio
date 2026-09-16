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

# ---- Design Background 右欄：接上 19 張平面作品 ----
# 設計已排好 7 個 2:1 寬格與 12 個 1:1 方格；依比例對應填入，保留原本的排列節奏
WIDE   = ['01', '03', '10', '18', '19']
SQUARE = ['02', '04', '07', '11', '13', '14', '16', '17', '20']
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

# ---- Design Background 版面：兩欄等高、更多作品連結移入網格 ----
# 1. 外層改為 stretch，左欄取消 sticky（sticky 與等高互斥）
body = body.replace(
    'display:flex;flex-wrap:wrap;gap:clamp(16px,2.2vw,28px);align-items:flex-start',
    'display:flex;flex-wrap:wrap;gap:clamp(16px,2.2vw,28px);align-items:stretch', 1)
body = body.replace('max-width:440px;min-width:0;position:sticky;top:110px;',
                    'max-width:440px;min-width:0;', 1)

# 2. 右欄與網格撐滿高度，列與列之間平均分配剩餘空間
body = body.replace('flex:1 1 420px;min-width:0;display:flex;flex-direction:column;gap:16px',
                    'flex:1 1 420px;min-width:0;display:flex;flex-direction:column;gap:16px', 1)
body = body.replace(
    'display:grid;grid-template-columns:repeat(auto-fill,minmax(min(24%,100px),1fr));gap:clamp(8px,1vw,12px)',
    'display:grid;grid-template-columns:repeat(auto-fill,minmax(min(24%,100px),1fr));'
    'gap:clamp(8px,1vw,12px);align-content:space-between;flex:1" data-grid="works', 1)

# 3. 「查看更多作品 →」改名並移進網格當最後一格
_more = re.compile(r'<a href="https://www\.cakeresume\.com/me/sandy06032/portfolios"[^>]*>.*?</a>', re.S)
_m = _more.search(body)
if _m:
    body = body.replace(_m.group(0), '', 1)
    tile = ('<a href="https://www.cakeresume.com/me/sandy06032/portfolios" target="_blank" rel="noopener" '
            'style="aspect-ratio:auto;min-height:100%;border-radius:12px;border:2px dashed #14110F;'
            'display:flex;align-items:center;justify-content:center;gap:6px;text-decoration:none;'
            'color:#14110F;font-weight:700;font-size:clamp(11px,1.05vw,13px);background:#FFF6D9;'
            'text-align:center;padding:6px;line-height:1.5">'
            '更多<br/>作品 →</a>')
    # 插在「最後一個作品格」之後（不要抓到後面區塊的 button）
    last_tile = body.rfind('data-lb=')
    end = body.index('</button>', last_tile) + len('</button>')
    body = body[:end] + tile + body[end:]

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

# 左欄 UI/UX 佔位改為撐滿（等高之後不要留下空白）
body = body.replace('aspect-ratio:4/5;border-radius:14px;background:#FFE9A8;',
                    'flex:1;min-height:300px;border-radius:14px;background:#FFE9A8;', 1)

# ---- 導覽列 logo 換成星芒圖 ----
body = body.replace(
    '<span style="width:26px;height:26px;border-radius:8px;background:#FFD34E;'
    'border:2px solid #14110F;display:inline-block"></span>',
    '<img src="./assets/logo.png" alt="" width="28" height="28" '
    'style="width:28px;height:28px;display:inline-block;flex:0 0 auto" />', 1)

# ---- 信箱膠囊：白底、無框線 ----
# 只改「顯示信箱位址」的兩顆（Hero 與聯絡區），不動「寫信給我」按鈕
def _mail_chip(m):
    st = m.group(2)
    st = st.replace('background:transparent;', 'background:#FFFFFF;')
    st = re.sub(r'border:2px solid #14110F;', '', st)
    # 少了 2px 邊框，補回內距讓尺寸不變
    st = st.replace('padding:16px 28px;', 'padding:18px 30px;').replace('padding:15px 28px;', 'padding:17px 30px;')
    return m.group(1) + st + m.group(3)

body = re.sub(
    r'(<a href="mailto:mu\.chang32@gmail\.com" style=")([^"]*background:transparent;[^"]*)(")',
    _mail_chip, body)

# ---- 明亮黃：∞ 與 say hello with me ----
body = body.replace('color:#C79400', 'color:#FFC400')

# ---- 頁尾：拿掉名字左邊的色塊 ----
body = re.sub(
    r'<span style="width:22px;height:22px;border-radius:7px;background:#FFD34E;'
    r'border:2px solid #14110F[^"]*"></span>', '', body, count=1)

# ---- 回到頂端：箭頭改為粗線 SVG ----
body = body.replace('>↑</button>',
    '><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#14110F" '
    'stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M12 20V5"/><path d="M5 12l7-7 7 7"/></svg></button>', 1)

# ---- 本輪文案／區塊名稱調整 ----
# 1. say hello：改用 Hero 的黃底標示，首字大寫，加笑臉
body = body.replace(
    '<span style="font-family:\'Space Grotesk\',sans-serif;font-style:italic;font-weight:700;color:#FFC400">say hello with me</span>',
    '<span style="position:relative;display:inline-block">'
    '<span style="position:absolute;left:-6px;right:-6px;bottom:.1em;height:.34em;'
    'background:#FFD34E;border-radius:4px;z-index:0"></span>'
    '<span style="position:relative;z-index:1;font-family:\'Space Grotesk\',sans-serif;'
    'font-style:italic;font-weight:700">Say hello with me ☺</span></span>', 1)

# 2. 區塊改名
body = body.replace('>Learning</h2>', '>Credentials</h2>')
body = body.replace('>Learning<', '>Credentials<')
body = body.replace('Design Background', 'Selected Design Work')

# 3. 刪除兩句說明
body = body.replace(
    '<p style="margin:0;font-size:14.5px;color:#3B342E;line-height:1.85">'
    '一則是交付過的產品，一則是從零定義的規劃。兩種不同的能力。</p>', '', 1)
import re as _re
body = _re.sub(r'<p style="margin:0;font-size:clamp\(15px,1\.4vw,19px\);font-weight:700;'
               r'color:#2C2620;line-height:1\.7">用 AI 工具動手做出來的產品</p>', '', body, count=1)

# 4. 英文 初階 → 中階（補一顆實心點）
_en = body.index('>英文<')
_seg_end = body.index('</div>', body.index('初階', _en))
_seg = body[_en:_seg_end]
_seg = _seg.replace('<span style="width:12px;height:12px;border-radius:50%;background:transparent;border:1.5px solid #14110F"></span>', '<span style="width:12px;height:12px;border-radius:50%;background:#FFD34E;border:1.5px solid #14110F"></span>', 1).replace('初階', '中階')
body = body[:_en] + _seg + body[_seg_end:]

# 5. 關於我：拿掉「與 Vibe Coding」
body = body.replace('現在透過 AI Coding 與 Vibe Coding，', '現在透過 AI Coding，', 1)

# ---- 職涯歷程：補全 2019 以前的工作內容（內容取自本人 104 履歷）----
UL = ('<ul style="margin:10px 0 0;padding-left:1.1em;display:flex;flex-direction:column;'
      'gap:9px;font-size:14.5px;line-height:1.8;color:#2C2620">{items}</ul>')
P_ONE = '<p style="margin:10px 0 0;font-size:14.5px;line-height:1.8;color:#2C2620">{txt}</p>'

def _bullets(*items):
    return UL.format(items=''.join(f'<li>{x}</li>' for x in items))

# 維思資訊：原本 2 條，補到 4 條
body = body.replace(
    '<li>品牌官網視覺設計提案與製作</li><li>活動企劃提案、廣告素材與影片腳本</li>',
    '<li>品牌官網所有視覺設計提案與製作</li>'
    '<li>活動企劃提案討論、活動素材製作</li>'
    '<li>廣告素材設計（Facebook、LINE@、Instagram、Google 多媒體）</li>'
    '<li>平面文宣設計與輸出、簡易網頁維護協助</li>', 1)

# 榭澄：單句 → 條列
body = body.replace(
    P_ONE.format(txt='在職期間單獨執行品牌官網大改版（Web ＋ 手機版）'),
    _bullets(
        '品牌官網視覺與維護，在職期間<strong>單獨執行網頁大改版</strong>（Web ＋ 手機版）',
        '商品拍攝、修圖與合成（單眼／微單拍攝，Lightroom 調光調色、Photoshop 細修）',
        '商品影片拍攝與剪輯（Premiere），並協助外拍',
        'FB 粉絲團、LINE@、IG 圖文與影片素材製作；平面文宣設計與季節性活動規劃',
    ), 1)

# 橋星：單句 → 條列
body = body.replace(
    P_ONE.format(txt='單獨從零架設品牌官網，自訂 CSS 調整版型'),
    _bullets(
        '<strong>單獨從零架設品牌官網</strong>，使用 Shopline 後台建置網站結構，並自訂 CSS 調整版型',
        '品牌官網所有視覺設計',
        'FB 粉絲團與官方 LINE@ 管理，文案撰寫與圖片、影片素材製作',
        '平面文宣設計、季節性活動規劃與數據概略分析',
    ), 1)

# 聯興通運：原本沒有內容，補上
body = body.replace(
    '聯興通運・實習</span>\n                </div>',
    '聯興通運・實習</span>\n                </div>' + _bullets(
        '維護人力資源紀錄（員工基本資料、職務輪調、出缺勤與績效評核）',
        '人員招募、甄選與任用',
        '薪酬運算與人事管理報表（組織圖、工時規劃、出勤管理）',
        '公司美編事務（宣傳海報、傳單、活動布置）',
    ), 1)

# ---- 「已解決的問題」加上 hover 對話框 ----
body = body.replace(
    '<div style="font-size:13px;color:#3B342E;margin-top:7px;line-height:1.7">已解決的問題</div>',
    '<div style="font-size:13px;color:#3B342E;margin-top:7px;line-height:1.7">'
    '<span class="tip" tabindex="0" role="button" aria-describedby="tip-inf">已解決的問題'
    '<span class="tip-bubble" id="tip-inf" role="tooltip">'
    '每個產品、每項功能、每個決策，背後的使用者、商業目標與技術限制都不一樣。'
    '沒有一套能完美複製的 SOP——所以問題永遠解不完，這也是這份工作最有意思的地方。'
    '</span></span></div>', 1)

# ===== 本輪調整 =====
# 1. say hello：回復黃字、取消斜體、移除黃底標示
body = body.replace(
    '<span style="position:relative;display:inline-block">'
    '<span style="position:absolute;left:-6px;right:-6px;bottom:.1em;height:.34em;'
    'background:#FFD34E;border-radius:4px;z-index:0"></span>'
    '<span style="position:relative;z-index:1;font-family:\'Space Grotesk\',sans-serif;'
    'font-style:italic;font-weight:700">Say hello with me ☺</span></span>',
    '<span style="font-family:\'Space Grotesk\',sans-serif;font-weight:700;color:#FFC400">'
    'Say hello with me ☺</span>', 1)

# 2. 複製 Email → 圖示（保留無障礙名稱）
_copy_icon = ('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
              'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
              '<rect x="9" y="9" width="12" height="12" rx="2.5"/>'
              '<path d="M5 15V5a2 2 0 0 1 2-2h10"/></svg>')
body = re.sub(
    r'<button data-on="copyEmail" style="[^"]*"(?:data-hv="h\d+")?',
    '<button data-on="copyEmail" data-copybtn style="border:0;background:none;padding:8px;'
    'color:#14110F;cursor:pointer;display:inline-flex;align-items:center;justify-content:center;'
    'line-height:0;transition:transform .16s ease,color .16s ease"',
    body)
body = re.sub(r'(<button data-on="copyEmail"[^>]*)(>)',
              r'\1 aria-label="複製 Email" title="複製 Email"\2', body)
_check_icon = ('<span data-copy-done hidden><svg width="20" height="20" viewBox="0 0 24 24" fill="none" '
               'stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" '
               'aria-hidden="true"><path d="M4 12.5l5.5 5.5L20 7"/></svg></span>')
body = body.replace('<span data-bind="copyLabel"></span>',
                    '<span data-copy-idle>' + _copy_icon + '</span>' + _check_icon
                    + '<span data-bind="copyLabel" class="sr-only"></span>')

# 3. 對話框：白底黑框、換內容
body = body.replace(
    '每個產品、每項功能、每個決策，背後的使用者、商業目標與技術限制都不一樣。'
    '沒有一套能完美複製的 SOP——所以問題永遠解不完，這也是這份工作最有意思的地方。',
    '累積解決 200+ 的問題，持續增加中⋯', 1)

# 4. 職涯歷程副標：點點前後不留空格
body = body.replace('職涯歷程　·　從視覺到體驗，再到產品與 AI 落地',
                    '職涯歷程·從視覺到體驗，再到產品與 AI 落地')

# 5. 展開／收合按鈕改黑底白字
body = body.replace(
    '<button data-on="toggleCareer" style="border:2px solid #14110F;background:#fff;',
    '<button data-on="toggleCareer" style="border:2px solid #14110F;background:#14110F;color:#FAF7F0;', 1)

# 6. 公司名稱補全
for a, b in [('>聯經數位<', '>聯經數位股份有限公司<'),
             ('>盈德網絡服務<', '>盈德網絡服務有限公司<'),
             ('>維思資訊<', '>維思資訊股份有限公司<'),
             ('>橋星企業<', '>橋星企業有限公司<'),
             ('>聯興通運・實習<', '>聯興通運股份有限公司・實習<')]:
    body = body.replace(a, b)

# 7. 展開區排版改為與上方一致：日期 → 職稱 → 公司 → 內容（垂直堆疊）
def _restack(m):
    date, title, company = m.group(1), m.group(2), m.group(3)
    return (f'<div style="margin-bottom:12px">'
            f'<span style="font-family:\'IBM Plex Mono\',monospace;font-size:12.5px;'
            f'font-weight:600;letter-spacing:.04em">{date}</span></div>'
            f'<h3 style="margin:0 0 4px;font-size:17px;font-weight:900;line-height:1.5">{title}</h3>'
            f'<p style="margin:0 0 14px;font-size:14px;color:#3B342E">{company}</p>')

body = re.sub(
    r'<div style="display:flex;flex-wrap:wrap;gap:12px;align-items:baseline">\s*'
    r'<span style="font-family:\'IBM Plex Mono\',monospace;font-size:12\.5px;font-weight:600">([^<]+)</span>\s*'
    r'<h3 style="margin:0;font-size:17px;font-weight:900">([^<]+)</h3>\s*'
    r'<span style="font-size:14px;color:#3B342E">([^<]+)</span>\s*</div>',
    _restack, body)

# 8. 前段工作內容補齊（取自本人 104 履歷）
body = body.replace(
    '<li>主導 AI 有聲書平台 Aicast 的產品開發、測試驗證與外包協作，管理 9–12 人</li>',
    '<li><strong>產品開發與迭代</strong>：主持每週兩次 Aicast 產品開發會議，控管開發進度並排除技術阻礙；'
    '依用戶回饋分析測試結果，持續優化操作流程與 UX 體驗</li>'
    '<li><strong>AI 語音專案落地</strong>：獨立統籌 30 位以上素人配音員的徵選、簽約與錄音審理；'
    '自學修音技術優化台灣口音 AI 配音模型，提升語音自然度</li>', 1)
body = body.replace(
    '<li>建立 30+ 位配音員聲音素材庫與 720 首音效資料庫</li>',
    '<li><strong>跨國資源與外包管理</strong>：統籌多語系翻譯人員（德、法、日）與平面設計師等外包資源，'
    '管理 9–12 人；主導發包並建置涵蓋 720 首音效的資料庫</li>', 1)
body = body.replace(
    '<li>主導 iF 設計獎與金點設計獎申請，2025 年獲 iF 設計獎</li>',
    '<li><strong>國際獎項與視覺統籌</strong>：主導產品品牌視覺與參賽策略，親自設計相關多媒體素材，'
    '帶領 Aicast 奪得 2025 年 iF 設計獎</li>', 1)
body = body.replace(
    '<li>品牌官網行銷活動 Landing Page 視覺設計</li><li>APP 與 Web UI 介面設計</li>',
    '<li>品牌官網行銷活動 Landing Page 網頁視覺設計與圖片素材 Resize</li>'
    '<li>APP、Web UI 介面設計</li>'
    '<li>製作廣告行銷用圖與各渠道用圖</li>'
    '<li>製作行銷影片素材</li>', 1)

# 9. 證照：核發單位改到名稱後面（同一行），並修正單位
PILL = ('<span style="display:inline-block;background:{bg};border-radius:999px;padding:6px 14px;'
        'font-size:13.5px;font-weight:700">{name}</span>')
def _cert(bg, name, issuer):
    return ('<div style="display:flex;flex-wrap:wrap;align-items:center;gap:8px">'
            + PILL.format(bg=bg, name=name)
            + f'<span style="font-size:11.5px;color:#6B635B">{issuer}</span></div>')

_certs = [
    ('#FFD34E', 'iPAS AI 應用規劃師（初級）', '經濟部產業發展署'),
    ('#F3EFE4', 'AI_UX 人工智慧輔助產品體驗設計', '經濟部商業發展署'),
    ('#F3EFE4', '獨角獸設計師養成計劃 Design Jam', 'Unblock'),
    ('#F3EFE4', '丙級電腦軟體設計技術士', '勞動部勞動力發展署'),
    ('#F3EFE4', 'Illustrator ・ Photoshop 原廠認證', 'Adobe'),
]
_old_start = body.index('CERTIFICATIONS</p>')
_blk_start = body.index('<div style="display:flex;flex-direction:column;gap:12px">', _old_start)
_blk_end = body.index('</div>\n        </div>', _blk_start)
body = (body[:_blk_start]
        + '<div style="display:flex;flex-direction:column;gap:12px">'
        + ''.join(_cert(*c) for c in _certs)
        + body[_blk_end:])

# 10. COMPETITIONS：加入 2026 公民科技協力場
_comp = ('<div>'
         '<p style="margin:0 0 4px;font-family:\'IBM Plex Mono\',monospace;font-size:12px;color:#6B635B">2026</p>'
         '<h3 style="margin:0 0 5px;font-size:15px;font-weight:900;line-height:1.6">'
         '公民科技協力場　安否通</h3>'
         '<p style="margin:0;font-size:13.5px;line-height:1.8;color:#3B342E">'
         '數位發展部徵案，兩人團隊提案弱勢機構災情即時回報平台，負責問題定義、流程設計與 UI／UX。'
         '<a href="./case/anfu.html" style="color:#6D4AFF;font-weight:700">閱讀完整案例 →</a></p>'
         '</div>')
_c = body.index('COMPETITIONS</p>')
_cb = body.index('<div style="display:flex;flex-direction:column;gap:18px">', _c)
_ins = body.index('>', _cb) + 1
body = body[:_ins] + _comp + body[_ins:]

# ===== 本輪 A：提示、箭頭、hover、競賽 =====
# A1. ∞ 的原生 title 會跟自訂對話框重複出現，移除
body = body.replace(' title="累積修復 200+ 個問題，還在繼續"', '')
body = body.replace('title="累積修復 200+ 個問題，還在繼續"', '')

# A2. 公民科技協力場：移除「閱讀完整案例」連結
body = body.replace(
    '<a href="./case/anfu.html" style="color:#6D4AFF;font-weight:700">閱讀完整案例 →</a>', '', 1)

# A3. COMPETITIONS：年份移到標題右方
def _comp_head(m):
    year, title = m.group(1), m.group(2)
    return (f'<div style="display:flex;align-items:baseline;gap:10px;justify-content:space-between;margin:0 0 5px">'
            f'<h3 style="margin:0;font-size:15px;font-weight:900;line-height:1.6">{title}</h3>'
            f'<span style="font-family:\'IBM Plex Mono\',monospace;font-size:12px;color:#6B635B;'
            f'flex:0 0 auto">{year}</span></div>')
body = re.sub(
    r'<p style="margin:0 0 4px;font-family:\'IBM Plex Mono\',monospace;font-size:12px;color:#6B635B">(\d{4})</p>\s*'
    r'<h3 style="margin:0 0 5px;font-size:15px;font-weight:900;line-height:1.6">([^<]+)</h3>',
    _comp_head, body)

# A4. Writing 箭頭改粗線 SVG
_ARROW = ('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#14110F" '
          'stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
          '<path d="M{d1}"/><path d="M{d2}"/></svg>')
body = body.replace('>←</button>',
    '>' + _ARROW.format(d1='19 12H5', d2='12 19l-7-7 7-7') + '</button>', 1)
body = body.replace('>→</button>',
    '>' + _ARROW.format(d1='5 12h14', d2='12 5l7 7-7 7') + '</button>', 1)

# A5. AI Lab 卡片 hover：上浮 + 微放大（規則位於 hover_css）
hover_css = hover_css.replace('transform:translateY(-4px)', 'transform:translateY(-4px) scale(1.04)')

# A6. What I Do 卡片 hover 改以 CSS 結構選擇器處理（見 head 的樣式區）


# ===== 本輪 B：信箱 hover 逐字動畫 =====
EMAIL = 'mu.chang32@gmail.com'
_spans = ''.join(
    f'<span style="--i:{i}">{c}</span>' for i, c in enumerate(EMAIL))
body = re.sub(
    r'(<a href="mailto:mu\.chang32@gmail\.com"[^>]*style="[^"]*)(")([^>]*>)' + re.escape(EMAIL) + r'(</a>)',
    lambda m: m.group(1) + ';' + m.group(2) + ' class="mailfx"' + m.group(3) + _spans + m.group(4),
    body)

# ===== 本輪 C：Credentials 版面 + SKILLS 工具 logo（使用者提供的檔案）=====
_SKILLS = [
    ('Claude',           'claude.png'),
    ('Gemini',           'gemini.png'),
    ('ChatGPT',          'ChatGPT.svg'),
    ('Google Antigravity','antigravity.png'),
    ('VS Code',          'VScode.png'),
    ('Figma',            'figma.png'),
    ('Illustrator',      'Adobe_Illustrator.png'),
    ('Photoshop',        'Adobe_Photoshop_CC.png'),
    ('After Effects',    'After_Effects.svg'),
    ('Premiere',         'Premiere.svg'),
]

def _logo(label, fn):
    return (f'<img src="./assets/logos/opt/{fn}" alt="{label}" title="{label}" '
            f'loading="lazy" decoding="async" '
            f'style="width:100%;height:auto;aspect-ratio:1;object-fit:contain;display:block" />')

_skills_block = (
    '<div style="min-width:0;margin-top:18px">'
    '<p style="margin:0 0 12px;font-family:\'IBM Plex Mono\',monospace;font-size:11px;'
    'letter-spacing:.18em;color:#6B635B">SKILLS</p>'
    '<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:9px;max-width:250px">'
    + ''.join(_logo(l, f) for l, f in _SKILLS) +
    '</div></div>')

body = body.replace(
    'display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,190px),1fr));'
    'gap:clamp(18px,2.2vw,32px)',
    'display:grid;gap:clamp(18px,2.2vw,28px)" data-grid="creds', 1)

def _close_of(html, open_idx):
    """回傳 open_idx 這個 <div> 對應的 </div> 結束位置（含標籤）"""
    depth, i = 0, open_idx
    while i < len(html):
        nd, cd = html.find('<div', i), html.find('</div>', i)
        if cd == -1:
            break
        if nd != -1 and nd < cd:
            depth += 1; i = nd + 4
        else:
            depth -= 1; i = cd + 6
            if depth == 0:
                return i
    raise ValueError('找不到對應的 </div>')

_lg = body.index('LANGUAGES</p>')
_col_open = body.rindex('<div style="min-width:0">', 0, _lg)
_col_close = _close_of(body, _col_open)
body = body[:_col_close - len('</div>')] + _skills_block + body[_col_close - len('</div>'):]

# LANGUAGES 三列行距縮小
body = body.replace('LANGUAGES</p> <div style="display:flex;flex-direction:column;gap:16px">',
                    'LANGUAGES</p> <div style="display:flex;flex-direction:column;gap:16px">')
_lgblk = body.index('LANGUAGES</p>')
_seg_end = body.index('</div>', body.index('英文', _lgblk))
_seg = body[_lgblk:_seg_end]
_seg = _seg.replace('flex-direction:column;gap:16px', 'flex-direction:column;gap:9px')
_seg = _seg.replace('display:flex;align-items:center;gap:12px', 'display:flex;align-items:center;gap:10px')
body = body[:_lgblk] + _seg + body[_seg_end:]

# ===== 本輪 D：摘要文案與 hover =====
# D1. Say hello 套用與信箱相同的逐字動畫
body = body.replace(
    '<span style="font-family:\'Space Grotesk\',sans-serif;font-weight:700;color:#FFC400">'
    'Say hello with me ☺</span>',
    '<span class="mailfx" style="font-family:\'Space Grotesk\',sans-serif;font-weight:700;color:#FFC400">'
    + ''.join(f'<span style="--i:{i}">{c}</span>' if c != ' ' else '<span style="--i:%d">&nbsp;</span>' % i
              for i, c in enumerate('Say hello with me ☺'))
    + '</span>', 1)

# D2. Aicast 摘要：拿掉反思，改以成果吸引點擊
body = body.replace(
    '製作一本多角色有聲書，需要配音員、錄音室與大量協調成本。Aicast 用三項 AI 技術把這件事自動化'
    '——但真正讓我學到最多的，是它最終在商業上並不成功。',
    '製作一本多角色有聲書，需要配音員、錄音室與大量協調成本。Aicast 用三項 AI 技術把這件事自動化：'
    '8 位 AI 配音員演繹 42 種聲音，多人配音有聲書的製作時間最多減少 90%。', 1)
body = re.sub(
    r'<p[^>]*>這個案例包含我如何在資源有限的團隊中做取捨.*?是兩件事。</strong></p>',
    '<p style="margin:0;font-size:14.5px;color:#3B342E;line-height:1.85">'
    '我負責需求定義、UI 規劃、測試驗證與跨職能外包管理，並主導申請 '
    '<strong>2025 iF 設計獎</strong>。</p>', body, count=1, flags=re.S)

# D3. 安否通摘要：反思移到內頁，首頁只留主張
body = re.sub(
    r'<p[^>]*>這個案例包含我如何在兩人團隊與三個月期程下切出 P0 範圍.*?寫進文件第一頁。</strong></p>',
    '<p style="margin:0;font-size:14.5px;color:#3B342E;line-height:1.85">'
    '兩人團隊提案，通過文件初審並進入<strong>數位發展部徵案決選</strong>。'
    '我負責問題定義、流程設計、介面設計與 P0 範圍切分。</p>', body, count=1, flags=re.S)

# D4. 要不要來一杯：移除該標籤
body = body.replace('data-tags="團購|使用者測試|唯一有真實其他使用者的產品"',
                    'data-tags="團購|使用者測試|多人協作"', 1)

# ---- 首頁也不出現刊物名稱 ----
body = body.replace('《聯8達》', '企業內部刊物').replace('「聯8達」', '企業內部刊物')
body = body.replace('企業內部刊物企業內部刊物', '企業內部刊物')

# ===== 本輪 F：接上四張封面 =====
def _img(src, alt, ratio, extra=''):
    return (f'<img src="{src}" alt="{alt}" loading="lazy" decoding="async"{extra} '
            f'style="aspect-ratio:{ratio};width:100%;max-width:100%;min-width:0;'
            f'object-fit:cover;border-radius:16px;display:block" />')

# F1. AI Lab：逐張把有素材的卡片接上截圖（佔位框以深度配對取代，並標示提示文字）
_LAB_COVERS = [
    ('https://muchang32.github.io/udn-order/',              '01-udn-order-2.jpg',   '要不要來一杯 點餐系統畫面'),
    ('https://miyu0603.github.io/my-finance/',              '05-my-finance.jpg',    '我的財務管家 介面'),
    ('https://muchang32.github.io/ai-treasure-chest/',      '06-treasure-chest.jpg','AI 精選寶箱 介面'),
    ('https://miyu0603.github.io/kyushu-2026/',              '07-kyushu.jpg',        '九州縱斷之旅 2026 介面'),
    ('https://muchang32.github.io/winter-fuji-hakone-2026/','08-winter-fuji.jpg',   '冬富士之旅 2026 介面'),
]
for _href, _file, _alt in _LAB_COVERS:
    _anchor = f'data-href="{_href}"'
    if _anchor not in body:
        raise SystemExit(f'找不到 AI Lab 卡片：{_href}')
    _c = body.index(_anchor)
    _ph = body.index('<div style="position:relative;aspect-ratio:16/10;', _c)
    _end = _close_of(body, _ph)
    # 佔位框上的 hover 標記必須跟著移轉，否則該卡會失去 hover 效果
    _hv = re.search(r'data-hv="(\w+)"', body[_ph:_end])
    _extra = f' data-hv="{_hv.group(1)}"' if _hv else ''
    body = body[:_ph] + _img(f'./assets/ai-lab/{_file}', _alt, '16/10', _extra) + body[_end:]
    # 卡片帶上封面路徑，彈窗開啟時顯示放大版
    body = body.replace(_anchor, _anchor + f' data-img="./assets/ai-lab/{_file}"', 1)

# F2. 精選案例 Aicast：主圖 + iF 官方獎章（用深度配對取代佔位框，避免吃掉相鄰結構）
_ai = body.index('Aicast 有聲內容製作平台')
_ap_start = body.rindex('<div style="aspect-ratio:16/10;border-radius:16px;background:#FFF1C2;', 0, _ai)
_ap_end = _close_of(body, _ap_start)
body = (body[:_ap_start]
        + '<div style="position:relative;min-width:0">'
        + _img('./assets/case/aicast/01.jpg', 'Aicast 有聲內容製作平台 產品畫面', '16/10')
        + '<img src="./assets/case/aicast/if-award-2025.png" alt="2025 iF Design Award" '
          'loading="lazy" decoding="async" '
          'style="position:absolute;right:10px;top:10px;width:clamp(64px,22%,96px);height:auto;'
          'display:block;filter:drop-shadow(0 2px 6px rgba(20,17,15,.3))" />'
        + '</div>'
        + body[_ap_end:])

# F3. Design Background 左欄 UI/UX 代表圖
_ui = body.index('前往 Behance 作品集')
_up_start = body.rindex('<div style="flex:1;min-height:300px;', 0, _ui)
_up_end = _close_of(body, _up_start)
body = (body[:_up_start]
        + '<img src="./assets/design/uiux/cover.jpg" alt="UI／UX 代表作品" '
          'loading="lazy" decoding="async" '
          'style="flex:1;min-height:0;width:100%;object-fit:cover;border-radius:14px;display:block" />'
        + body[_up_end:])

# ===== 本輪 G：AI Lab 彈窗（封面、放大、關閉鍵固定右上）=====
_mi = body.index('data-if="labOpen"')

# G1. 面板加大並改為 relative，讓關閉鍵可絕對定位
_panel = ('background:#fff;border:2.5px solid #14110F;border-radius:22px;'
          'box-shadow:8px 8px 0 #14110F;padding:clamp(24px,3.4vw,38px);max-width:520px;width:100%;')
assert _panel in body, '找不到彈窗面板樣式'
body = body.replace(_panel,
    'position:relative;background:#fff;border:2.5px solid #14110F;border-radius:22px;'
    'box-shadow:8px 8px 0 #14110F;padding:clamp(22px,3vw,34px);max-width:min(860px,94vw);'
    'width:100%;max-height:88vh;overflow-y:auto;', 1)

# G2. 關閉鍵移出標題列，固定於面板右上
_close_btn = ('<button data-on="closeLab" aria-label="關閉" style="flex:0 0 auto;width:38px;height:38px;'
              'border-radius:50%;border:2px solid #14110F;background:#fff;font-size:17px;'
              'line-height:1;cursor:pointer">×</button>')
assert _close_btn in body, '找不到彈窗關閉鍵'
body = body.replace(_close_btn, '', 1)

_close_fixed = ('<button data-on="closeLab" aria-label="關閉" data-hv="lbclose" '
                'style="position:absolute;top:14px;right:14px;z-index:2;width:40px;height:40px;'
                'border-radius:50%;border:2px solid #14110F;background:#fff;font-size:19px;'
                'line-height:1;cursor:pointer;box-shadow:2px 2px 0 #14110F">×</button>')

# G3. 封面圖插在面板最前，關閉鍵疊在其上
_modal_img = ('<img data-img-bind="labImg" alt="" hidden '
              'style="width:100%;aspect-ratio:16/10;object-fit:cover;border-radius:14px;'
              'border:2px solid #14110F;display:block" />')
_h3row = '<div style="display:flex;gap:14px;align-items:flex-start;justify-content:space-between">'
_ins = body.index(_h3row, _mi)
body = body[:_ins] + _close_fixed + _modal_img + body[_ins:]

head_extra = """
<title>張詩沂 Shi-Yi Chang｜設計出身的 AI 產品人</title>
<meta name="description" content="10 年設計積累 × PM 實戰 × AI 工具應用。2025 iF 設計獎、iPAS AI 應用規劃師。從需求分析到原型實作，都能自己動手。" />
<meta name="author" content="張詩沂 Shi-Yi Chang" />
<link rel="canonical" href="https://muchang32.github.io/portfolio/" />
<meta property="og:type" content="website" />
<meta property="og:title" content="張詩沂 Shi-Yi Chang｜設計出身的 AI 產品人" />
<meta property="og:description" content="10 年設計積累 × PM 實戰 × AI 工具應用。從需求分析到原型實作，都能自己動手。" />
<meta property="og:locale" content="zh_TW" />
<meta property="og:url" content="https://muchang32.github.io/portfolio/" />
<meta property="og:image" content="https://muchang32.github.io/portfolio/assets/og-cover.jpg" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta property="og:image:alt" content="張詩沂 — 設計出身的 AI 產品人" />
<meta name="twitter:card" content="summary_large_image" />
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
<link rel="icon" type="image/png" sizes="64x64" href="./assets/favicon.png" />
<link rel="apple-touch-icon" href="./assets/apple-touch-icon.png" />
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
/* 有 hover 標記就一定有過渡，避免取代元素時漏掉 inline transition */
[data-hv]{{transition:transform .16s ease,box-shadow .16s ease,color .16s ease}}
/* Credentials 四區：桌機 4 欄、平板 2 欄、手機 1 欄 */
[data-grid="creds"]{{grid-template-columns:repeat(3,minmax(0,1fr));align-items:start}}
@media (max-width:900px){{[data-grid="creds"]{{grid-template-columns:repeat(2,minmax(0,1fr))}}}}
@media (max-width:560px){{[data-grid="creds"]{{grid-template-columns:1fr}}}}
/* 信箱 hover：逐字由上往下重新落位 */
.mailfx span{{display:inline-block;will-change:transform}}
.mailfx:hover span{{animation:mailDrop .52s cubic-bezier(.22,.68,.3,1) both;
 animation-delay:calc(var(--i) * 26ms)}}
@keyframes mailDrop{{
 0%{{transform:translateY(0);opacity:1}}
 42%{{transform:translateY(-115%);opacity:0}}
 43%{{transform:translateY(115%);opacity:0}}
 100%{{transform:translateY(0);opacity:1}}
}}
@media (prefers-reduced-motion: reduce){{.mailfx:hover span{{animation:none}}}}
[data-copybtn]:hover{{transform:scale(1.12);color:#6D4AFF}}
[data-hv="lbclose"]:hover{{transform:translate(-1px,-1px);box-shadow:3px 3px 0 #14110F}}
[data-copybtn]:active{{transform:scale(.94)}}
/* What I Do：四張卡片結構不同，改用屬性選擇器一次涵蓋 */
#skills div[style*="border:2px solid #14110F"]{{transition:transform .16s ease,box-shadow .16s ease}}
#skills div[style*="border:2px solid #14110F"]:hover{{transform:translate(-3px,-3px);box-shadow:8px 8px 0 #14110F}}
/* 「已解決的問題」hover 對話框 */
.tip{{position:relative;border-bottom:2px dotted #14110F;cursor:help;outline:none}}
.tip-bubble{{position:absolute;left:0;bottom:calc(100% + 14px);transform:translateY(4px);
 width:max-content;max-width:min(300px,74vw);background:#FFFFFF;color:#14110F;font-size:13px;
 line-height:1.75;text-align:left;white-space:normal;font-weight:700;
 padding:12px 16px;border:2px solid #14110F;border-radius:12px;box-shadow:4px 4px 0 #14110F;
 opacity:0;visibility:hidden;transition:opacity .16s ease,transform .16s ease;z-index:40;pointer-events:none}}
.tip-bubble::after{{content:"";position:absolute;left:22px;top:100%;
 border:9px solid transparent;border-top-color:#14110F}}
.tip-bubble::before{{content:"";position:absolute;left:22px;top:calc(100% - 3px);
 border:9px solid transparent;border-top-color:#FFFFFF;z-index:1}}
.tip:hover .tip-bubble,.tip:focus .tip-bubble{{opacity:1;visibility:visible;transform:translateY(0)}}

/* 平面作品網格：桌機 3 欄、手機 2 欄（覆寫 inline style） */
[data-grid="works"]{{grid-template-columns:repeat(5,minmax(0,1fr)) !important}}
@media (max-width:640px){{[data-grid="works"]{{grid-template-columns:repeat(2,minmax(0,1fr)) !important}}}}
:focus-visible{{outline:3px solid #6D4AFF;outline-offset:3px;border-radius:4px}}
.sr-only{{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}}
/* 跳過連結：鍵盤 focus 時要看得見，否則等於沒有 */
a.sr-only:focus{{position:fixed;top:12px;left:12px;width:auto;height:auto;margin:0;clip:auto;
 padding:12px 20px;background:#14110F;color:#FAF7F0;border-radius:999px;font-weight:700;z-index:300}}
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
