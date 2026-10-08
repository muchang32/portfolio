# 手機版實作規格（給 Claude Code）

> 來源設計稿：`手機版設計提案.dc.html`（每段「現況／提案／實作提示」三欄對照）
> 目標檔案：現行網站 `index.html`（https://muchang32.github.io/portfolio/）
> 範圍：**只動手機版（≤640px）**。桌機與平板外觀必須維持不變。

---

## 0. 原則與限制

1. **不換結構、不重寫 HTML。** 建置流程有 123 處字串比對綁在現有結構上。只允許：
   - 新增 `data-*` 屬性
   - 新增極少量包裹元素（下文逐項列出）
   - 在 `<style>` 新增 media query
   - 新增少量原生 JS（優先用 `<details>`／`<summary>`，能不用 JS 就不用）
2. 站點幾乎全為 inline style，樣式表要覆蓋**一律加 `!important`**。
3. 斷點：
   - `@media (max-width:640px)`：手機主斷點（沿用現有）
   - `@media (max-width:560px)`：只用於 Credentials（沿用現有 `[data-grid="creds"]`）
4. 文案不改字。唯一例外是 §4 精選案例的**手機專用短版簡介**（已經使用者確認）。
5. 不新增：登入、表單、第三方腳本、自動播放輪播或影片。
6. 觸控目標最小 44×44。
7. 橫向溢出必須維持 0。
8. 必須沿用、不可破壞的既有手機調整：
   - 漢堡選單全屏、「設計作品」第二層
   - Hero 人像寬 108%，黃色圓形 inset 縮一階，頭頂凸出
   - 專欄輪播的箭頭在下方置中、卡片吃滿寬度（`[data-carousel]`）
   - AI Lab 先顯示 6 張＋「看更多作品 ↓」（`[data-lab-more]`）
   - 轉職鏈 hover 對話框在 ≤640px 隱藏

---

## 1. 全站：手機標題樣式（段落節奏）

**目標：** 九段的「英文大標＋中文副標」在手機改為靠左，並加上章節編號與細線，讓讀者知道換段了。

**HTML：** 每段標題容器（`section[id] > div > div:first-child`）加上 `data-chapter`：

| section id | data-chapter |
|---|---|
| （Hero 不加） | — |
| `about` | `02 / 09` |
| `career` | `03 / 09` |
| `case` | `04 / 09` |
| `ai-lab` | `05 / 09` |
| `writing` | `06 / 09` |
| `skills` | `07 / 09` |
| `learning` | `08 / 09` |
| `contact` | `09 / 09` |

**CSS：**
```css
@media (max-width:640px){
  [data-chapter]{text-align:left!important;margin-left:0!important;margin-right:0!important}
  [data-chapter]::before{
    content:attr(data-chapter);
    display:flex;align-items:center;gap:10px;margin-bottom:12px;
    font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.16em;color:#6B635B;
    /* 右側細線 */
    background:linear-gradient(rgba(20,17,15,.18),rgba(20,17,15,.18)) no-repeat right center/calc(100% - 64px) 1px;
  }
  [data-chapter] h2{font-size:34px!important;line-height:1.1!important;margin-bottom:4px!important}
  [data-chapter] h2 + p{font-size:15px!important}
}
```

---

## 2. Hero ＋ 數據（目標高度 ≈1,100px）

### 2.1 版面順序
手機順序改為：**Eyebrow → H1 →〔人像〕→ 副標 → CTA → 數據**。
人像要剛好在標題下方，讓人物抬起的手指向上方的「設計出身的 AI 產品人」。

**HTML（最小改動）：**
- Hero 左欄 `div` 加 `data-hero-copy`
- H1 加 `data-hero-title`
- 副標 `<p>` 加 `data-hero-sub`
- CTA 外層 flex 容器加 `data-hero-cta`
- 人像右欄 `div` 加 `data-hero-photo`

