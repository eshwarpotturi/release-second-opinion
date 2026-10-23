import csv, json, re, difflib, collections, sys, datetime
def log(m): print(datetime.datetime.now().strftime('%H:%M:%S'), m, flush=True)
O={'N/A':0,'Low':1,'Medium':2,'High':3}
norm=lambda s: re.sub(r'[^a-z0-9 ]','',s.lower().replace('&','and')).strip()
F=list(csv.DictReader(open('data/features.csv')))
by=collections.defaultdict(dict)
for x in F: by[x['release']][norm(x['feature'])]=x
D=list(csv.DictReader(open('data/drift.csv')))
rows=[];miss=0
for i,d in enumerate(D,1):
    k=norm(d['feature']); pool=by[d['release']]
    m=pool.get(k)
    if not m:
        c=difflib.get_close_matches(k,list(pool),n=1,cutoff=0.8)
        m=pool[c[0]] if c else None
    if not m:
        c=[p for p in pool if k and (k in p or p in k)]
        m=pool[c[0]] if len(c)==1 else None
    if not m:
        allp={}
        for rel in by:
            for kk,v in by[rel].items(): allp.setdefault(kk,v)
        m=allp.get(k)
        if not m:
            c=difflib.get_close_matches(k,list(allp),n=1,cutoff=0.88)
            m=allp[c[0]] if c else None
    if not m: miss+=1
    fr,to=d['from'],d['to']
    rows.append(dict(release=d['release'],feature=d['feature'],frm=fr,to=to,
      dir='down' if O[to]<O[fr] else 'up',
      cross=(O[fr]>=2)!=(O[to]>=2),
      section=m['section'] if m else 'Unmatched',
      app=m['application'] if m else '',
      desc=(m['description'][:260] if m else '')))
    if i%40==0 or i==len(D): log(f'matched {i}/{len(D)}, unmatched {miss}')
json.dump(rows,open('data/story.json','w'),indent=1)
c=collections.Counter((r['section'],r['dir']) for r in rows)
print(sorted(c.items()))
