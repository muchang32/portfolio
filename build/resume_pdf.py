#!/usr/bin/env python3
"""把個人網站的內容排成可列印的履歷，輸出 build/_pdf/resume.html。

為什麼不直接列印 index.html：網站是一頁式長捲軸，有輪播、收合卡片與彈窗，
列印出來會是一條又長又空的東西。這支用網站同一套視覺（奶油底、亮黃、硬陰影、
同一組字型）重新排成兩頁 A4：第一頁是人與經歷，第二頁是案例、能力與聯絡方式。
版型來自她在 Claude Design 做的「張詩沂履歷PDF製作」，文字則一律用網站定案的版本。

文案與網站共用的部分（職涯條列、案例的判斷／結果、能力卡引言、證照）
由 verify.py 逐字比對兩邊，任何一邊改了另一邊沒跟上就會報錯。

照片是 build/_pdf/headshot-2026.jpg（由根目錄的 大頭照.png 裁成方形）。
QR code 是 build/_pdf/qr-portfolio.svg，網址改了要重產：
    swift build/make_qr.swift "<網址>" build/_pdf/qr-portfolio.svg

用法：
    python3 build/resume_pdf.py          # 產生 HTML
    python3 build/resume_pdf.py --pdf    # 再用 Chrome 列印成 assets/resume.pdf
"""
import base64, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / 'build' / '_pdf'
OUT_HTML = OUT_DIR / 'resume.html'
OUT_PDF = ROOT / 'assets' / 'resume.pdf'
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
SITE = 'https://muchang32.github.io/portfolio/'

# ===================== 內容 =====================

NAME_ZH, NAME_EN = '張詩沂', 'Chang Shi-Yi'
ROLE = '產品經理　Product Manager'
EYEBROW = 'PRODUCT MANAGEMENT · AI APPLICATION · DESIGN'
TAGLINE = ('設計出身的', 'AI 產品人')          # 後半段畫螢光筆
SUMMARY = ('10 年設計累積 × 產品規劃到落地 × AI 工具應用，從需求分析到原型實作，都能自己動手。'
           '我習慣從使用者需求出發，結合產品規劃、跨部門協作與 AI 工具，'
           '把想法轉化成可測試的原型，再透過回饋持續改善，讓解法真正融入工作流程。')

EMAIL = 'mu.chang32@gmail.com'
SITE_LABEL = 'muchang32.github.io/portfolio'
AREA = '基隆／台北／新北'

INK, YELLOW, PURPLE, BLUE, PINK = '#14110F', '#FFD34E', '#CDBCFF', '#DDEEFF', '#FFE6E1'

STATS = [('10', '年', '設計與產品經歷', '#fff'), ('2025', '', 'iF 設計獎', YELLOW),
         ('2024', '', '公司年度 MVP', PURPLE), ('iPAS', '', 'AI 應用規劃師（初級）', BLUE)]