**CSS：**
```css
@media (max-width:640px){
  /* 攤平左欄，讓人像能插進 h1 與副標之間 */
  main#top > section:first-child{display:flex!important;flex-direction:column!important;gap:0!important}
  [data-hero-copy]{display:contents}
  [data-hero-copy] > p:first-child{order:1;line-height:1.8!important;white-space:normal!important}  /* eyebrow 可換行 */
  [data-hero-title]{order:2;margin-bottom:0!important}
  [data-hero-photo]{order:3;margin:6px 0 0!important}
  [data-hero-sub]{order:4;margin-top:22px!important}
  [data-hero-cta]{order:5}
  /* 黃色圓略偏右，讓手部落在左上方 */
  [data-hero-photo] [data-hero-circle]{left:11%!important;right:6%!important}
}
```
> 黃色圓形元素加 `data-hero-circle`。實際偏移量請以真實人像微調：手指尖應落在 H1 第二行左下方附近。

### 2.2 CTA
- 「看精選案例 →」手機隱藏：`[data-cta]{display:none!important}`
- 留下「信箱膠囊＋圓形複製鍵」同列：
```css
@media (max-width:640px){
  [data-hero-cta]{display:flex!important;flex-wrap:nowrap!important;gap:10px!important}
  [data-hero-cta] .mailfx{flex:1;min-width:0;height:50px;justify-content:center}
  [data-hero-cta] [data-copybtn]{flex:0 0 50px;height:50px;border-radius:50%}
}
```

### 2.3 數據六格
3×2 網格，**不加任何分隔線**：
```css
@media (max-width:640px){
  [data-stats]{grid-template-columns:repeat(3,1fr)!important;gap:20px 12px!important;padding-top:28px!important}
  [data-stats] > div{padding:0!important;border-left:0!important}
  [data-stats] > div > div:first-child{font-size:24px!important}
  [data-stats] > div > div:last-child{font-size:11.5px!important}
}
```

---

## 3. About Me ＋ 獎項帶（目標 ≈1,000px，收合時）

### 3.1 內文收合
- 只露出前三段，到「於是，我開始往產品的上游走。」為止。
- 第 4–7 段包進 `<div data-about-more>`，後面接按鈕。
- 按鈕文案：收合時「繼續閱讀 ↓」，展開時「收合 ↑」。
- 按鈕樣式：文字按鈕，黃色底線，高 44px。

```html
<div data-about-more> …第 4–7 段… </div>
<button type="button" data-about-toggle aria-expanded="false">繼續閱讀 ↓</button>
```
```css
[data-about-toggle]{display:none}
@media (max-width:640px){
  [data-about-toggle]{display:inline-flex;align-items:center;height:44px;border:0;background:none;
    font:700 14.5px 'Noto Sans TC';border-bottom:2px solid #FFD34E;padding:0 4px}
  [data-about-more]:not(.open){display:none}
}
```

### 3.2 轉職鏈
三個膠囊在 390px 必須同一行：
- 字級 12.5px、高 34px、左右 padding 12px
- 「平面設計」與「UI / UX」用灰底 `#E8E4DC`；「產品管理」黃底加框（沿用）

### 3.3 SOP 引言卡
- 與內文同寬的卡片，**不要滿版**。
- 只露出主句「產品沒有一套可以完美複製的 SOP。」，右側放 44px 圓形「+」鈕（黃底黑框），點開才顯示說明段落。
- 建議用 `<details>` 實作：

```html
<details data-quote>
  <summary>產品沒有一套可以完美複製的 SOP。<span aria-hidden="true"></span></summary>
  <p>每一個產品、每一項功能……找到當下最適合的解法。</p>
</details>
```
```css
@media (max-width:640px){
  [data-quote]{background:#FFF6D9;border:2px solid #14110F;border-radius:18px;box-shadow:4px 4px 0 #14110F;margin:30px 0 0}
  [data-quote] summary{list-style:none;display:flex;align-items:center;gap:10px;padding:16px 12px 16px 18px;
    font-size:17px;font-weight:900;line-height:1.55;cursor:pointer}
  [data-quote] summary::-webkit-details-marker{display:none}
  [data-quote] summary span{flex:0 0 44px;height:44px;border-radius:50%;background:#FFD34E;border:2px solid #14110F;
    display:grid;place-items:center;margin-left:auto}
  [data-quote] summary span::before{content:"+";font-weight:700;font-size:18px}
  [data-quote][open] summary span::before{content:"−"}
  [data-quote] p{padding:0 18px 18px;margin:0;font-size:14px;line-height:1.85}
}
```
> 桌機必須維持原本「永遠展開」的樣子：≥641px 時讓 `<p>` 永遠顯示，並把 summary 的 `+` 隱藏（或桌機直接在 JS 中把 `details` 設為 `open`，並禁止點擊收合）。

