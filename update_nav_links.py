#!/usr/bin/env python3
"""
Batch-add '白对虾价格监测' nav link to all HTML pages that have the nav-tools link.
Skips files that already have the shrimp-prices.html link.
"""
import os
import re

SITE_DIR = "/Users/johnzhuang/以鲜国际"

NAV_LINK = '<li><a href="shrimp-prices.html" style="background:linear-gradient(135deg,#e74c3c,#c0392b);color:#fff!important;padding:5px 14px;border-radius:20px;font-size:12px;font-weight:700">\U0001F4C8 价格监测</a></li>'

# Pattern: find <li><a href="tools.html" class="nav-tools">...</a></li>
PATTERN = re.compile(r'(<li><a\s+href="tools\.html"\s+class="nav-tools"[^>]*>.*?</a></li>)')

files_updated = []
files_skipped = []

for fname in os.listdir(SITE_DIR):
    if not fname.endswith('.html'):
        continue
    fpath = os.path.join(SITE_DIR, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Skip if already has shrimp-prices.html in nav
    if 'shrimp-prices.html' in content:
        files_skipped.append(fname)
        continue

    # Check if pattern exists
    match = PATTERN.search(content)
    if match:
        old_line = match.group(1)
        new_content = content.replace(old_line, NAV_LINK + '\n    ' + old_line)
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        files_updated.append(fname)
    else:
        files_skipped.append(fname)

print("Updated:", len(files_updated))
for f in files_updated:
    print("  -", f)
print("\nSkipped:", len(files_skipped))
for f in files_skipped:
    print("  -", f)
