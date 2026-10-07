#!/usr/bin/env python3
"""建置後驗證：確認每一項調整都真的套用了。
assemble.py 有 60+ 處字串取代，任何一處比對不到都會無聲失敗——這支讓它出聲。"""
import re, sys, pathlib

h = pathlib.Path('index.html').read_text(encoding='utf-8')
fails, warns = [], []

def need(desc, cond):
    (fails if not cond else []).append(desc) if not cond else None

def has(s, n=1):      return h.count(s) >= n
def absent(s):        return s not in h

C = [
  # --- 連結與素材 ---
  ('八個 AI Lab 專案網址', len(re.findall(r'data-href="https://', h)) == 7),
  ('LiveLingo 保持未上架', h.count('data-href="#"') == 1),
  ('按鈕文字與連結相符', len(re.findall(r'data-link="示範影片 →"', h)) == 1),
  ('LiveLingo 寫出實際導入的場合', has('Mario García') and has('漢來大飯店')),
  ('現職不綁單一場次', 'Mario García' not in h[h.index('id="career"'):h.index('id="case"')]),
  ('現職寫成常態能力', has('自製即時字幕翻譯工具')),
  ('彈窗不講底層技術', absent('AudioWorklet') and absent('PCM16') and absent('Deepgram')),
  ('沒有連結的專案不留死按鈕', has('data-href-bind="labHref" data-if="labHasLink"')
                           and "labHasLink: !!(state.lab" in h),
  ('五篇專欄內頁連結', len(re.findall(r'href="\./writing/\d', h)) == 5),
  ('兩則案例內頁連結', len(re.findall(r'href="\./case/\w+\.html"', h)) == 2),
  ('履歷 PDF', has('assets/resume.pdf', 2)),
  ('轉職鏈 UI / UX → Behance', has('behance.net/changmu')),
  ('轉職鏈 平面設計 → Cake', has('cakeresume.com')),
  ('轉職鏈兩顆都是對話框連結', h.count('class="tip tip-link"') == 2
                             and has('.tip-link:hover')),
  ('設計作品下拉在履歷下載左邊', h.index('data-dropdown') < h.index('履歷下載')
                             and has('data-on="toggleDesign"')),
  ('下拉選項沒有箭頭', not re.search(r'(平面設計|UI / UX) 作品集 ↗', h)),
  ('手機 AI Lab 先顯示 6 張', has('[data-lab-grid]:not([data-expanded])')
                           and has('data-on="toggleLabMore"')),
  ('手指游標已移除', absent('data-handcue')),
  ('設計作品區已移除', absent('id="design"') and absent('_selected/')
                     and absent('design/uiux/') and absent('href="#design"')),
  ('無殘留死連結', len(re.findall(r'<a [^>]*href="#"', h)) <= 2),
  # --- 圖片 ---
  ('專欄五張封面', len(re.findall(r'assets/writing/[\w-]+/cover\.jpg', h)) == 5),
  ('AI Lab 八張卡片封面全到齊',
   len(set(re.findall(r'data-img="\./assets/ai-lab/([\w-]+\.jpg)"', h))) == 8),
  ('彈窗外框與捲動層分開', has('data-modal-scroll') and has('top:-14px;right:-14px')),
  ('換卡時捲回最上方', "box.scrollTop = 0" in h),
  ('AI Lab 旅遊三張排在最後',
   (lambda seg: [t for t in re.findall(r'data-title="([^"]*)"', seg)][-3:]
    == ['Travel Spot 景點自動萃取', '冬富士之旅 2026', '九州縱斷之旅 2026'])
   (h[h.index('id="ai-lab"'):h.index('id="writing"')])),
  ('彈窗封面已綁定', has('data-img-bind="labImg"') and len(re.findall(r'data-img="', h)) == 8),
  ('示範影片有標明素材來源', has('黃仁勳主題演講公開直播') and has('非上述活動現場') and has('data-bind="labVCap"')),
  ('LiveLingo 彈窗放示範錄影',
   has('data-video-bind="labVideo"') and has('02-livelingo-demo.mp4')
   and pathlib.Path('assets/ai-lab/02-livelingo-demo.mp4').exists()),
  ('AI Lab 八張縮圖都有 hover 標記',
   len(re.findall(r'aspect-ratio:16/10[^>]*data-hv="h\d+"|data-hv="h\d+"[^>]*aspect-ratio:16/10', h)) == 8),
  ('Aicast 主圖', has('case/aicast/01.jpg')),
  ('安否通 主圖', has('case/anfu/cover.jpg')),
  ('iF 獎章', has('if-award-2025.png')),
  ('SKILLS 十個 logo', len(re.findall(r'assets/logos/opt/', h)) == 10),
  ('Hero 去背照', has('./assets/avatar.png') and has('fetchpriority="high"')
                and pathlib.Path('assets/avatar.png').exists()),
  ('Hero 有主要行動點', has('href="#case" data-cta') and has('看精選案例 →')
                     and has('[data-cta]:hover')),
  ('Hero 人像舞台已放大', has('width:min(100%,520px);aspect-ratio:1/1.06')),
  ('數據列寬螢幕排成一排', has('[data-stats]{grid-template-columns:repeat(6,1fr) !important}')),
  ('Hero 黃色圓形已縮小', has('inset:14% 12% 6% 12%')
                      and has('[data-hero-ring]{inset:20% 16% 10% 16% !important}')),
  ('Hero 照片在手機不會撐破版面', bool(re.search(r'img\[data-hero\]\{width:\d+% !important\}', h))),
  ('站台 logo 與 favicon', has('assets/logo-84.png') and has('assets/favicon.png')),
  ('導覽列沒有用到 512px 原圖', absent('"./assets/logo.png"')),
  ('OG 分享圖為絕對網址', has('og:image" content="https://')),
  # --- 版面結構 ---
  ('Credentials 三欄', has('[data-grid="creds"]')),
  ('精選案例只有整張卡有 hover',
   len(re.findall(r'data-hv="h\d+"', h[h.index('id="case"'):h.index('id="ai-lab"')])) == 2),
  ('案例按鈕與內文留有間距', h.count('style="margin-top:22px;display:inline-block;') == 2),
  ('沒有重複的 style 屬性', not re.search(r'<[a-z]+[^>]*\sstyle="[^"]*"[^>]*\sstyle="', h)),
  ('What I Do 用結構選擇器', has('#skills div[style*="border:2px solid #14110F"]:hover')),
  ('無 hidden 殘留在 SVG', not re.search(r'<svg[^>]*\shidden[^>]*>', h)),
  # --- 文案 ---
  ('區塊標題無編號', not re.search(r'>0\d\s*/\s*[A-Z]', h)),
  ('無刊物名稱', absent('聯8達')),
  ('無內網位址', absent('10.20.51')),
  ('首頁沒有佔位框', absent('畫面準備中')),
  ('沒有寫給自己看的素材規格', absent('素材待補') and absent('去背半身照')
                           and absent('示範錄影') and absent('產品截圖')),
  ('無學歷', absent('華梵')),
  ('英文為中階', not re.search(r'英文</span>.{0,400}初階', h, re.S)),
  ('數據列六格', len(re.findall(r'data-bind="n\w+"', h)) == 4
                 and len(re.findall(r'data-bind="n\w+">\d', h)) == 4),
  ('iF 無「得主」', absent('設計獎得主')),
  # --- 互動 ---
  ('複製鍵打勾包在 span', has('<span data-copy-done')),
  ('信箱逐字動畫', h.count('class="mailfx"') == 3),
  ('對話框存在', has('tip-bubble')),
  ('輪播循環', has('writingNext') and has('writingPrev')),
  # --- style 屬性完整性（字串注入最常見的破壞方式）---
  ('彈窗面板保有 flex 版面',
   bool(re.search(r'<div style="[^"]*position:relative;background:#fff;[^"]*'
                  r'display:flex;flex-direction:column;gap:14px;animation:riseIn', h))),
  ('沒有被切斷到 data 屬性的樣式',
   not re.search(r'data-[\w-]+="[^"]*(?:display:flex|flex-direction|animation:|'
                 r'box-shadow:|border-radius:)[^"]*"', h)),
  ('hover 元素都有過渡', has('[data-hv]{transition:')),
  ('無 React 依賴', absent('unpkg.com') and absent('React.createElement')),
]
for desc, ok in C:
    (fails if not ok else warns).append(desc) if not ok else None