### 3.4 獎項帶
`#about` 後面的 `section`（背景 `#F3EFE4`）內層容器在手機改為 2×2：
```css
@media (max-width:640px){
  #about + section > div{display:grid!important;grid-template-columns:1fr 1fr;gap:12px 10px!important;justify-content:stretch!important}
  #about + section > div > span{font-size:13px!important}
}
```

---

## 4. Work Experience（目標 ≈1,050px，預設狀態）

- **手風琴：**
  - 現職（資訊管理師）預設展開。
  - 其餘只露標題列：日期＋徽章／職稱／公司。
  - 每列右側放 44px 圓形 `+`／`−` 鈕。
- **一次只展開一張**：用 JS 處理；改用 `<details>` 則允許多張同時展開，也可接受。
- 手機拿掉左側虛線時間軸與圓點，卡片吃滿寬度。
- 技能標籤改單行橫向捲動，並隱藏捲軸。
- 「展開完整經歷 ↓」沿用。早期四份經歷展開後先以**精簡列**呈現（日期／職稱／公司），點開才看條列。

**HTML：**
- 時間軸容器加 `data-timeline`
- 每張卡 `article` 加 `data-job`
- 標題區（日期列、h3、公司）包進 `<div data-job-head>`
- 條列 `ul`、標籤列、「看完整案例」包進 `<div data-job-body>`

```css
@media (max-width:640px){
  #career [data-timeline]{border-left:0!important;padding-left:0!important}
  #career [data-job] > span:first-child{display:none!important}   /* 時間軸圓點 */
  [data-job-head]{position:relative;padding-right:56px;min-height:44px;cursor:pointer}
  [data-job-head]::after{content:"+";position:absolute;right:0;top:0;width:44px;height:44px;border-radius:50%;
    border:2px solid #14110F;background:#fff;display:grid;place-items:center;font-weight:700}
  [data-job].open [data-job-head]::after{content:"−"}
  [data-job]:not(.open) [data-job-body]{display:none}
  [data-job-body] .tags{flex-wrap:nowrap!important;overflow-x:auto;scrollbar-width:none}
}
```
```js
// 只在手機啟用；預設第一張 .open
const mq = matchMedia('(max-width:640px)');
document.querySelectorAll('[data-job-head]').forEach(h => h.addEventListener('click', () => {
  if (!mq.matches) return;
  const card = h.closest('[data-job]'), willOpen = !card.classList.contains('open');
  document.querySelectorAll('[data-job].open').forEach(c => c.classList.remove('open'));
  if (willOpen) card.classList.add('open');
}));
document.querySelector('[data-job]')?.classList.add('open');
```

---

## 5. Featured Case（目標 ≈880px）

### 5.1 版面
- 兩張卡改**橫向滑動**：卡寬 82%，露出下一張的邊緣，scroll-snap。
- 卡內版面改單欄：圖片 16:10 在上，文字在下。
- 六個標籤在手機隱藏（`data-case-tags`）。
- 下方加兩個位置點（可選；做的話要隨捲動更新 active 點）。

### 5.2 手機專用短版簡介（已確認的文案變更）
- 卡內原本兩段，手機只顯示一段短版；桌機顯示原文，不變。
- 原文第一段（情境描述）加 `data-case-long`，手機隱藏。
- 第二段加 `data-case-short-src`。若原文第二段與下表一致，可直接沿用該段，不需要另外新增元素。

| 卡片 | 手機顯示文字（一字不改） |
|---|---|
| Aicast | 負責需求定義、UI 規劃、測試驗證與跨職能外包管理，並主導申請**2025 iF 設計獎**。 |
| 安否通 | 兩人團隊提案，通過文件初審並進入**數位發展部徵案決選**。我負責問題定義、流程設計、介面設計與 P0 範圍切分。 |

> 粗體保留原站的螢光筆樣式：Aicast 黃底 `#FFD34E`、安否通紫底 `#CDBCFF`。
> 第一張的原文是「我負責…」，手機版開頭**沒有**「我」，請用上表字串。

