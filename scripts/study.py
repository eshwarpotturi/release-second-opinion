import csv, json, re, difflib, collections, datetime, sys, glob, warnings, os
warnings.filterwarnings('ignore')
def log(m): print(datetime.datetime.now().strftime('%H:%M:%S'), m, flush=True)
O={'N/A':0,'Low':1,'Medium':2,'High':3}
norm=lambda s: re.sub(r'\s+',' ',re.sub(r'[^a-z0-9 ]',' ',s.lower().replace('&','and'))).strip()
F=list(csv.DictReader(open('data/features_pdf.csv')))+[x for x in csv.DictReader(open('data/features.csv')) if x['release'][:2] not in('19','20','21','22')]+list(csv.DictReader(open('data/features_extra.csv')))
w=csv.DictWriter(open('data/features_all.csv','w',newline=''),fieldnames=list(F[0].keys())); w.writeheader(); w.writerows(F)
log(f'features {len(F)}')
RELS=sorted({x['release'] for x in F},key=lambda r:(r[:2],r[2:]))
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
# 1. corrections with from/to
rows=[]
D=list(csv.DictReader(open('data/drift.csv')))
for i,d in enumerate(D,1):
    m=find(d['release'],d['feature']); fr,to=d['from'],d['to']
    rows.append(dict(release=d['release'],feature=d['feature'],frm=fr,to=to,dir='down' if O[to]<O[fr] else 'up',
        cross=(O[fr]>=2)!=(O[to]>=2),section=m['section'] if m else None,
        desc=(m['description'][:240] if m else ''),final=m['risk'] if m else None,fkey=(m['release'],m['feature']) if m else None))
    if i%40==0 or i==len(D): log(f'from/to matched {i}/{len(D)}')
# 2. names-only corrections
names=[]
quote=re.compile(r'[“"”]([^“"”]{4,160})[“"”]')
def blocks(text):
    for b in re.split(r'\n\s*\n',text):
        if re.search(r'updated[^\n]{0,40}gxp risk',b,re.I): yield b
have={(r['release']) for r in rows}
import openpyxl
for f in sorted(glob.glob('/tmp/ria/*.xlsx')):
    rel=re.search(r'(\d\dR\d)\.xlsx',f).group(1)
    ws=openpyxl.load_workbook(f,read_only=True)['Change Log']
    for r in ws.iter_rows(values_only=True):
        t='\n'.join(str(c) for c in r if c)
        if rel not in('25R3','26R1','26R2'):
            for b in blocks(t):
                for q in quote.findall(b):
                    if not re.search(r'gxp risk|feature$',q,re.I): names.append((rel,q.strip()))
CL=list(csv.DictReader(open('data/changelog.csv')))
for c in CL:
    if c['release'] in('21R3','22R1','22R2','22R3') and re.search(r'GxP Risk',c['action'],re.I):
        for q in quote.findall(c['detail']): names.append((c['release'],q.strip()))
names=sorted(set(names)); log(f'name-only corrections {len(names)}')
nrows=[]
for rel,nm in names:
    m=find(rel,nm)
    nrows.append(dict(release=rel,feature=nm,section=m['section'] if m else None,final=m['risk'] if m else None))
# 3. totals per release and rating mix by section/era
tot=collections.Counter(x['release'] for x in F)
era=lambda r:'2019–2021' if r[:2] in('19','20','21') else ('2022' if r[:2]=='22' else ('2023–2024' if r[:2] in('23','24') else '2025–2026'))
mix=collections.defaultdict(lambda:collections.Counter())
for x in F:
    mix[(x['section'],era(x['release']))][x['risk']]+=1
mixo=collections.defaultdict(collections.Counter)
for x in F: mixo[era(x['release'])][x['risk']]+=1
json.dump(dict(rows=rows,nrows=nrows,tot=tot,mix={f'{a}|{b}':v for (a,b),v in mix.items()},mixo=mixo,rels=RELS),open('data/study.json','w'),indent=1)
m1=sum(r['section'] is not None for r in rows); m2=sum(r['section'] is not None for r in nrows)
log(f'from/to placed {m1}/{len(rows)}; name-only placed {m2}/{len(nrows)}')
print(sorted(collections.Counter(r['release'] for r in nrows).items()))
print({k:dict(v) for k,v in mixo.items()})

# ---- analysis ----
seen=set(); dd=[]
for r in rows:
    if not r['section'] and re.search(r'connection$',r['feature'],re.I): r['section']='Vault Connections'
    k=(r['release'],r['feature'],r['frm'],r['to'])
    if k in seen: continue
    seen.add(k); dd.append(r)
grp=collections.OrderedDict()
for r in dd: grp.setdefault(r['fkey'] or id(r),[]).append(r)
rows=[]
for k,g in grp.items():
    if len(g)>1: log('merged repeat revision: '+g[0]['feature']+' '+' / '.join(x['frm']+'>'+x['to'] for x in g))
    r=dict(g[0]); r['to']=g[-1]['to']; r['dir']='down' if O[r['to']]<O[r['frm']] else 'up'; r['cross']=(O[r['frm']]>=2)!=(O[r['to']]>=2)
    if r['frm']==r['to']: continue
    rows.append(r)
