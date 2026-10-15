# 張詩沂 個人網站

面試用個人網站，部署於 GitHub Pages：<https://muchang32.github.io/portfolio/>

## 結構

```
index.html              首頁（單檔，無外部 runtime，CSS 與 JS 全部內嵌）
case/                   四則精選案例內頁（.md 為來源，.html 為產出）
writing/                五篇《聯8達》專欄內頁（同上）
assets/
├── avatar.png          Hero 去背半身照
├── og-cover.jpg        分享縮圖
├── resume.pdf          履歷（由 build/resume_pdf.py 產生，見下）
├── case/               四則案例的封面與內頁素材
├── writing/            專欄封面與插圖
├── ai-lab/             AI Lab 八個專案的截圖與示範影片
├── logos/opt/          SKILLS 的工具 logo（opt 是壓過的，站上用這組）
└── design/graphic/_selected/   平面作品（thumb 網格用、full 燈箱用）
build/                  建置腳本
張詩沂個人網站首頁/        Claude Design 設計母檔（.dc.html）── 首頁的視覺來源，不要刪
design-handoff/         手機版改版時給設計的交付包（歷史資料，站上不引用）
```

## 建置

首頁的視覺母檔是 Claude Design 輸出的 `.dc.html`，改完設計後重跑：

```bash
python3 build/convert.py "張詩沂個人網站首頁/張詩沂個人網站.dc.html" build/_parts.txt
python3 build/assemble.py
```

`convert.py` 把 `sc-if` / `sc-for` / `{{ }}` / `style-hover` 轉成標準 HTML；
`assemble.py` 接上連結、素材、meta，並內嵌 `build/app.js`（取代 React runtime）。

內頁由 markdown 產生：

```bash
python3 build/pages.py
```

履歷 PDF 由網站同一套視覺排版後，用 Chrome headless 列印：

```bash
python3 build/resume_pdf.py --pdf
```

最後一定要跑驗證。`assemble.py` 有 60+ 處字串取代，任何一處比對不到都會無聲失敗，
這支讓它出聲（目前 123 項，失敗會回非零）：

```bash
python3 build/verify.py
```

## 注意

- **repo 是公開的**，GitHub Pages 直接從 `main` 部署。放進版控的東西等於上線，
  求職文件（`resume/`）、規劃文件與大型素材都在 `.gitignore` 裡。
- 履歷 PDF 與網站共用十餘句文案（成效數字、案例結果、能力卡、語言程度），
  `verify.py` 會逐字比對兩邊。改了網站就要重跑 `resume_pdf.py --pdf`，否則驗證不會過。