```css
@media (max-width:640px){
  [data-cases]{display:flex!important;flex-direction:row!important;overflow-x:auto;scroll-snap-type:x mandatory;
    gap:12px!important;margin:0 -16px;padding:4px 16px 12px;scroll-padding:0 16px;scrollbar-width:none}
  [data-cases] > article{flex:0 0 82%;scroll-snap-align:start;grid-template-columns:1fr!important;padding:12px 12px 18px!important}
  [data-case-long],[data-case-tags]{display:none!important}
  [data-cases] h3{font-size:19px!important}
}
```

---

## 6. AI Lab（目標 ≈900px）

- 改兩欄網格：圖片裁成 1:1（`object-fit:cover`），**只留標題**（14px，900 字重），說明文字在手機隱藏。
- 沿用「先 6 張＋看更多作品 ↓」。
- **點開後：畫面中央的彈窗**（不要從底部滑出）：

| 項目 | 規格 |
|---|---|
| 遮罩 | `position:fixed; inset:0; background:rgba(20,17,15,.6)`，內容置中 |
| 卡片寬度 | `calc(100vw - 32px)`，最大高度 `calc(100vh - 40px)`，超出時內部捲動 |
| 外觀 | 2.5px 黑框、圓角 22px、硬陰影 `6px 6px 0 #14110F` |
| 內容順序 | 圖片 4:3（下緣 2px 黑線）→ 標題 20px → 說明 14px → 「開啟網頁 →」／「示範影片 →」按鈕（48px 高） |
| 關閉 | 右上 44px 圓形 × 鈕；點遮罩關閉；Esc 關閉 |
| 捲動 | 開啟時鎖定 body 捲動，關閉後還原 |

```css
@media (max-width:640px){
  #ai-lab [data-lab-grid]{grid-template-columns:1fr 1fr!important;gap:20px 12px!important}
  #ai-lab [data-lab-grid] img{aspect-ratio:1/1;object-fit:cover;border-radius:14px}
  #ai-lab [data-lab-grid] p{display:none!important}
  #ai-lab [data-lab-grid] h3{font-size:14px!important;line-height:1.45!important}
}
```
> 卡片網格容器加 `data-lab-grid`。若現有彈窗已是置中樣式，只需確認上表的手機尺寸與關閉行為。

---

## 7. Writing（目標 ≈600px，大致維持）

- 沿用現有 `[data-carousel]` 手機樣式。
- 只套用 §1 的標題樣式。
- 可選：箭頭中間加位置提示「1 / 5」（IBM Plex Mono 13px），隨捲動更新。

---

## 8. What I Do（目標 ≈800px，收合時）

- **04 AI 落地與原型實作**移到最上方，完整展開（黃底卡）。
- **01–03 改摺疊列**：
  - 收合時只顯示：黑色圓形編號（32px）、標題（17px，900 字重）、一句話（12.5px）、右側 44px 的 `+`
  - 點開後顯示條列與工具標籤
- 每張卡保留各自的底色：01 `#DDEEFF`／02 `#EDE6FF`／03 `#FFE6E1`。

**HTML：**
- 卡片容器加 `data-skills`
- 每張卡加 `data-skill="01|02|03|04"`
- 01–03 的標題區加 `data-skill-head`

```css
@media (max-width:640px){
  #skills [data-skills]{display:flex!important;flex-direction:column;gap:10px!important}
  #skills [data-skill="04"]{order:-1;margin-bottom:8px}
  #skills [data-skill]:not([data-skill="04"]):not(.open) ul,
  #skills [data-skill]:not([data-skill="04"]):not(.open) [data-tags]{display:none!important}
  #skills [data-skill-head]{position:relative;padding-right:52px;min-height:44px;cursor:pointer}
  #skills [data-skill-head]::after{content:"+";position:absolute;right:0;top:50%;transform:translateY(-50%);
    width:44px;height:44px;display:grid;place-items:center;font-weight:700}
  #skills [data-skill].open [data-skill-head]::after{content:"−"}
}
```
JS 與 §4 相同模式：手機才啟用，一次只開一張，預設全部收合。

---

## 9. Credentials（目標 ≈520px）

- 四類改**分段切換**，順序為：競賽／證照／語言／工具。
- 頁籤列的樣式：
  - 四欄等寬，膠囊外框（底色 `#F3EFE4`，內距 4px）
  - 每顆按鈕高 40px；含外框約 48px，符合觸控尺寸
  - 選中狀態：黑底 `#14110F`、米白字