# 職涯：full 是整張卡加條列；one 是一張卡一行；row 是併在同一張卡裡的一列
JOBS = [
    ('2025/3 – 現在', '資訊管理師', '聯經數位股份有限公司', 'full', ('現職', INK),
     ['<b>內部產品優化</b>主導「自動配圖」改版：訪談記者與編輯，歸納四類問題並重新定義圖片排序邏輯，'
      '搜尋後實際匯入稿單的比例從 3% 提升到 42%',
      '<b>產品需求規劃</b>主導 CMS「AI 文生圖」功能規劃：訪談收斂五項關鍵洞察，'
      '將需求分成 P0／P1／P2 三層，定義從稿件讀取到入稿的完整流程與工程規格',
      '<b>自製工具落地</b>獨立開發 LiveLingo Chrome 擴充功能，串接語音辨識與翻譯 API 提供即時字幕，'
      '兩場活動實際導入',
      '<b>AI 工作流自動化</b>以 n8n 透過 MCP 串接 Claude，為新聞自動摘要建立內容檢核；'
      '與組內試驗 RAG 查詢',
      '<b>內部推廣與培訓</b>推動 AI Coding 培訓與實作工作坊；於企業內部刊物撰寫 AI 專欄共 5 篇',
      '<b>跨部門專案溝通</b>將各單位需求轉化為工程與系統可執行的內容']),
    ('2024/5 – 2025/3', '專案經理', '聯經數位股份有限公司', 'full', ('Aicast', PURPLE),
     ['主持每週兩次 Aicast 產品開發會議，控管開發進度並排除技術阻礙；依用戶回饋持續優化操作流程與 UX',
      '獨立統籌 30 位以上素人配音員的徵選、簽約與錄音審理；自學修音技術優化台灣口音 AI 配音模型',
      '統籌多語系翻譯人員（德、法、日）與平面設計師等外包資源，管理 9–12 人；'
      '建置涵蓋 720 首音效的資料庫',
      '主導產品品牌視覺與參賽策略，帶領 Aicast 奪得 2025 年 iF 設計獎；獲公司 2024 年度 MVP']),
    ('2022/8 – 2023/7', '網頁設計師（UI 設計）', '盈德網絡服務有限公司', 'one', None,
     ['品牌官網行銷活動 Landing Page 視覺設計、APP 與 Web UI 介面設計']),
    ('2019/1 – 2022/4', '網頁企劃視覺設計', '維思資訊', 'row', None,
     ['品牌官網視覺提案、活動企劃與廣告素材']),
    ('2017/2 – 2019/1', '視覺設計行銷企劃專員', '榭澄有限公司', 'row', None,
     ['單獨執行品牌官網大改版（Web ＋ 手機版）']),
    ('2015/7 – 2017/1', '行銷企劃專員', '橋星企業', 'row', None,
     ['單獨從零架設品牌官網']),
    ('2014/10 – 2015/6', '人資專員（兼美編）', '聯興國際物流　·　實習', 'row', None,
     ['人資行政與公司美編事務']),
]

# 四則案例：判斷與結果兩句與網站逐字相同
CASES = [
    (YELLOW, '2025 iF 設計獎', 'Aicast 有聲內容製作平台',
     '先把核心的角色辨識與配音修穩，再擴充功能 - 這一層不可信，周邊做再多都留不住人',
     '修復 200+ 個問題並建立測試機制，獲 2025 iF 設計獎', 'case/aicast.html'),
    (BLUE, '聯經數位　新聞編務系統', '自動配圖　從編輯的回饋到產品優化',
     '先訪談再動手 - 把回饋歸納成四類，先修產品可信度，再處理曝光與習慣',
     '搜尋後實際匯入稿單的比例從 3% 提升到 42%', 'case/auto-image.html'),
    (PINK, 'Chrome 擴充功能　活動現場導入', 'LiveLingo 即時字幕翻譯',
     '現場操作的人不是我，把每個意見抽象成可調選項，而不是照著改',
     '兩場活動實際使用，獲公司頒發獎金，已上架 Chrome 商店', 'case/livelingo.html'),
    (PURPLE, '數位發展部　全國公民科技試驗場域推廣案', '安否通　弱勢機構災情即時回報平台',
     '把清查方向反轉 - 系統點名、機構一鍵回報，市府只處理未回報的那幾家',
     '通過文件初審，進入數位發展部徵案決選', 'case/anfu.html'),
]

# 四張能力卡：引言與網站 What I Do 同一份，下面那一行取自網站條列（太長的收短成一行）
SKILLS = [
    ('★', YELLOW, 'AI 應用與原型開發', '判斷 AI 該用在哪，然後把想法做出來。',
     '運用 AI Coding 建立互動式 Web／PWA 原型，加速想法驗證'),
    ('01', BLUE, '產品規劃與需求定義', '把模糊的需求，收斂成可驗證的產品方案。',
     '透過使用者訪談與回饋分析，釐清痛點及真正需求'),
    ('02', '#EDE6FF', '專案推進與跨部門協作', '讓需求不只停在文件，而是推進到交付。',
     '協調設計、工程及外部合作夥伴，確保資訊同步與交付品質'),
    ('03', PINK, 'UX 設計與體驗驗證', '用設計讓產品更容易理解、操作與驗證。',
     '規劃資訊架構、使用者流程、Wireframe 與互動原型'),
]

