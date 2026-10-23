import json, collections, datetime
def log(m): print(datetime.datetime.now().strftime('%H:%M:%S'), m, flush=True)
R=json.load(open('data/story.json'))
n=len(R); down=sum(r['dir']=='down' for r in R); cross=sum(r['cross'] for r in R)
off=sum(r['cross'] and r['dir']=='down' for r in R); on=cross-off
order=['19R1','19R2','19R3','20R1','20R2','20R3','21R1','21R2','25R3','26R1','26R2']
rel={k:[0,0] for k in order}
for r in R: rel[r['release']][0 if r['dir']=='down' else 1]+=1
per=lambda rs:(sum(r['dir']=='down' for r in rs),len(rs))
early=per([r for r in R if r['release'][:2] in('19','20','21')]); late=per([r for r in R if r['release'][:2] in('25','26')])
sec=collections.defaultdict(lambda:[0,0])
for r in R:
    if r['section']!='Unmatched': sec[r['section']][0 if r['dir']=='down' else 1]+=1
unm=sum(r['section']=='Unmatched' for r in R)
lv=['High','Medium','Low','N/A']
mat={f:{t:0 for t in lv} for f in lv}
for r in R: mat[r['frm']][r['to']]+=1
start=collections.defaultdict(lambda:[0,0])
for r in R: start[r['frm']][0 if r['dir']=='down' else 1]+=1
D=dict(n=n,down=down,up=n-down,cross=cross,off=off,on=on,rel=rel,order=order,sec=sec,unm=unm,mat=mat,start=start,
       early=early,late=late,rows=R)
html=open('scripts/story_template.html').read().replace('/*DATA*/null',json.dumps(D))
open('index.html','w').write(html); log(f'index.html written, {len(html)//1024} KB, {n} corrections')