- 預設顯示「競賽」。
- 手機隱藏各區原本的小標（COMPETITIONS…），由頁籤取代。

**HTML：**
- 在 `[data-grid="creds"]` 前面插入 `<div data-cred-tabs role="tablist">…4 個 button…</div>`
- 四個子區塊加 `data-cred="comp|cert|lang|skill"`

```css
[data-cred-tabs]{display:none}
@media (max-width:560px){
  [data-cred-tabs]{display:grid;grid-template-columns:repeat(4,1fr);gap:4px;background:#F3EFE4;border-radius:999px;padding:4px;margin-bottom:22px}
  [data-cred-tabs] button{height:40px;border:0;border-radius:999px;background:transparent;font:700 13px 'Noto Sans TC';color:#14110F}
  [data-cred-tabs] button[aria-selected="true"]{background:#14110F;color:#FAF7F0}
  [data-grid="creds"] > [data-cred]:not(.active){display:none!important}
  [data-grid="creds"] > [data-cred] > p:first-child{display:none!important}
}
```
> 第一次載入時，`comp` 頁籤與 `[data-cred="comp"]` 都要預設為 active。

---

## 10. Contact（≈340px）

- 信箱膠囊吃滿寬度（高 52px），右側放 52px 圓形複製鍵（黑底、黃色硬陰影）。這和 Hero 的 CTA 是同一組元件。
- 標題：「與我聯絡，」34px／「Say hello with me ☺」30px，Space Grotesk 斜體。
- 頁尾兩行靠左。

```css
@media (max-width:640px){
  #contact [data-contact-cta]{display:flex!important;gap:10px!important;width:100%}
  #contact [data-contact-cta] .mailfx{flex:1;min-width:0;height:52px;justify-content:center}
  #contact [data-contact-cta] [data-copybtn]{flex:0 0 52px;height:52px;border-radius:50%}
}
```

---

## 11. 驗收標準

在 390×844（iPhone 14）與 375×667（iPhone SE）各測一次：

- [ ] 整頁高度 ≤ 7,600px（目前 12,093px）
- [ ] 各段高度大致符合各節標的目標值（±15%）
- [ ] 橫向溢出 = 0：`document.documentElement.scrollWidth === innerWidth`
- [ ] 所有可點元素 ≥ 44×44
- [ ] 九段內容都在，可透過展開或切換看到全部原文（§5 短版例外）
- [ ] ≥641px 與修改前像素一致（可截圖比對 1440 與 900 寬）
- [ ] 鍵盤操作：所有展開鈕、頁籤可用 Tab 聚焦，Enter／Space 可觸發；彈窗可用 Esc 關閉
- [ ] 展開類元件都有正確的 `aria-expanded`，頁籤有 `role="tab"` 與 `aria-selected`
- [ ] `prefers-reduced-motion` 下沒有動畫
- [ ] 123 處字串比對的建置流程仍可通過

---

## 12. 新增的 data 屬性一覽

| 屬性 | 位置 | 用途 |
|---|---|---|
| `data-chapter` | 各段標題容器 | 手機標題樣式＋章節編號 |
| `data-hero-copy` / `-title` / `-sub` / `-cta` / `-photo` / `-circle` | Hero | 手機重排 |
| `data-about-more` / `data-about-toggle` | About | 內文收合 |
| `data-quote` | About SOP 卡 | `<details>` 收合 |
| `data-timeline` / `data-job` / `data-job-head` / `data-job-body` | Career | 手風琴 |
| `data-cases` / `data-case-long` / `data-case-tags` | Case | 橫向滑動、短版 |
| `data-lab-grid` | AI Lab | 兩欄網格 |
| `data-skills` / `data-skill` / `data-skill-head` / `data-tags` | What I Do | 排序與摺疊 |
| `data-cred-tabs` / `data-cred` | Credentials | 分段切換 |
| `data-contact-cta` | Contact | CTA 版面 |

既有、繼續沿用：`data-stats`、`data-cta`、`data-copybtn`、`data-carousel`、`data-slider`、`data-lab-more`、`data-grid="creds"`、`.mailfx`。