TOOLS = [('AI', ['Claude', 'ChatGPT', 'Gemini', 'Google Antigravity']),
         ('開發與自動化', ['VS Code', 'n8n', 'API 串接', 'JSON', 'RAG']),
         ('設計', ['Figma', 'Illustrator', 'Photoshop', 'After Effects', 'Premiere'])]

COMPS = [('2026', '公民科技協力場　安否通'),
         ('2023', '第三屆捷運盃黑客松 UI/UX 設計賽'),
         ('2022', '獨角獸設計師競賽　PetCare 寵物照護 APP')]

CERTS = ['iPAS AI 應用規劃師（初級）', 'AI_UX 人工智慧輔助產品體驗設計',
         '獨角獸設計師養成計劃 Design Jam', '丙級電腦軟體設計技術士',
         'Illustrator ・ Photoshop 原廠認證']

LANGS = [('中文', 5, '母語'), ('日文', 4, '中上'), ('英文', 3, '中等')]

EDU = ('2010 – 2015', '華梵大學', '工業設計學系（時尚設計組）', '學士')

# ===================== 排版 =====================

CSS = """
@page{size:A4;margin:0}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{background:#FAF7F0;color:#14110F;
  font-family:'Noto Sans TC','PingFang TC','Heiti TC',sans-serif;
  -webkit-print-color-adjust:exact;print-color-adjust:exact;
  -webkit-font-smoothing:antialiased}
.page{position:relative;width:210mm;height:297mm;padding:13mm 14mm 14mm;
  background:#FAF7F0;overflow:hidden;page-break-after:always;break-after:page}
.page:last-child{page-break-after:auto;break-after:auto}
a{color:inherit;text-decoration:none}
.mono{font-family:'IBM Plex Mono',ui-monospace,monospace}
.card{border:1.5px solid #14110F;border-radius:9px;background:#fff;
  box-shadow:3px 3px 0 #14110F;break-inside:avoid}

/* 區塊標題：英文大字＋中文小字 */
.h{display:flex;align-items:baseline;gap:3mm;margin:5mm 0 2.6mm;
  font-family:'Space Grotesk',sans-serif;font-size:15pt;font-weight:700;line-height:1}
.h small{font-family:'Noto Sans TC',sans-serif;font-size:8pt;font-weight:500;color:#3B342E}
.h:first-child{margin-top:0}
.lab{font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:7pt;
  letter-spacing:.18em;color:#6B635B;margin:0 0 2.6mm}

/* ---- 頁首 ---- */
.head{display:grid;grid-template-columns:1fr 31mm;gap:8mm;align-items:center;
  border-bottom:1.5px solid #14110F;padding-bottom:6mm}
.who{display:flex;align-items:center;gap:2.4mm;font-size:10.5pt;font-weight:700}
.who i{width:4.4mm;height:4.4mm;border-radius:1.2mm;background:#FFD34E;border:1.5px solid #14110F}
.who span{font-family:'Space Grotesk',sans-serif;font-weight:500;color:#6B635B}
.title{margin:3mm 0 0;font-size:27pt;font-weight:900;line-height:1.15;letter-spacing:-.01em}
.title mark{background:linear-gradient(transparent 58%,#FFD34E 58%,#FFD34E 92%,transparent 92%);
  color:inherit;padding:0 .08em}
.eyebrow{font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:7.2pt;
  letter-spacing:.2em;color:#3B342E;margin:3.4mm 0 0}
.links{display:flex;flex-wrap:wrap;gap:1.5mm 5mm;margin-top:3.6mm;
  font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:7.8pt}
.links a{font-weight:500;border-bottom:2px solid #FFD34E;padding-bottom:1px}
.links span{color:#3B342E}
.photo{width:31mm;height:31mm;border-radius:50%;border:1.5px solid #14110F;
  box-shadow:1.6mm 1.6mm 0 #FFD34E;overflow:hidden;background:#E9E6DF}
.photo img{display:block;width:100%;height:100%;object-fit:cover}

.summary{margin:5mm 0 0;font-size:8.8pt;line-height:1.8;color:#2C2620}

/* ---- 數據卡 ---- */
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:3.4mm;margin-top:5mm}
.stat{padding:3mm 3.6mm 3.2mm}
.stat-n{font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:15pt;font-weight:500;line-height:1.1}
.stat-n span{font-family:'Noto Sans TC',sans-serif;font-size:7.6pt;font-weight:700;margin-left:1.5px}
.stat-l{font-size:7.4pt;color:#2C2620;margin-top:1.2mm}

/* ---- 職涯 ---- */
.job{display:grid;grid-template-columns:27mm 1fr;gap:0 4mm;padding:3.6mm 4.4mm;margin-bottom:3mm}
.job.now{background:#FFF6DC}
.when{font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:7.4pt;font-weight:500;
  padding-top:.7mm;white-space:nowrap}
.tagp{display:inline-block;margin-top:2mm;border:1.2px solid #14110F;border-radius:999px;
  padding:1px 7px;font-family:'Noto Sans TC',sans-serif;font-size:6.8pt;font-weight:700}
.job h3{margin:0;font-size:10pt;font-weight:900;line-height:1.35}
.job h3 em{font-style:normal;font-weight:500;font-size:8pt;color:#3B342E;margin-left:2.4mm}
.job ul{margin:1.6mm 0 0;padding-left:1.05em}
.job li{font-size:7.9pt;line-height:1.6;color:#2C2620;margin-bottom:.5mm}
.job li:last-child{margin-bottom:0}
.job li b{font-weight:700;color:#14110F;margin-right:.6em}
.job .one{margin:.8mm 0 0;font-size:7.9pt;line-height:1.6;color:#2C2620}
.rows{padding:1.2mm 4.4mm;margin-bottom:0}
.row{display:grid;grid-template-columns:27mm 1fr;gap:0 4mm;padding:2.1mm 0;
  border-top:1px dashed rgba(20,17,15,.28);align-items:baseline}
.row:first-child{border-top:0}
.row p{margin:0;font-size:7.9pt;line-height:1.5;color:#2C2620}
.row p b{font-size:8.4pt;font-weight:900;color:#14110F;margin-right:2mm}
.row p i{font-style:normal;color:#6B635B;margin-right:1.6mm}

/* ---- 案例 ---- */
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:3.2mm}
.case{display:block;padding:3.2mm 4.2mm 3.4mm}
.pill{display:inline-block;border-radius:999px;padding:1.5px 8px;font-size:6.9pt;font-weight:700}
.case h3{margin:1.8mm 0 1.2mm;font-size:10pt;font-weight:900;line-height:1.35}
.case p{margin:0;font-size:7.9pt;line-height:1.6;color:#2C2620;text-wrap:pretty}
.case .res{margin-top:1.4mm;font-weight:700;color:#14110F}
.case .res mark{color:inherit;padding:.5px 3px;-webkit-box-decoration-break:clone;box-decoration-break:clone}

/* ---- 能力卡 ---- */
.skill{padding:3mm 4.2mm 3.2mm}
.skill h3{display:flex;align-items:center;gap:2mm;margin:0;font-size:9.6pt;font-weight:900}
.skill h3 i{font-style:normal;background:#14110F;color:#FAF7F0;border-radius:999px;
  font-family:'Space Grotesk',sans-serif;font-size:6.8pt;font-weight:700;
  min-width:6.4mm;height:4.4mm;display:inline-flex;align-items:center;justify-content:center}
.skill .lead{margin:1.4mm 0 .4mm;font-size:8pt;font-weight:700;line-height:1.55}
.skill .sub{margin:0;font-size:7.6pt;line-height:1.55;color:#2C2620}

.tools{display:flex;flex-wrap:wrap;align-items:center;gap:1.6mm 5mm;margin-top:3.4mm}
.tools > span{display:inline-flex;align-items:center;gap:1.4mm;white-space:nowrap}
.tools b{font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:6.6pt;font-weight:500;
  letter-spacing:.14em;color:#6B635B;margin-right:.6mm}
.chip{border:1.2px solid #14110F;border-radius:999px;padding:1px 7px;font-size:7.2pt;
  font-weight:500;background:#fff;white-space:nowrap}

/* ---- 學歷 ---- */
.edu{display:grid;grid-template-columns:27mm auto 1fr auto;gap:0 4mm;align-items:baseline;
  border-top:1.5px solid #14110F;border-bottom:1.5px solid #14110F;padding:3mm 0}
.edu span{font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:7.4pt;font-weight:500}
.edu b{font-size:9.6pt;font-weight:900}
.edu p{margin:0;font-size:8.2pt;color:#2C2620}
.edu em{font-style:normal;font-size:7.8pt;font-weight:700;background:#F3EFE4;border-radius:999px;padding:1.5px 9px}

/* ---- 競賽／認證／語言 ---- */
.creds{display:grid;grid-template-columns:1.05fr 1.2fr .95fr;gap:7mm;margin-top:4.4mm}
.comp{margin-bottom:1.8mm}
.comp span{display:block;font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:6.8pt;color:#6B635B}
.comp b{display:block;font-size:8pt;font-weight:900;line-height:1.5}
.cert{display:block;width:fit-content;background:#F3EFE4;border-radius:999px;padding:2px 9px;
  font-size:7.5pt;font-weight:700;margin-bottom:1.2mm}
.cert.hl{background:#FFD34E}
.lang{display:flex;align-items:center;gap:2.4mm;margin-bottom:1.8mm;font-size:8pt}
.lang b{flex:0 0 9mm;font-weight:700}
.dots{display:flex;gap:1.1mm}
.dots i{width:2.7mm;height:2.7mm;border-radius:50%;border:1.2px solid #14110F;background:#fff}
.dots i.on{background:#FFD34E}
.lang em{font-style:normal;font-size:7.2pt;color:#6B635B}

/* ---- 聯絡 ---- */
.contact{display:grid;grid-template-columns:1fr auto;gap:6mm;align-items:center;
  margin-top:4mm;background:#14110F;color:#FAF7F0;border-radius:11px;padding:3.8mm 6mm;
  box-shadow:3px 3px 0 #FFD34E}
.contact h3{margin:0 0 2.4mm;font-size:12pt;font-weight:900}
.contact h3 em{font-family:'Space Grotesk',sans-serif;font-weight:700;color:#FFD34E}
.contact .ways{display:flex;flex-wrap:wrap;gap:2mm}
.contact .ways a{border:1.2px solid #FAF7F0;border-radius:999px;padding:2px 10px;
  font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:7.6pt}
.qr{width:17mm;height:17mm;background:#fff;border-radius:2.2mm;padding:1.5mm}
.qr svg{display:block;width:100%;height:100%}

/* 第一頁內容較少，把多出來的留白平均分給各區塊，不要全堆在頁尾 */
.p1 .head{padding-bottom:7mm}
.p1 .summary{margin-top:6mm}
.p1 .stats{margin-top:6mm}
.p1 .h{margin:7.4mm 0 3.6mm}
.p2 .h{margin-top:7mm}
.p2 .h:first-child{margin-top:0}
.p2 .creds{margin-top:6mm}
.p2 .contact{margin-top:7mm}
.p1 .job{padding:4.2mm 4.6mm;margin-bottom:3.4mm}
.p1 .job li{margin-bottom:.9mm}
.p1 .rows{padding:1.6mm 4.6mm}
.p1 .row{padding:2.6mm 0}

.foot{position:absolute;left:14mm;right:14mm;bottom:7mm;display:flex;
  justify-content:space-between;font-family:'IBM Plex Mono',ui-monospace,monospace;
  font-size:6.8pt;color:#6B635B}
"""


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def h2(en, zh):
    return f'<h2 class="h">{esc(en)}<small>{esc(zh)}</small></h2>'


