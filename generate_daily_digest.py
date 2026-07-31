import json
import os
import re
from datetime import datetime

# Configuration
TODAY = '2026-07-31'
OUTPUT_DIR = '/Users/johnzhuang/老庄浅谈/2026年7月/公众号'
SOURCE_URL = 'www.efsupplychain.com/reports.html'

# Load data
with open('/Users/johnzhuang/以鲜国际/demo_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Categorize today's entries
today_items = {
    'news': [i for i in data.get('news', []) if i.get('date') == TODAY],
    'events': [i for i in data.get('events', []) if i.get('date') == TODAY],
    'policies': [i for i in data.get('policies', []) if i.get('date') == TODAY],
    'reports': [i for i in data.get('reports', []) if i.get('date') == TODAY],
}

# Get latest previous entries for review context
def get_latest_prev(section, today_items_list):
    candidates = [i for i in data.get(section, []) if i.get('date') != TODAY]
    # Sort by date descending, then by id descending
    def sort_key(i):
        return (i.get('date', ''), i.get('id', ''))
    candidates.sort(key=sort_key, reverse=True)
    return candidates[:2] if candidates else []


def split_sentences(text):
    """Split Chinese text into sentences, handling common punctuation."""
    if not text:
        return []
    # Split by Chinese sentence endings
    parts = re.split(r'(?<=[。！？；])\s*', text)
    return [p.strip() for p in parts if p.strip()]


def extract_analysis(content):
    """Extract the 以鲜国际分析 section from content."""
    markers = ['以鲜国际分析：', '以鲜国际分析', '【以鲜国际分析】']
    for marker in markers:
        idx = content.find(marker)
        if idx != -1:
            return content[idx + len(marker):].strip()
    return content.strip()


def make_summary_points(item):
    """Generate 2-3 summary bullet points from summary + content."""
    summary = unescape_content(item.get('summary', ''))
    sentences = split_sentences(summary)
    if len(sentences) >= 3:
        return sentences[:3]
    # Fallback to content first few sentences
    content = unescape_content(item.get('content', ''))
    content_sents = split_sentences(content)
    combined = sentences + content_sents
    return combined[:3]


def unescape_content(text):
    """Convert literal escape sequences (\\n, \\t) in parsed strings to actual characters."""
    return text.replace('\\n', '\n').replace('\\t', '\t').replace('\\r', '\r')


def clean_text(text):
    """Clean up newlines and extra spaces."""
    text = text.replace('\n', ' ').strip()
    text = re.sub(r'\s+', ' ', text)
    return text


def extract_analysis(raw_content):
    """Extract the analysis/recommendation section from content."""
    content = unescape_content(raw_content)
    markers = ['以鲜国际分析：', '以鲜国际分析', '【以鲜国际分析】']
    for marker in markers:
        idx = content.find(marker)
        if idx != -1:
            return content[idx + len(marker):].strip()
    # Fallback: look for section headers like "四、市场影响与风险研判" or "四、市场信号与行业影响"
    section_match = re.search(r'[三四五]、[^\n]*(?:影响|风险|研判|信号|建议|展望)[^\n]*\n+([\s\S]+)$', content)
    if section_match:
        return section_match.group(1).strip()
    # Fallback: look for recommendation sections
    rec_markers = ['\n建议', '建议进口企业', '建议企业', '进口企业应', '企业应关注']
    for marker in rec_markers:
        idx = content.find(marker)
        if idx != -1:
            return content[idx:].strip()
    # Fallback: take the last substantial paragraph
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    if paragraphs:
        # Prefer last section that contains analysis keywords
        for p in reversed(paragraphs):
            if re.search(r'[一二三四五]、|建议|风险|影响|研判', p):
                return p
        return paragraphs[-1]
    return content.strip()


def make_risk_points(item):
    """Generate 2-3 risk/impact bullet points from analysis section."""
    content = item.get('content', '')
    analysis = extract_analysis(content)
    # Try to extract numbered list items at line start (1. xxx or 一、xxx)
    numbered = re.findall(r'^(?:\d+|[一二三四五])[\.、]\s*([^\n]+)', analysis, re.MULTILINE)
    if len(numbered) >= 2:
        return [clean_text(p) for p in numbered[:3]]
    # Try to split by paragraph or sentences
    sents = split_sentences(analysis)
    if len(sents) >= 3:
        return [clean_text(s) for s in sents[:3]]
    # Split by newline if sentences too few
    parts = [p.strip() for p in analysis.split('\n') if p.strip()]
    if len(parts) >= 2:
        return [clean_text(p) for p in parts[:3]]
    return [clean_text(s) for s in sents[:3]] if sents else [clean_text(analysis)]


def format_item(item, emoji='📰'):
    """Format a single item in standard structure."""
    title = item.get('title', '')
    source = item.get('source', '')
    summary_points = make_summary_points(item)
    risk_points = make_risk_points(item)

    lines = [
        f"## {emoji} {title}",
        '',
        f"**原文来源**：{source}",
        '',
        '**摘要要点**：',
    ]
    for idx, p in enumerate(summary_points, 1):
        lines.append(f"{idx}. {p}")
    lines.append('')
    lines.append('⚠️ **对进口商的实操影响**：')
    for p in risk_points:
        lines.append(f"- {p}")
    lines.append('')
    return '\n'.join(lines)


def write_file(filename, content):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return path


def generate_daily_overview():
    lines = [
        '# 🦐 老庄报告 · 每日速览 | 2026年7月31日',
        '',
        '> 今日老庄报告精选速递，一文读懂进口水产行业最新动向。',
        '',
    ]

    sections = [
        ('news', '📰 热点新闻'),
        ('events', '🔍 焦点事件'),
        ('policies', '⚖️ 政策法规'),
        ('reports', '📊 行业报告'),
    ]

    for section_key, section_label in sections:
        items = today_items[section_key]
        lines.append(f"## {section_label}")
        lines.append('')
        if items:
            for item in items:
                lines.append(f"- **{item.get('title')}**")
                # Add one-line summary
                summary = item.get('summary', '')
                if summary:
                    # Truncate to ~80 chars
                    short = summary[:80] + ('...' if len(summary) > 80 else '')
                    lines.append(f"  {short}")
                lines.append('')
        else:
            lines.append('今日无更新。')
            lines.append('')

    lines.append('---')
    lines.append('')
    lines.append(f"📮 官网：{SOURCE_URL} | 关注公众号「老庄报告」")
    lines.append('')

    return '\n'.join(lines)


def generate_news():
    items = today_items['news']
    lines = [
        '# 📰 热点新闻 | 2026年7月31日',
        '',
        '> 精选 2-3 条最具行业影响力的进口水产新闻。',
        '',
    ]

    if not items:
        lines.append('## 今日无更新')
        lines.append('')
        lines.append('今日暂无新增热点新闻。建议关注近期厄虾合规动态、口岸通关效率及运价变化。')
        lines.append('')
    else:
        for item in items:
            lines.append(format_item(item, emoji='📰'))
            lines.append('---')
            lines.append('')

    # Add review of previous news if only one today
    if len(items) < 2:
        prev_items = get_latest_prev('news', items)
        if prev_items:
            lines.append('## 📌 近期热点回顾')
            lines.append('')
            for prev in prev_items[:1]:
                lines.append(format_item(prev, emoji='📌'))
                lines.append('---')
                lines.append('')

    lines.append(f"📮 官网：{SOURCE_URL} | 关注公众号「老庄报告」")
    lines.append('')
    return '\n'.join(lines)


def generate_events():
    items = today_items['events']
    lines = [
        '# 🔍 焦点事件 | 2026年7月31日',
        '',
        '> 1-2 条深度事件分析，拆解趋势与机会。',
        '',
    ]

    if not items:
        lines.append('## 今日无更新')
        lines.append('')
        lines.append('今日暂无新增焦点事件。建议回顾近期厄虾供给过剩、口岸通关提速等深度话题。')
        lines.append('')
    else:
        for item in items:
            lines.append(format_item(item, emoji='🔍'))
            lines.append('---')
            lines.append('')

    lines.append(f"📮 官网：{SOURCE_URL} | 关注公众号「老庄报告」")
    lines.append('')
    return '\n'.join(lines)


def generate_policies():
    items = today_items['policies']
    if not items:
        return None
    lines = [
        '# ⚖️ 政策法规 | 2026年7月31日',
        '',
        '> 最新海关、监管与贸易政策解读。',
        '',
    ]
    for item in items:
        lines.append(format_item(item, emoji='⚖️'))
        lines.append('---')
        lines.append('')
    lines.append(f"📮 官网：{SOURCE_URL} | 关注公众号「老庄报告」")
    lines.append('')
    return '\n'.join(lines)


def generate_reports():
    items = today_items['reports']
    if not items:
        return None
    lines = [
        '# 📊 行业报告 | 2026年7月31日',
        '',
        '> 最新行业数据与研究报告精要。',
        '',
    ]
    for item in items:
        lines.append(format_item(item, emoji='📊'))
        lines.append('---')
        lines.append('')
    lines.append(f"📮 官网：{SOURCE_URL} | 关注公众号「老庄报告」")
    lines.append('')
    return '\n'.join(lines)


# Generate files
files_generated = []

overview = generate_daily_overview()
files_generated.append(write_file(f'{TODAY}-01-每日速览.md', overview))

news = generate_news()
files_generated.append(write_file(f'{TODAY}-02-热点新闻.md', news))

events = generate_events()
files_generated.append(write_file(f'{TODAY}-03-焦点事件.md', events))

policies = generate_policies()
if policies:
    files_generated.append(write_file(f'{TODAY}-04-政策法规.md', policies))

reports = generate_reports()
if reports:
    files_generated.append(write_file(f'{TODAY}-05-行业报告.md', reports))

# Print summary
print(f"Generated {len(files_generated)} files in {OUTPUT_DIR}:")
for f in files_generated:
    print(f"  {os.path.basename(f)}")

# Also print skipped
skipped = []
if not today_items['policies']:
    skipped.append('04-政策法规')
if not today_items['reports']:
    skipped.append('05-行业报告')
if skipped:
    print(f"Skipped: {', '.join(skipped)} (no updates)")
