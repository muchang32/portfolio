# 張詩沂 個人網站

面試用個人網站，部署於 GitHub Pages：<https://muchang32.github.io/portfolio/>

## 結構

```
index.html              首頁（單檔，無外部 runtime）
writing/                五篇《聯8達》專欄內頁（.md 為來源，.html 為產出）
case/                   兩則精選案例內頁
assets/
├── writing/            專欄封面與插圖
├── case/aicast/        Aicast 產品畫面與 iF 獎章
└── design/graphic/_selected/   平面作品 19 張（thumb 網格用、full 燈箱用）
build/                  建置腳本
張詩沂個人網站首頁/        Claude Design 設計母檔（.dc.html）
```

## 改設計之後如何重建

首頁的視覺母檔是 Claude Design 輸出的 `.dc.html`。改完設計後重跑：

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

## 待補素材

- Hero 去背半身照
- AI Lab 八個專案截圖、Travel Spot 與 LiveLingo 的示範錄影
- UI/UX 代表圖（Design Background 左欄）
- `assets/resume.pdf`（導覽列「履歷下載」目前指向此路徑）
- OG 分享縮圖（`og:image` 暫時移除，待去背照到位後補）