def head_block(photo_uri):
    return f"""<header class="head">
  <div>
    <div class="who"><i></i>{esc(NAME_ZH)}<span>/ {esc(NAME_EN)}</span></div>
    <h1 class="title">{esc(TAGLINE[0])} <mark>{esc(TAGLINE[1])}</mark></h1>
    <p class="eyebrow">{esc(EYEBROW)}</p>
    <div class="links"><a href="{SITE}">{esc(SITE_LABEL)}</a>
      <span>{esc(EMAIL)}</span><span style="font-family:'Noto Sans TC',sans-serif">{esc(AREA)}</span></div>
  </div>
  <div class="photo"><img src="{photo_uri}" alt="{esc(NAME_ZH)}" /></div>
</header>
<p class="summary">{esc(SUMMARY)}</p>"""


def stats_block():
    cells = ''.join(
        f'<div class="card stat" style="background:{bg}"><div class="stat-n">{esc(n)}'
        f'<span>{esc(u)}</span></div><div class="stat-l">{esc(l)}</div></div>'
        for n, u, l, bg in STATS)
    return f'<div class="stats">{cells}</div>'


def jobs_block():
    """現職與 Aicast 各一張卡加條列；盈德一張卡一行；更早的四份併成一張卡，一列一份。"""
    out, rows = [], []
    for when, title, co, kind, pill, items in JOBS:
        if kind == 'row':
            rows.append(f'<div class="row"><div class="when">{esc(when)}</div>'
                        f'<p><b>{esc(title)}</b><i>{esc(co)}</i>{esc(items[0])}</p></div>')
            continue
        tag = ''
        if pill:
            fg = '#FAF7F0' if pill[1] == INK else INK
            tag = f'<br /><span class="tagp" style="background:{pill[1]};color:{fg}">{esc(pill[0])}</span>'
        if kind == 'full':
            body = '<ul>' + ''.join(f'<li>{x}</li>' for x in items) + '</ul>'   # 條列裡有 <b>，不轉義
        else:
            body = f'<p class="one">{esc(items[0])}</p>'
        now = ' now' if when.endswith('現在') else ''
        out.append(f'<div class="card job{now}"><div class="when">{esc(when)}{tag}</div>'
                   f'<div><h3>{esc(title)}<em>{esc(co)}</em></h3>{body}</div></div>')
    out.append(f'<div class="card rows">{"".join(rows)}</div>')
    return ''.join(out)