# 內頁的素材也要跟著檢查
_anfu = pathlib.Path('case/anfu.html').read_text(encoding='utf-8')
C.append(('安否通內頁示範錄影',
          'assets/case/anfu/demo.mp4' in _anfu and 'demo-poster.jpg' in _anfu
          and pathlib.Path('assets/case/anfu/demo.mp4').exists()))
for desc, ok in C[-1:]:
    (fails if not ok else warns).append(desc) if not ok else None

_w1 = pathlib.Path('writing/01-auto-image.html').read_text(encoding='utf-8')
C.append(('專欄頁維持原本樣式',
          'class="kicker"' not in _w1 and 'dl.meta' not in _w1 and 'h2 span{' not in _w1))
C.append(('案例頁的摘要與規格卡',
          'blockquote class="summary"' in _anfu and 'dl.meta' in _anfu
          and _anfu.index('blockquote class="summary"') < _anfu.index('<dl class="meta"')))
C.append(('案例頁沒有星芒分隔線', '2726' not in _anfu))
C.append(('安否通沒有自我評審那段', '自己的評審' not in _anfu and '86 分' not in _anfu))
C.append(('正取公司名稱正確', '睿鍶科技' in _anfu and '睿鍇' not in _anfu))
_ai = pathlib.Path('case/aicast.html').read_text(encoding='utf-8')
C.append(('Aicast 影片自架', 'case/aicast/if-video.mp4' in _ai
          and pathlib.Path('assets/case/aicast/if-video.mp4').exists()
          and pathlib.Path('assets/case/aicast/if-video-poster.jpg').exists()))
C.append(('案例頁完全沒有 YouTube', 'youtube' not in _ai.lower()))
C.append(('影片用原生控制列',
          _ai.count('<video') == 1 and 'controls' in _ai and 'preload="metadata"' in _ai))
for desc, ok in C[-7:]:
    (fails if not ok else warns).append(desc) if not ok else None

print(f'檢查 {len(C)} 項')
if fails:
    print(f'\n✗ 失敗 {len(fails)} 項：')
    for f in fails: print('  ·', f)
    sys.exit(1)
print('✓ 全數通過')
