#!/usr/bin/env python3
"""在站内所有带主导航的页面插入「🤝 渠道合作」入口（幂等，可重复执行）

规则：
  - 目标块 = 页面里的 <ul class="nav-links" ...>...</ul>（主导航）
  - 插入位置 = 「以鲜甄选」之后；找不到则退化为插在 </ul> 之前
  - 已含 partner.html 的导航块直接跳过，重复执行不会产生重复项
"""
import os
import re
import sys

SITE_DIR = os.path.dirname(os.path.abspath(__file__))

ITEM = ('<li><a href="partner.html" class="nav-partner" '
        'style="background:linear-gradient(135deg,#0d9488,#00d4aa);color:#06231d!important;'
        'padding:5px 14px;border-radius:20px;font-size:12px;font-weight:800">\U0001F91D 渠道合作</a></li>')

BLOCK = re.compile(r'(<ul class="nav-links"[^>]*>)(.*?)(</ul>)', re.S)
ANCHOR = re.compile(r'<li><a\s+href="products\.html"[^>]*>.*?</a></li>', re.S)


def process(path):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    changed = False

    def repl(m):
        nonlocal changed
        head, inner, tail = m.group(1), m.group(2), m.group(3)
        if "partner.html" in inner:
            return m.group(0)
        anchor = ANCHOR.search(inner)
        if anchor:
            new_inner = inner[:anchor.end()] + "\n    " + ITEM + inner[anchor.end():]
        else:
            new_inner = inner.rstrip() + "\n    " + ITEM + "\n  "
        changed = True
        return head + new_inner + tail

    new_html = BLOCK.sub(repl, html)
    if changed:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_html)
    return changed


def main():
    updated, skipped, no_nav = [], [], []
    for name in sorted(os.listdir(SITE_DIR)):
        if not name.endswith(".html"):
            continue
        path = os.path.join(SITE_DIR, name)
        with open(path, "r", encoding="utf-8") as f:
            has_nav = '<ul class="nav-links"' in f.read()
        if not has_nav:
            no_nav.append(name)
            continue
        (updated if process(path) else skipped).append(name)

    print("已插入渠道合作入口：%d 个" % len(updated))
    for n in updated:
        print("  + " + n)
    print("已存在，跳过：%d 个" % len(skipped))
    for n in skipped:
        print("  = " + n)
    print("无主导航，未处理：%d 个" % len(no_nav))
    for n in no_nav:
        print("  - " + n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