def cases_block():
    out = []
    for color, kicker, title, call, result, url in CASES:
        out.append(
            f'<a class="card case" href="{SITE + url}">'
            f'<span class="pill" style="background:{color}">{esc(kicker)}</span>'
            f'<h3>{esc(title)}</h3><p>{esc(call)}</p>'
            f'<p class="res"><mark style="background:{color}">{esc(result)}</mark></p></a>')
    return f'<div class="grid2">{"".join(out)}</div>'


def skills_block():
    cards = ''.join(
        f'<div class="card skill" style="background:{bg}"><h3><i>{esc(badge)}</i>{esc(title)}</h3>'
        f'<p class="lead">{esc(lead)}</p><p class="sub">{esc(sub)}</p></div>'
        for badge, bg, title, lead, sub in SKILLS)
    chips = ''.join(f'<span><b>{esc(group)}</b>'
                    + ''.join(f'<span class="chip">{esc(t)}</span>' for t in names) + '</span>'
                    for group, names in TOOLS)
    return f'<div class="grid2">{cards}</div><div class="tools">{chips}</div>'


def edu_block():
    when, school, dept, degree = EDU
    return (f'<div class="edu"><span>{esc(when)}</span><b>{esc(school)}</b>'
            f'<p>{esc(dept)}</p><em>{esc(degree)}</em></div>')


