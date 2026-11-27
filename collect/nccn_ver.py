#!/usr/bin/env python3
"""NCCN 지침 목록의 판 번호만 읽어 이전과 달라진 암종을 기록한다 (지침 본문은 수집하지 않는다)."""
import re, json, os, html, urllib.request, datetime
URL = 'https://www.nccn.org/guidelines/category_1'
OUT = 'collect/nccn_versions.json'
req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
h = urllib.request.urlopen(req, timeout=60).read().decode('utf-8', 'ignore')
t = [html.unescape(x.strip()) for x in re.sub(r'<[^>]+>', '\n', h).split('\n') if x.strip()]
cur = {t[i-1]: t[i].split(':', 1)[1].strip() for i in range(1, len(t))
       if re.fullmatch(r'Version:\s*\d+\.\d{4}', t[i])}
old = json.load(open(OUT)) if os.path.exists(OUT) else {'versions': {}, 'changes': []}
baseline = not old['versions']
if len(cur) < 40: raise SystemExit('parse failed: %d entries' % len(cur))
if not baseline:
    for k, v in cur.items():
        if old['versions'].get(k) not in (None, v):
            old['changes'].append({'guideline': k, 'from': old['versions'][k], 'to': v, 'seen': datetime.date.today().isoformat()})
old['versions'] = cur
old['generated'] = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%MZ')
json.dump(old, open(OUT, 'w'), ensure_ascii=False, indent=1)
print(f"guidelines={len(cur)} changes={len(old['changes'])} baseline={baseline}")
