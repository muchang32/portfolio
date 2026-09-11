#!/usr/bin/env python3
"""把 Claude Design 的 .dc.html 轉成可直接部署的 index.html（純 vanilla，無外部 runtime）。
設計母檔仍是 .dc.html；改完設計重跑這支即可。"""
import re, sys, pathlib, html

SRC = pathlib.Path(sys.argv[1]); OUT = pathlib.Path(sys.argv[2])
s = SRC.read_text(encoding='utf-8')

# 1. 取出 helmet 內容（字型與全域 style），移除 dc 包裝與 runtime
helmet = re.search(r'<helmet>(.*?)</helmet>', s, re.S).group(1)
body = s.split('</helmet>',1)[1]
body = body.split('<script type="text/x-dc"',1)[0]
body = body.replace('</x-dc>','').strip()

# 2. sc-if → 在「單一子元素」上加 data-if，避免多包一層破壞 flex/grid
def sc_if(m):
    cond, inner = m.group(1), m.group(2)
    stripped = inner.strip()
    tag = re.match(r'<([a-zA-Z][\w-]*)', stripped)
    # 只有一個頂層元素時直接掛 data-if
    if tag and stripped.count('<'+tag.group(1)) == stripped.count('</'+tag.group(1)+'>'):
        first_end = stripped.index('>')
        head, rest = stripped[:first_end], stripped[first_end:]
        return f'{head} data-if="{cond}" hidden{rest}'
    return f'<div data-if="{cond}" hidden>{inner}</div>'
body = re.sub(r'<sc-if value="\{\{ (\w+) \}\}"[^>]*>(.*?)</sc-if>', sc_if, body, flags=re.S)

# 3. sc-for → template
body = re.sub(r'<sc-for list="\{\{ (\w+) \}\}" as="(\w+)"[^>]*>(.*?)</sc-for>',
              lambda m: f'<template data-for="{m.group(1)}" data-as="{m.group(2)}">{m.group(3)}</template>',
              body, flags=re.S)

# 4. 事件、ref、屬性綁定
body = re.sub(r'onClick="\{\{ (\w+) \}\}"', r'data-on="\1"', body)
body = re.sub(r'href="\{\{ (\w+) \}\}"',  r'href="#" data-href-bind="\1"', body)
body = re.sub(r'(?<![a-zA-Z])ref="\{\{ (\w+) \}\}"', r'data-ref="\1"', body)

# 5. style-hover → 逐一轉成 class + CSS 規則
hovers = []
def hov(m):
    i = len(hovers); hovers.append(m.group(1))
    return f'data-hv="h{i}"'
body = re.sub(r'\s*style-hover="([^"]*)"', hov, body)
hover_css = "\n".join(f'[data-hv="h{i}"]:hover{{{rule}}}' for i, rule in enumerate(hovers))

# 6. 文字內插 {{ x }} → 可綁定 span
body = re.sub(r'\{\{ (\w+) \}\}', r'<span data-bind="\1"></span>', body)

OUT.write_text(helmet + "\n<!--SPLIT-->\n" + hover_css + "\n<!--SPLIT-->\n" + body, encoding='utf-8')
print(f"helmet {len(helmet)}b / hover 規則 {len(hovers)} / body {len(body)}b")