def creds_block():
    comps = ''.join(f'<div class="comp"><span>{esc(y)}</span><b>{esc(t)}</b></div>' for y, t in COMPS)
    certs = ''.join(f'<span class="cert{" hl" if i == 0 else ""}">{esc(n)}</span>'
                    for i, n in enumerate(CERTS))
    langs = ''.join(
        f'<div class="lang"><b>{esc(n)}</b><span class="dots">'
        + ''.join(f'<i class="{"on" if i < lv else ""}"></i>' for i in range(5))
        + f'</span><em>{esc(lab)}</em></div>' for n, lv, lab in LANGS)
    return f"""<div class="creds">
  <div><p class="lab">COMPETITIONS</p>{comps}</div>
  <div><p class="lab">CERTIFICATIONS</p>{certs}</div>
  <div><p class="lab">LANGUAGES</p>{langs}</div>
</div>"""


def contact_block(qr_svg):
    return f"""<div class="contact">
  <div><h3>與我聯絡，<em>say hello</em></h3>
    <div class="ways"><a href="mailto:{EMAIL}">{esc(EMAIL)}</a><a href="{SITE}">{esc(SITE_LABEL)}</a></div></div>
  <a class="qr" href="{SITE}">{qr_svg}</a>
</div>"""


def foot(n, total):
    return (f'<div class="foot"><span>{esc(NAME_ZH)} {esc(NAME_EN)}　·　Resume</span>'
            f'<span>{n:02d} / {total:02d}</span></div>')