log(f'from/to after de-duplication {len(rows)}')
for r in nrows:
    if not r['section'] and re.search(r'connection$',r['feature'],re.I): r['section']='Vault Connections'
VIS=sorted({r['release'] for r in rows},key=lambda r:(r[:2],r[2:]))
# first rating reconstruction for releases whose from/to is visible (only features that exist in final list)
corr={r['fkey']:r for r in rows if r['fkey']}
first=collections.Counter(); fin=collections.Counter(); lowered_from_tested=0; raised_from_untested=0; kept=0
for x in F:
    if x['release'] not in VIS: continue
    k=(x['release'],x['feature']); c=corr.get(k)
    f0=c['frm'] if c else x['risk']
    first[f0]+=1; fin[x['risk']]+=1
    if O[f0]>=2:
        if O[x['risk']]<2: lowered_from_tested+=1
        else: kept+=1
    elif c and O[x['risk']]>=2: raised_from_untested+=1
t0=first['High']+first['Medium']; t1=fin['High']+fin['Medium']; N=sum(first.values())
log(f'visible releases {VIS}; features {N}; first tested {t0} ({100*t0/N:.1f}%), final tested {t1} ({100*t1/N:.1f}%)')
log(f'of {t0} first-tested: {lowered_from_tested} later below testing line ({100*lowered_from_tested/t0:.1f}%); raised into testing {raised_from_untested}')
# revision rate by release (all corrections incl names-only)
cnt=collections.Counter(r['release'] for r in rows)+collections.Counter(r['release'] for r in nrows)
print({k:(cnt[k],tot[k],round(100*cnt[k]/tot[k],1)) for k in RELS if tot[k]})
# by section
secn=collections.Counter(); secd=collections.defaultdict(lambda:[0,0])
for r in rows+nrows: secn[r['section']]+=1
for r in rows: secd[r['section']][0 if r['dir']=='down' else 1]+=1
stot=collections.Counter(x['section'] for x in F)
print({s:(secn[s],stot[s],round(100*secn[s]/stot[s],1),secd[s]) for s in stot if stot[s]>=100})

# stability by first rating and enablement (visible releases, matched only)
st=collections.defaultdict(lambda:[0,0,0]); en=collections.defaultdict(lambda:[0,0])
for x in F:
    if x['release'] not in VIS: continue
    c=corr.get((x['release'],x['feature'])); f0=c['frm'] if c else x['risk']
    st[f0][0]+=1; 
    if c: st[f0][1]+=1; st[f0][2]+= c['dir']=='down'
    e=x['enablement'].strip().lower() or 'n/a'; en[e][0]+=1; en[e][1]+= bool(c)
print('by first rating (n, revised, lowered):',{k:(v[0],v[1],round(100*v[1]/v[0],1),v[2]) for k,v in st.items()})
print('by enablement:',{k:(v[0],v[1],round(100*v[1]/v[0],1)) for k,v in en.items() if v[0]>30})
pairs=collections.Counter((r['frm'],r['to']) for r in rows); print(pairs.most_common(6), len(rows))

# ---- export for the page ----
items=[]
for r in rows:
    items.append(dict(release=r['release'],feature=r['feature'],first=r['frm'],now=r['to'],dir=r['dir'],cross=r['cross'],section=r['section'],desc=r['desc'],vis=bool(r['fkey'])))
for r in nrows:
    items.append(dict(release=r['release'],feature=r['feature'],first=None,now=r['final'],dir='unknown',cross=None,section=r['section'],desc='',vis=False))
hero=collections.Counter(); Nvis=0
for x in F:
    if x['release'] not in VIS: continue
    Nvis+=1; c=corr.get((x['release'],x['feature']))
    if not c: hero['same']+=1; continue
    hero[('off' if c['cross'] else 'lower') if c['dir']=='down' else ('on' if c['cross'] else 'raise')]+=1
secs={}
for s in stot:
    if stot[s]<150: continue
    sec_rows=[i for i in items if i['section']==s]
    secs[s]=dict(features=stot[s],revised=len(sec_rows),down=sum(i['dir']=='down' for i in sec_rows),up=sum(i['dir']=='up' for i in sec_rows),unknown=sum(i['dir']=='unknown' for i in sec_rows))
relx={k:dict(features=tot[k],down=sum(i['dir']=='down' and i['release']==k for i in items),up=sum(i['dir']=='up' and i['release']==k for i in items),unknown=sum(i['dir']=='unknown' and i['release']==k for i in items)) for k in RELS}
S=dict(hero=dict(hero),Nvis=Nvis,vis=VIS,tiers={k:dict(n=v[0],revised=v[1],lowered=v[2]) for k,v in st.items()},secs=secs,rel=relx,
  era={k:dict(v) for k,v in mixo.items()},items=items,total_features=len(F),n_rows=len(rows),n_down=sum(r['dir']=='down' for r in rows),
  n_names=len(nrows),pairs=[[a,b,c] for (a,b),c in pairs.most_common()])
json.dump(S,open('data/story.json','w'))
log(f"story.json written: hero={dict(hero)} N={Nvis} secs={len(secs)} items={len(items)}")
