"""流量統計（Google Analytics 4）的追蹤碼，首頁與內頁共用這一份。

評估 ID 會出現在網頁原始碼裡，本來就是公開資訊，不需要放進環境變數。
"""

GA_MEASUREMENT_ID = 'G-E1DRLT2NG8'
PRODUCTION_HOST = 'muchang32.github.io'

# 第一段先於 gtag.js 執行：本機預覽與其他網域不送資料，免得自己的預覽被算成流量。
# 第二、三段維持 Google 提供的標準寫法，後台的「代碼偵測」才認得。
GA_SNIPPET = f"""<script>
if (location.hostname !== '{PRODUCTION_HOST}') window['ga-disable-{GA_MEASUREMENT_ID}'] = true;
</script>
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){{dataLayer.push(arguments);}}
gtag('js', new Date());
gtag('config', '{GA_MEASUREMENT_ID}');
</script>"""