def build_html():
    photo = OUT_DIR / 'headshot-2026.jpg'
    uri = 'data:image/jpeg;base64,' + base64.b64encode(photo.read_bytes()).decode()
    qr_svg = (OUT_DIR / 'qr-portfolio.svg').read_text(encoding='utf-8')
    p1 = (head_block(uri) + stats_block()
          + h2('Work Experience', '職涯歷程') + jobs_block() + foot(1, 2))
    p2 = (h2('Featured Case', '精選案例') + cases_block()
          + h2('What I Do', '我能做什麼') + skills_block()
          + h2('Education', '學歷') + edu_block()
          + creds_block() + contact_block(qr_svg) + foot(2, 2))
    pages = ''.join(f'<section class="page p{i}">{p}</section>' for i, p in enumerate((p1, p2), 1))
    return f"""<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8" />
<title>{esc(NAME_ZH)} {esc(NAME_EN)}　產品經理履歷</title>
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;900&family=Space+Grotesk:wght@500;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet" />
<style>{CSS}</style></head><body>{pages}</body></html>"""


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(build_html(), encoding='utf-8')
    print(f'{OUT_HTML.relative_to(ROOT)}　{OUT_HTML.stat().st_size} bytes')
    if '--pdf' not in sys.argv:
        return
    if not pathlib.Path(CHROME).exists():
        sys.exit('找不到 Chrome，無法列印 PDF')
    # virtual-time-budget 是為了等 Google Fonts 下載完才截稿，不然會印出備用字型
    subprocess.run([CHROME, '--headless', '--disable-gpu', '--no-pdf-header-footer',
                    '--virtual-time-budget=20000',
                    f'--print-to-pdf={OUT_PDF}', OUT_HTML.as_uri()],
                   check=True, capture_output=True)
    print(f'{OUT_PDF.relative_to(ROOT)}　{OUT_PDF.stat().st_size} bytes')


if __name__ == '__main__':
    main()
