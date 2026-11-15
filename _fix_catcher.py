# -*- coding: utf-8 -*-
import io, re

h = io.open('index.html', encoding='utf-8').read()
if '__capErr' in h:
    print('catcher already present')
else:
    i = h.index('<body>')
    catcher = (
        "<script>\n"
        "window.__capErr = [];\n"
        "window.addEventListener('error', e => {\n"
        "  const s = String(e.error && e.error.stack || e.message);\n"
        "  window.__capErr.push(s.slice(0, 300));\n"
        "});\n"
        "</script>\n"
    )
    h = h[:i+len('<body>')] + '\n' + catcher + h[i+len('<body>'):]
    io.open('index.html', 'w', encoding='utf-8').write(h)
    print('catcher installed')
