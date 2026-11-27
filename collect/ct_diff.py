#!/usr/bin/env python3
"""ClinicalTrials.gov 등록 정보 변경 대조. 이전 스냅샷과 비교해 변경 항목만 changes.json에 남긴다."""
import json, sys, os, urllib.request, urllib.parse, datetime
NCTS = [l.strip() for l in open('collect/nct_list.txt') if l.strip()]
SNAP = 'collect/ct_snapshot.json'
OUT = 'collect/ct_changes.json'
FIELDS = ['NCTId','OverallStatus','LastUpdatePostDate','PrimaryCompletionDate','CompletionDate','HasResults','EnrollmentCount','BriefTitle']
def fetch(batch):
    q = urllib.parse.urlencode({'filter.ids': ','.join(batch), 'pageSize': 1000,
        'fields': ','.join(['NCTId','OverallStatus','LastUpdatePostDate','PrimaryCompletionDate','CompletionDate','HasResults','EnrollmentCount','BriefTitle'])})
    with urllib.request.urlopen('https://clinicaltrials.gov/api/v2/studies?' + q, timeout=60) as r:
        return json.load(r)['studies']
def flat(s):
    p = s['protocolSection']; i = p['identificationModule']; st = p['statusModule']
    return {'nct': i['nctId'], 'title': i.get('briefTitle',''),
            'status': st.get('overallStatus'), 'updated': st.get('lastUpdatePostDateStruct',{}).get('date'),
            'primary_completion': st.get('primaryCompletionDateStruct',{}).get('date'),
            'completion': st.get('completionDateStruct',{}).get('date'),
            'has_results': bool(s.get('hasResults')),
            'enrollment': p.get('designModule',{}).get('enrollmentInfo',{}).get('count')}
cur = {}
for k in range(0, len(NCTS), 100):
    for s in fetch(NCTS[k:k+100]):
        f = flat(s); cur[f['nct']] = f
old = json.load(open(SNAP)) if os.path.exists(SNAP) else None
KEYS = ['status','primary_completion','completion','has_results','enrollment']
changes = []
if old is not None:
    for n, c in cur.items():
        o = old.get(n)
        if o is None: continue
        d = {k: [o.get(k), c.get(k)] for k in KEYS if o.get(k) != c.get(k)}
        if d: changes.append({'nct': n, 'title': c['title'], 'diff': d, 'updated': c['updated']})
    missing = [n for n in NCTS if n not in cur]
else:
    missing = [n for n in NCTS if n not in cur]
out = {'generated': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'), 'baseline': old is None,
       'tracked': len(cur), 'not_found': missing, 'changes': changes}
# 변경 누적: 월간 갱신이 처리 후 비울 때까지 유지
prev = json.load(open(OUT)) if os.path.exists(OUT) else {'changes': []}
acc = {c['nct']: c for c in prev.get('changes', [])}
for c in changes:
    if c['nct'] in acc:
        for k, v in c['diff'].items():
            acc[c['nct']]['diff'][k] = [acc[c['nct']]['diff'].get(k, v)[0], v[1]]
        acc[c['nct']]['updated'] = c['updated']
    else: acc[c['nct']] = c
out['changes'] = list(acc.values())
json.dump(cur, open(SNAP, 'w'), ensure_ascii=False, indent=0)
json.dump(out, open(OUT, 'w'), ensure_ascii=False, indent=1)
print(f"tracked={len(cur)} new_changes={len(changes)} pending={len(out['changes'])} not_found={len(missing)}")
