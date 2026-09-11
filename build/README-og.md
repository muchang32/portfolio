# OG 分享圖重新產生

版型：`build/og-card.html`（1200×630，沿用站上的色彩與 logo）

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
  --window-size=1200,630 --virtual-time-budget=6000 \
  --screenshot="$PWD/build/og-raw.png" "file://$PWD/build/og-card.html"

python3 -c "from PIL import Image; Image.open('build/og-raw.png').convert('RGB').save('assets/og-cover.jpg','JPEG',quality=88,optimize=True,progressive=True)"
```

改完文案或想加入去背照，編輯 `og-card.html` 後重跑即可。
