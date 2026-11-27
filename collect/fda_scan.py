#!/usr/bin/env python3
"""FDA 항암 승인 공지 목록에서 새 항목을 후보로 누적한다 (제목, 링크, 날짜만 기록)."""
import re, json, os, urllib.request, html, datetime
URL = 'https://www.fda.gov/drugs/cancer-approvals/oncology-cancerhematologic-malignancies-approval-notifications'
OUT = 'collect/fda_candidates.json'
HDR = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Language': 'en-US,en;q=0.9'}
def get(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers=HDR), timeout=60).read().decode('utf-8', 'ignore')
try:
    h = get(URL)
except Exception as e:
    print('page failed:', e); h = ''

items = {}
for row in re.split(r'<tr', h)[1:]:
    m = re.search(r'<a href="(/drugs/[^"]+)"[^>]*>(.*?)</a>', row, re.S)
    if not m or 'approves' not in m.group(2).lower() and 'grants' not in m.group(2).lower(): continue
    cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.S)
    desc = html.unescape(re.sub(r'<[^>]+>', '', cells[1])).strip() if len(cells) > 1 else ''
    dm = re.search(r'On ([A-Z][a-z]+ \d{1,2}, \d{4})', desc)
    date = None
    if dm:
        try: date = datetime.datetime.strptime(dm.group(1), '%B %d, %Y').strftime('%Y-%m-%d')
        except ValueError: pass
    t = html.unescape(re.sub(r'<[^>]+>', '', m.group(2))).strip()
    items[m.group(1)] = {'title': t, 'date': date, 'summary': desc[:300], 'url': 'https://www.fda.gov' + m.group(1)}
if len(items) < 20: raise SystemExit('parse failed: %d entries' % len(items))
old = json.load(open(OUT)) if os.path.exists(OUT) else {'seen': {}, 'pending': []}
baseline = not old['seen']
new = [] if baseline else [v for k, v in items.items() if k not in old['seen']]
old['seen'].update({k: v['date'] for k, v in items.items()})
old['pending'] += new
old['generated'] = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%MZ')
json.dump(old, open(OUT, 'w'), ensure_ascii=False, indent=1)
print(f"parsed={len(items)} new={len(new)} pending={len(old['pending'])} baseline={baseline}")
