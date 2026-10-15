#!/usr/bin/env python3
"""把個人網站的內容排成可列印的履歷，輸出 build/_pdf/resume.html。

為什麼不直接列印 index.html：網站是一頁式長捲軸，有輪播、收合卡片與彈窗，
列印出來會是一條又長又空的東西。這支用網站同一套視覺（奶油底、亮黃、硬陰影、
同一組字型）重新排成 A4，內容則是履歷該有的密度。

文案與網站共用的部分（職涯條列、案例的問題／判斷／結果、證照、工具）
由 verify.py 逐字比對兩邊，任何一邊改了另一邊沒跟上就會報錯。

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
EYEBROW = 'PRODUCT MANAGER · AI PRACTITIONER · DESIGNER'
TAGLINE = '設計出身的 AI 產品人'
SUMMARY = ('10 年設計積累 × PM 實戰 × AI 工具應用，從需求分析到原型實作，都能自己動手。'
           '我習慣從使用者需求出發，結合產品規劃、跨部門協作與 AI 工具，'
           '把想法轉化成可測試的原型，再透過回饋持續改善，讓解法真正融入工作流程。')

CONTACT = [('信箱', 'mu.chang32@gmail.com'),
           ('地區', '基隆／台北／新北'),
           ('作品集', 'muchang32.github.io/portfolio')]

STATS = [('10', '年', '設計與產品經歷'), ('2025', '', 'iF 設計獎'),
         ('1', '座', '2024 公司年度 MVP'), ('11', '位', '跨職能協作夥伴'),
         ('8', '+ 件', '自製產品')]

# 四張能力卡，與網站 What I Do 同一份文案
SKILLS = [
    ('亮點', 'AI 應用與原型開發', '判斷 AI 該用在哪，然後把想法做出來。',
     ['評估 AI 的適用情境與限制，設計及優化 Prompt 與生成流程',
      '將 AI 應用需求轉化為功能規格、處理邏輯與可執行方案',
      '運用 AI Coding 建立互動式 Web／PWA 原型，加速想法驗證與流程改善']),
    ('01', '產品規劃與需求定義', '把模糊的需求，收斂成可驗證的產品方案。',
     ['透過使用者訪談與回饋分析，釐清痛點及真正需求',
      '將問題拆解為功能需求、使用流程與產品規格',
      '依據使用情境、影響程度與資源限制，排定功能優先順序']),
    ('02', '專案推進與跨部門協作', '讓需求不只停在文件，而是推進到交付。',
     ['拆解工作範圍、交付節點與驗收條件，持續對齊需求與進度',
      '協調設計、工程及外部合作夥伴，確保資訊同步與交付品質',
      '在時程與資源限制下管理優先順序、處理問題並推進成果']),
    ('03', 'UX 設計與體驗驗證', '用設計讓產品更容易理解、操作與驗證。',
     ['規劃資訊架構、使用者流程、Wireframe 與互動原型',
      '將複雜需求轉化為清楚易懂的介面與操作體驗',
      '透過視覺一致性、細節檢查與使用者回饋，持續改善產品體驗']),
]

# 四則案例，問題／判斷／結果與網站逐字相同
CASES = [
    ('#FFD34E', 'Aicast 有聲內容製作平台', '2025 iF 設計獎',
     '把內容製作流程，轉化為更有效率的 AI 有聲內容生產體驗。',
     [('問題', '多角色有聲書的配音與錄音成本過高，多數作品只能由單人朗讀完成'),
      ('判斷', '先把核心的角色辨識與配音修穩，再擴充功能 - 這一層不可信，周邊做再多都留不住人'),
      ('結果', '修復 200+ 個問題並建立測試機制，獲 2025 iF 設計獎')],
     '我負責需求定義、UI 規劃、測試驗證與跨職能外包管理，獎項申請也由我主導。',
     'case/aicast.html'),
    ('#DDEEFF', '自動配圖　從編輯的回饋到產品優化', '聯經數位　新聞編務系統',
     '讓編輯的真實回饋，成為產品優化的依據。',
     [('問題', '自動配圖上線後使用率不如預期，但使用者說的「不好用」不是同一件事'),
      ('判斷', '先訪談再動手 - 把回饋歸納成四類，先修產品可信度，再處理曝光與習慣'),
      ('結果', '排序邏輯重新定義為「相關度＋時效性＋可用性」，搜尋後實際匯入稿單的比例從 3% 提升到 42%')],
     '我負責使用者訪談、問題分類、優化優先順序與圖片排序邏輯定義，技術實作由開發團隊執行。',
     'case/auto-image.html'),
    ('#FFE6E1', 'LiveLingo 即時字幕翻譯', 'Chrome 擴充功能　活動現場導入',
     '把一次性的活動需求，做成可以重複使用的工具。',
     [('問題', '測試了幾款商業工具發現一些限制，因此考慮自行開發'),
      ('判斷', '自己做換到預算可控與完全客製'),
      ('結果', '兩場活動實際使用，獲公司頒發獎金，規劃上架 Chrome 商店')],
     '我負責需求定義、開發、現場測試與調整，以及命名與識別設計。',
     'case/livelingo.html'),
    ('#CDBCFF', '安否通　弱勢機構災情即時回報平台', '數位發展部　全國公民科技試驗場域推廣案',
     '從真實的社會需求出發，設計更即時的災情回報方式。',
     [('問題', '震災後市府逐一撥號清查全部機構，全數確認預估要數小時'),
      ('判斷', '把清查方向反轉 - 系統點名、機構一鍵回報，市府只處理未回報的那幾家'),
      ('結果', '通過文件初審，進入數位發展部徵案決選')],
     '兩人團隊提案，我負責問題定義、流程設計、介面設計與 P0 範圍切分。',
     'case/anfu.html'),
]

JOBS = [
    ('2025/3 – 現在', '資訊管理師', '聯經數位股份有限公司', True,
     ['<b>內部產品優化：</b>主導「自動配圖」功能改版。訪談記者與編輯，把「不好用」歸納成四類問題，'
      '排定優化順序並重新定義圖片排序邏輯，搜尋後實際匯入稿單的比例從 3% 提升到 42%',
      '<b>產品需求規劃：</b>主導 CMS「AI 文生圖」功能規劃，訪談收斂出五項關鍵洞察，將需求分成 '
      'P0／P1／P2 三層，定義從稿件讀取、Prompt 優化到選圖與入稿的完整流程與工程規格；'
      '並將合規納入規格，保存生成紀錄與 Prompt 以利著作權與來源溯源',
      '<b>自製工具落地：</b>獨立開發 LiveLingo Chrome 擴充功能，串接語音辨識與翻譯 API 提供即時字幕，'
      '供公司邀請國際講者來台時使用，兩場活動實際導入',
      '<b>AI 工作流自動化：</b>以 n8n 串接 Claude API（MCP）、解析 JSON 回應串接後段流程，'
      '為新聞自動摘要建立內容檢核；另做一個測試介面，讓編輯不必改動流程或資料就能自行調整 Prompt、'
      '比較效果；另與組內以 Open WebUI 搭公開資料試驗 RAG 查詢',
      '<b>內部推廣與培訓：</b>推動 AI Coding 培訓與實作工作坊，帶非工程背景同仁用 AI 生成工具'
      '做出應用原型，降低導入門檻；於企業內部刊物撰寫 AI 專欄共 5 篇',
      '<b>跨部門專案溝通：</b>將各單位需求轉化為工程與系統可執行的內容']),
    ('2024/5 – 2025/3', '專案經理', '聯經數位股份有限公司　·　Aicast', True,
     ['<b>產品開發與迭代：</b>主持每週兩次 Aicast 產品開發會議，控管開發進度並排除技術阻礙；'
      '依用戶回饋分析測試結果，持續優化操作流程與 UX 體驗',
      '<b>AI 語音專案落地：</b>獨立統籌 30 位以上素人配音員的徵選、簽約與錄音審理；'
      '自學修音技術優化台灣口音 AI 配音模型，提升語音自然度',
      '<b>跨國資源與外包管理：</b>統籌多語系翻譯人員（德、法、日）與平面設計師等外包資源，'
      '管理 9–12 人；主導發包並建置涵蓋 720 首音效的資料庫',
      '<b>國際獎項與視覺統籌：</b>主導產品品牌視覺與參賽策略，親自設計相關多媒體素材，'
      '帶領 Aicast 奪得 2025 年 iF 設計獎。獲公司 2024 年度 MVP']),
    ('2022/8 – 2023/7', '網頁設計師（UI 設計）', '盈德網絡服務有限公司', False,
     ['品牌官網行銷活動 Landing Page 視覺設計、APP 與 Web UI 介面設計、廣告行銷用圖與影片素材製作']),
    ('2019/1 – 2022/4', '網頁企劃視覺設計', '維思資訊股份有限公司', False,
     ['品牌官網所有視覺設計提案與製作、活動企劃提案、廣告素材設計（Facebook／LINE@／Instagram／'
      'Google 多媒體）、平面文宣設計與簡易網頁維護']),
    ('2017/2 – 2019/1', '視覺設計行銷企劃專員', '榭澄有限公司', False,
     ['品牌官網視覺與維護，在職期間單獨執行網頁大改版（Web ＋ 手機版）；'
      '商品拍攝、修圖與合成、商品影片拍攝與剪輯；社群圖文與季節性活動規劃']),
    ('2015/7 – 2017/1', '行銷企劃專員', '橋星企業有限公司', False,
     ['單獨從零架設品牌官網（Shopline 後台建置結構並自訂 CSS）、品牌官網所有視覺設計、'
      '社群經營與文案撰寫、平面文宣設計與數據概略分析']),
    ('2014/10 – 2015/6', '人資專員（兼美編）', '聯興通運股份有限公司　·　實習', False,
     ['維護人力資源紀錄、人員招募甄選與任用、薪酬運算與人事管理報表、公司美編事務']),
]

EDU = ('2010 – 2015', '華梵大學　工業設計學系（時尚設計組）　學士')

COMPS = [('2026', '公民科技協力場　安否通', '數位發展部全國公民科技試驗場域推廣案，兩人團隊提案，負責問題定義、流程設計與 UI／UX'),
         ('2023', '第三屆捷運盃黑客松 UI/UX 設計賽', '自行組隊，負責 UI 與 Wireframe、Mockup、Prototype'),
         ('2022', '獨角獸設計師競賽　PetCare 寵物照護 APP', '兩週完成提案，主責架構、介面與視覺設計')]

CERTS = [('iPAS AI 應用規劃師（初級）', '經濟部產業發展署'),
         ('AI_UX 人工智慧輔助產品體驗設計', '經濟部商業發展署'),
         ('獨角獸設計師養成計劃 Design Jam', 'Unblock'),
         ('丙級電腦軟體設計技術士', '勞動部勞動力發展署'),
         ('Illustrator ・ Photoshop 原廠認證', 'Adobe')]

LANGS = [('中文', 5, '母語'), ('日文', 4, '中上'), ('英文', 3, '中等')]

TOOLS = [('AI', 'Claude ・ ChatGPT ・ Gemini ・ Google Antigravity'),
         ('開發與自動化', 'VS Code ・ n8n ・ API 串接 ・ JSON ・ RAG'),
         ('設計', 'Figma ・ Illustrator ・ Photoshop ・ After Effects ・ Premiere')]

# ===================== 排版 =====================

CSS = """
@page{size:A4;margin:0}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{background:#FAF7F0;color:#14110F;
  font-family:'Noto Sans TC','PingFang TC','Heiti TC',sans-serif;
  -webkit-print-color-adjust:exact;print-color-adjust:exact;
  -webkit-font-smoothing:antialiased}
