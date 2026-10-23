import pdfplumber, glob, re, csv, datetime, collections
def log(m): print(datetime.datetime.now().strftime('%H:%M:%S'), m, flush=True)
clean=lambda s: re.sub(r'\s+',' ',(s or '').replace('\n',' ')).strip()
RISK={'high':'High','medium':'Medium','low':'Low','n/a':'N/A','na':'N/A'}
out=[]; files=sorted(glob.glob('raw/RIA-*.pdf'))
for fi,f in enumerate(files,1):
    rel=re.search(r'RIA-(\w+)\.pdf',f).group(1); n=0; sec=None; mp=None; app=None
    with pdfplumber.open(f) as pdf:
        for p in pdf.pages:
            for t in p.extract_tables():
                for r in t:
                    cells=[clean(c) for c in r]
                    low=[c.lower() for c in cells]
                    if 'feature name' in low or 'name' in low and any('risk' in c for c in low):
                        mp={}
                        for j,c in enumerate(low):
                            if c in('feature name','name'): mp['name']=j
                            elif 'risk' in c: mp['risk']=j
                            elif c.startswith('application') and 'application' not in mp: mp['application']=j
                            elif c.startswith('enablement'): mp['enab']=j
                            elif c.startswith('default'): mp['def']=j
                            elif c.startswith('description'): mp['desc']=j
                        if cells[0]: sec=cells[0]
                        continue
                    if not mp or len(cells)<=max(mp.values()): continue
                    risk=RISK.get(cells[mp['risk']].lower())
                    name=cells[mp['name']]
                    if not risk or not name: continue
                    if mp.get('application') is not None and cells[mp['application']]: app=cells[mp['application']]
                    if cells[0] and cells[0]!=sec and len(cells[0])<40 and not cells[mp['name']]==cells[0]: sec=cells[0] or sec
                    out.append([rel,sec,app,name,risk,cells[mp.get('enab',0)] if 'enab' in mp else '',cells[mp.get('def',0)] if 'def' in mp else '',cells[mp['desc']][:300] if 'desc' in mp else '',''])
                    n+=1
    log(f'{fi}/{len(files)} {rel}: {n} features')
w=csv.writer(open('data/features_pdf.csv','w',newline='')); w.writerow('release section application feature risk enablement default_impact description page'.split()); w.writerows(out)
old=collections.Counter(x['release'] for x in csv.DictReader(open('data/features.csv')) if x['release'][:2] in('19','20','21','22'))
new=collections.Counter(x[0] for x in out)
print({k:(old[k],new[k]) for k in sorted(new)})
print(collections.Counter(x[1] for x in out).most_common(20))
