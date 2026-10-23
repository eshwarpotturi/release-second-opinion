"""Adds one record per feature (the 11 releases that publish old and new ratings) to data/story.json,
so the page can draw one square per feature and open a single feature on click.
Repeats the matching used in study.py, so the revised features are the same ones."""
import csv, json, re, difflib, collections, datetime
def log(m): print(datetime.datetime.now().strftime('%H:%M:%S'), m, flush=True)
O={'N/A':0,'Low':1,'Medium':2,'High':3}
norm=lambda s: re.sub(r'\s+',' ',re.sub(r'[^a-z0-9 ]',' ',s.lower().replace('&','and'))).strip()
F=list(csv.DictReader(open('data/features_all.csv')))
S=json.load(open('data/story.json'))
VIS=set(S['vis'])
by=collections.defaultdict(dict); allp={}
for x in F:
    k=norm(x['feature']); by[x['release']][k]=x; allp.setdefault(k,x)
def find(rel,name):
    k=norm(name)
    for pool in (by[rel],allp):
        if k in pool: return pool[k]
        if len(k)>=12:
            c=[p for p in pool if len(p)>=12 and (p.startswith(k) or k.startswith(p))]
            if len(c)==1: return pool[c[0]]
        c=difflib.get_close_matches(k,list(pool),n=1,cutoff=0.86)
        if c: return pool[c[0]]
    return None
# same order and de-duplication as study.py
seen=set(); dd=[]
for d in csv.DictReader(open('data/drift.csv')):
    m=find(d['release'],d['feature'])
    r=dict(release=d['release'],feature=d['feature'],frm=d['from'],to=d['to'],fkey=(m['release'],m['feature']) if m else None)
    k=(r['release'],r['feature'],r['frm'],r['to'])
    if k in seen: continue
    seen.add(k); dd.append(r)
grp=collections.OrderedDict()
for r in dd: grp.setdefault(r['fkey'] or id(r),[]).append(r)
rows=[]
for g in grp.values():
    r=dict(g[0]); r['to']=g[-1]['to']
    if r['frm']==r['to']: continue
    rows.append(r)
assert len(rows)==S['n_rows'],(len(rows),S['n_rows'])
for r,it in zip(rows,S['items']):
    assert r['release']==it['release'] and r['feature']==it['feature'],(r,it)
    r['i']=S['items'].index(it)
corr={r['fkey']:r['i'] for r in rows if r['fkey']}
sq=[]
for x in F:
    if x['release'] not in VIS: continue
    sq.append([x['release'],x['section'],x['feature'],x['risk'],corr.get((x['release'],x['feature']),-1)])
assert len(sq)==S['Nvis'],(len(sq),S['Nvis'])
assert sum(1 for s in sq if s[4]>=0)==sum(S['hero'][k] for k in ('off','lower','on','raise'))
S['squares']=sq
json.dump(S,open('data/story.json','w'))
log(f'squares {len(sq)}, revised {sum(1 for s in sq if s[4]>=0)}')