.page{position:relative;width:210mm;height:297mm;padding:12mm 13mm 10mm;
  background:#FAF7F0;overflow:hidden;page-break-after:always;break-after:page}
.page:last-child{page-break-after:auto;break-after:auto}
a{color:#14110F;text-decoration:none}

/* 小標：跟網站的區塊標籤同一個樣子 */
.lab{font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:7.6pt;
  letter-spacing:.18em;color:#6B635B;margin:0 0 6px}
.rule{height:1.5px;background:#14110F;margin:0 0 7px}
.sec{margin-top:5mm}

/* ---- 頁首 ---- */
.head{display:grid;grid-template-columns:1fr 27mm;gap:7mm;align-items:start;
  border-bottom:1.5px solid #14110F;padding-bottom:6mm}
.eyebrow{font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:7.2pt;
  letter-spacing:.18em;color:#6B635B;margin:0 0 4px}
.name{font-size:27pt;font-weight:900;line-height:1.05;margin:0;letter-spacing:-.01em}
.name small{font-family:'Space Grotesk',sans-serif;font-size:12pt;font-weight:700;
  color:#6B635B;margin-left:8px;letter-spacing:0}
.role{font-size:11pt;font-weight:700;margin:5px 0 0}
.tag{display:inline-block;margin-top:6px;background:#FFD34E;border:1.5px solid #14110F;
  border-radius:999px;padding:3px 11px;font-size:8.6pt;font-weight:700;
  box-shadow:2.5px 2.5px 0 #14110F}
.photo{width:27mm;height:33mm;object-fit:cover;object-position:50% 18%;
  border:1.5px solid #14110F;border-radius:5px}
.contact{margin:7px 0 0;font-size:8.4pt;color:#2C2620;line-height:1.9}
.contact b{font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:7pt;
  letter-spacing:.12em;color:#6B635B;font-weight:500;margin-right:6px}

.summary{margin:5mm 0 0;font-size:9pt;line-height:1.75;color:#2C2620}

/* ---- 數據 ---- */
.stats{display:grid;grid-template-columns:repeat(5,1fr);gap:0;margin:5mm 0 0;
  border-top:1.5px solid #14110F;border-bottom:1.5px solid #14110F;padding:3.5mm 0}
.stats > div{padding:0 3mm;border-left:1px solid rgba(20,17,15,.14)}
.stats > div:first-child{border-left:0;padding-left:0}
.stat-n{font-family:'Space Grotesk',sans-serif;font-size:17pt;font-weight:700;line-height:1}
.stat-n span{font-size:.5em;margin-left:2px;font-weight:500}
.stat-l{font-size:7.4pt;color:#6B635B;margin-top:3px;line-height:1.4}

/* ---- 能力卡 ---- */
.skills{display:grid;grid-template-columns:1fr 1fr;gap:3.4mm;margin-top:3mm}
.skill{position:relative;border:1.5px solid #14110F;border-radius:9px;
  padding:4.6mm 4mm 4mm;background:#fff;box-shadow:3px 3px 0 #14110F;break-inside:avoid}
.skill.hl{background:#FFD34E}
.badge{position:absolute;top:-2.6mm;left:4mm;height:5.2mm;padding:0 2.4mm;border-radius:999px;
  background:#14110F;color:#FAF7F0;font-size:7pt;font-weight:900;
  display:flex;align-items:center;letter-spacing:.02em}
.skill h3{margin:1mm 0 0;font-size:11pt;font-weight:900;line-height:1.35}
.skill .lead{margin:1.6mm 0 2.2mm;font-size:8.2pt;font-weight:500;color:#3B342E}
.skill ul{margin:0;padding-left:1.05em}
.skill li{font-size:8pt;line-height:1.55;color:#2C2620;margin-bottom:.8mm}
.skill.hl,.skill.wide{grid-column:1/-1}
.skill.hl ul,.skill.wide ul{columns:2;column-gap:6mm}

/* ---- 案例 ---- */
.case{display:block;color:#14110F;border:1.5px solid #14110F;border-radius:9px;background:#fff;
  box-shadow:3px 3px 0 #14110F;padding:3.6mm 4mm;margin-bottom:3.2mm;break-inside:avoid}
.case-top{display:flex;align-items:baseline;gap:3mm;margin-bottom:1.4mm}
.case-dot{width:3mm;height:3mm;border-radius:50%;border:1.2px solid #14110F;flex:0 0 auto;
  position:relative;top:.3mm}
.case h3{margin:0;font-size:10.4pt;font-weight:900;line-height:1.3;flex:1}
.case-kicker{font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:6.8pt;
  letter-spacing:.1em;color:#6B635B;white-space:nowrap}
.case .lead{margin:0 0 2mm;font-size:8.2pt;color:#3B342E;font-weight:500}
.pdo{display:grid;grid-template-columns:13mm 1fr;gap:0 2.5mm;
  border-top:1px solid rgba(20,17,15,.13);padding-top:1.8mm}
.pdo dt{font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:7pt;
  letter-spacing:.08em;color:#6B635B;padding:.9mm 0}
.pdo dd{margin:0;font-size:8.1pt;line-height:1.55;padding:.9mm 0}
.pdo .res{font-weight:700}
.case .role{margin:1.8mm 0 0;font-size:7.6pt;color:#6B635B;font-weight:400}
.case .url{font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:6.9pt;color:#6B635B}

/* ---- 職涯 ---- */
.job{display:grid;grid-template-columns:26mm 1fr;gap:0 4mm;padding:1.9mm 0;
  border-top:1px solid rgba(20,17,15,.14);break-inside:avoid}
.job:first-of-type{border-top:0}
.job-when{font-family:'Space Grotesk',sans-serif;font-size:8pt;font-weight:500;color:#6B635B;
  padding-top:.6mm}
.job-when .now{display:inline-block;margin-top:1.4mm;background:#FFD34E;
  border:1.2px solid #14110F;border-radius:999px;padding:1px 5px;font-size:6.8pt;
  font-weight:700;color:#14110F;font-family:'Noto Sans TC',sans-serif}
.job h3{margin:0;font-size:10pt;font-weight:900;line-height:1.3}
.job .co{font-size:8.2pt;color:#6B635B;margin:.6mm 0 1.6mm}
.job ul{margin:0;padding-left:1.05em}
.job li{font-size:8.1pt;line-height:1.5;color:#2C2620;margin-bottom:.8mm}
.job li:last-child{margin-bottom:0}
.job.slim{padding:1.4mm 0}
.job.slim h3{font-size:8.8pt;font-weight:900}
.job.slim h3 em{font-style:normal;font-weight:500;font-size:8pt;color:#6B635B;margin-left:3mm}
.job.slim .one{margin:.5mm 0 0;font-size:7.8pt;line-height:1.55;color:#2C2620}

.comps{display:grid;grid-template-columns:repeat(3,1fr);gap:5mm}
.comp{padding:0;border-top:0}

/* ---- 學習與認證 ---- */
.creds{display:grid;grid-template-columns:1.25fr 1fr 1fr;gap:5mm}
.cred-row{display:grid;grid-template-columns:1fr auto;gap:3mm;font-size:8.1pt;
  padding:1.1mm 0;border-top:1px solid rgba(20,17,15,.12)}
.cred-row:first-of-type{border-top:0}
.cred-row b{font-weight:700}
.cred-row span{font-size:7.4pt;color:#6B635B;white-space:nowrap}
.comp{padding:1.6mm 0;border-top:1px solid rgba(20,17,15,.12)}
.comp:first-of-type{border-top:0}
.comp .y{font-family:'Space Grotesk',sans-serif;font-size:7.4pt;color:#6B635B}
.comp .t{font-size:8.6pt;font-weight:900;margin:.4mm 0}
.comp .d{font-size:7.6pt;color:#3B342E;line-height:1.55}
.pill{display:inline-block;background:#F3EFE4;border-radius:999px;padding:2px 8px;
  font-size:7.8pt;font-weight:700}
.pill.hl{background:#FFD34E}
.lang{display:flex;align-items:center;gap:2.5mm;margin-bottom:2mm}
.lang-n{flex:0 0 11mm;font-size:8pt;font-weight:700}
.bar{flex:1;display:grid;grid-template-columns:repeat(5,1fr);height:3.6mm;
  border:1.2px solid #14110F;border-radius:999px;overflow:hidden}
.bar i{display:block}
.bar i.on{background:#FFD34E}
.bar i:not(:last-child){border-right:1.2px solid #14110F}
.lang-l{flex:0 0 auto;font-size:7.2pt;color:#6B635B}
.tool{display:grid;grid-template-columns:20mm 1fr;gap:3mm;font-size:8pt;padding:1.4mm 0;
  border-top:1px solid rgba(20,17,15,.12)}
.tool:first-of-type{border-top:0}
.tool b{font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:7pt;
  letter-spacing:.1em;color:#6B635B;font-weight:500}
.edu{font-size:8pt;line-height:1.6;padding-top:.6mm}
.edu b{display:block;font-family:'Space Grotesk',sans-serif;font-size:7.4pt;
  font-weight:500;color:#6B635B;margin-bottom:.4mm}

.foot{position:absolute;left:13mm;right:13mm;bottom:6mm;display:flex;
  justify-content:space-between;font-family:'IBM Plex Mono',ui-monospace,monospace;
  font-size:6.8pt;color:#6B635B;border-top:1px solid rgba(20,17,15,.14);padding-top:2mm}
"""


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def head_block(photo_uri):
    rows = ''.join(f'<div><b>{esc(k)}</b>{esc(v)}</div>' for k, v in CONTACT)
    return f'''<header class="head">
  <div>
    <p class="eyebrow">{esc(EYEBROW)}</p>
    <h1 class="name">{esc(NAME_ZH)}<small>{esc(NAME_EN)}</small></h1>
    <p class="role">{esc(ROLE)}</p>
    <div class="tag">{esc(TAGLINE)}</div>
    <div class="contact">{rows}</div>
  </div>
  <img class="photo" src="{photo_uri}" alt="{esc(NAME_ZH)}" />
</header>
<p class="summary">{esc(SUMMARY)}</p>'''


def stats_block():
    cells = ''.join(
        f'<div><div class="stat-n">{esc(n)}<span>{esc(u)}</span></div>'
        f'<div class="stat-l">{esc(l)}</div></div>' for n, u, l in STATS)
    return f'<div class="stats">{cells}</div>'


def skills_block():
    out = []
    for badge, title, lead, items in SKILLS:
        hl = ' hl' if badge == '亮點' else (' wide' if badge == '03' else '')
        lis = ''.join(f'<li>{esc(x)}</li>' for x in items)
        out.append(f'<div class="skill{hl}"><span class="badge">{esc(badge)}</span>'
                   f'<h3>{esc(title)}</h3><p class="lead">{esc(lead)}</p><ul>{lis}</ul></div>')
    return f'<div class="skills">{"".join(out)}</div>'


def cases_block():
    out = []
    for color, title, kicker, lead, pdo, role, url in CASES:
        rows = ''.join(
            f'<dt>{esc(k)}</dt><dd{" class=\"res\"" if k == "結果" else ""}>{esc(v)}</dd>'
            for k, v in pdo)
        out.append(
            f'<a class="case" href="{SITE + url}">'
            f'<div class="case-top"><span class="case-dot" style="background:{color}"></span>'
            f'<h3>{esc(title)}</h3><span class="case-kicker">{esc(kicker)}</span></div>'
            f'<p class="lead">{esc(lead)}</p><dl class="pdo">{rows}</dl>'
            f'<p class="role">{esc(role)}　<span class="url">{esc(SITE + url)}</span></p></a>')
    return ''.join(out)


def jobs_block(jobs):
    """前兩份（現職與 Aicast）條列全寫；其餘五份一行帶過，不然三頁裝不下。"""
    out = []
    for when, title, co, detailed, items in jobs:
        now = '<div class="now">現職</div>' if when.endswith('現在') else ''
        if detailed:
            lis = ''.join(f'<li>{x}</li>' for x in items)   # 條列裡有 <b>，不轉義
            body = f'<h3>{esc(title)}</h3><p class="co">{esc(co)}</p><ul>{lis}</ul>'
            out.append(f'<div class="job"><div class="job-when">{esc(when)}{now}</div>'
                       f'<div>{body}</div></div>')
        else:
            out.append(f'<div class="job slim"><div class="job-when">{esc(when)}</div>'
                       f'<div><h3>{esc(title)}<em>{esc(co)}</em></h3>'
                       f'<p class="one">{esc(items[0])}</p></div></div>')
    return ''.join(out)


def comps_block():
    cells = ''.join(f'<div class="comp"><div class="y">{esc(y)}</div>'
                    f'<div class="t">{esc(t)}</div><div class="d">{esc(d)}</div></div>'
                    for y, t, d in COMPS)
    return f'<div class="comps">{cells}</div>'


def creds_block():
    certs = ''.join(f'<div class="cred-row"><div><span class="pill{" hl" if i == 0 else ""}">'
                    f'{esc(n)}</span></div><span>{esc(org)}</span></div>'
                    for i, (n, org) in enumerate(CERTS))
    langs = ''.join(
        '<div class="lang"><span class="lang-n">' + esc(n) + '</span><span class="bar">'
        + ''.join(f'<i class="{"on" if i < lv else ""}"></i>' for i in range(5))
        + f'</span><span class="lang-l">{esc(lab)}</span></div>' for n, lv, lab in LANGS)
    tools = ''.join(f'<div class="tool"><b>{esc(k)}</b><div>{esc(v)}</div></div>'
                    for k, v in TOOLS)
    return f'''<div class="creds">
  <div><p class="lab">CERTIFICATIONS</p><div class="rule"></div>{certs}</div>
  <div>
    <p class="lab">LANGUAGES</p><div class="rule"></div>{langs}
    <div class="sec"><p class="lab">EDUCATION</p><div class="rule"></div>
      <div class="edu"><b>{esc(EDU[0])}</b>{esc(EDU[1])}</div></div>
  </div>
  <div><p class="lab">TOOLS</p><div class="rule"></div>{tools}</div>
</div>'''


def foot(n, total):
    return (f'<div class="foot"><span>{esc(NAME_ZH)} {esc(NAME_EN)}　·　{esc(ROLE)}</span>'
            f'<span>{SITE}　·　{n} / {total}</span></div>')


def build_html():
    photo = OUT_DIR / 'headshot.jpg'
    uri = 'data:image/jpeg;base64,' + base64.b64encode(photo.read_bytes()).decode()
    p1 = (head_block(uri) + stats_block()
          + '<div class="sec"><p class="lab">WHAT I DO　我能做什麼</p><div class="rule"></div>'
          + skills_block() + '</div>'
          + '<div class="sec"><p class="lab">COMPETITIONS　競賽與提案</p><div class="rule"></div>'
          + comps_block() + '</div>' + foot(1, 3))
    p2 = ('<p class="lab">FEATURED CASE　精選案例</p><div class="rule"></div>'
          + cases_block() + foot(2, 3))
    p3 = ('<p class="lab">WORK EXPERIENCE　職涯歷程</p><div class="rule"></div>'
          + jobs_block(JOBS)
          + '<div class="sec"><p class="lab">CREDENTIALS　學習與認證</p><div class="rule"></div>'
          + creds_block() + '</div>' + foot(3, 3))
    pages = ''.join(f'<section class="page">{p}</section>' for p in (p1, p2, p3))
    return f'''<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8" />
<title>{esc(NAME_ZH)} {esc(NAME_EN)}　產品經理履歷</title>
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;900&family=Space+Grotesk:wght@500;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet" />
<style>{CSS}</style></head><body>{pages}</body></html>'''


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
