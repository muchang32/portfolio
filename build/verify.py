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
  ('五篇專欄內頁連結', len(re.findall(r'href="\./writing/\d', h)) == 5),
  ('兩則案例內頁連結', len(re.findall(r'href="\./case/\w+\.html"', h)) == 2),
  ('履歷 PDF', has('assets/resume.pdf', 2)),
  ('Behance 外連', has('behance.net/changmu')),
  ('Cake 外連', has('cakeresume.com')),
  ('無殘留死連結', len(re.findall(r'<a [^>]*href="#"', h)) <= 2),
  # --- 圖片 ---
  ('專欄五張封面', len(re.findall(r'assets/writing/[\w-]+/cover\.jpg', h)) == 5),
  ('平面作品 14 張', len(re.findall(r'_selected/thumb/\d+\.jpg', h)) == 14),
  ('燈箱 14 張', len(re.findall(r'_selected/full/\d+\.jpg', h)) == 14),
  ('AI Lab 兩張截圖', has('ai-lab/01-udn-order-2.jpg') and has('ai-lab/05-my-finance.jpg')),
  ('Aicast 主圖', has('case/aicast/01.jpg')),
  ('iF 獎章', has('if-award-2025.png')),
  ('UI/UX 代表圖', has('design/uiux/cover.jpg')),
  ('SKILLS 十個 logo', len(re.findall(r'assets/logos/opt/', h)) == 10),
  ('站台 logo 與 favicon', has('assets/logo.png') and has('assets/favicon.png')),
  ('OG 分享圖為絕對網址', has('og:image" content="https://')),
  # --- 版面結構 ---
  ('平面作品網格 5 欄', has('repeat(5,minmax(0,1fr))')),
  ('Credentials 三欄', has('[data-grid="creds"]')),
  ('What I Do 用結構選擇器', has('#skills div[style*="border:2px solid #14110F"]:hover')),
  ('無 hidden 殘留在 SVG', not re.search(r'<svg[^>]*\shidden[^>]*>', h)),
  # --- 文案 ---
  ('區塊標題無編號', not re.search(r'>0\d\s*/\s*[A-Z]', h)),
  ('無刊物名稱', absent('聯8達')),
  ('無內網位址', absent('10.20.51')),
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
  ('hover 元素都有過渡', has('[data-hv]{transition:')),
  ('無 React 依賴', absent('unpkg.com') and absent('React.createElement')),
]
for desc, ok in C:
    (fails if not ok else warns).append(desc) if not ok else None

print(f'檢查 {len(C)} 項')
if fails:
    print(f'\n✗ 失敗 {len(fails)} 項：')
    for f in fails: print('  ·', f)
    sys.exit(1)
print('✓ 全數通過')
