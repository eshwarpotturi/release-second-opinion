import pandas as pd, json, numpy as np
from scipy.stats import fisher_exact
f=pd.read_csv("data/features.csv",keep_default_na=False)
for m,c in [("gpt-4.1","A"),("gpt-5.1","B")]:
    b=pd.DataFrame([json.loads(l) for l in open(f"data/blind_{m}.jsonl")]).set_index("i")
    f[c]=b.rating; f["why_"+c]=b.reason
assert f.A.notna().all() and f.B.notna().all(), (f.A.isna().sum(),f.B.isna().sum())
o={"N/A":0,"Low":1,"Medium":2,"High":3}
for c in ["risk","A","B"]: f["n_"+c]=f[c].map(o)
f["era"]=np.where(f.release<"21R3","1",np.where(f.release<"23R1","2","3"))
f["gate_v"]=f.n_risk>=2;f["gate_A"]=f.n_A>=2;f["gate_B"]=f.n_B>=2
def kappa(x,y):
    po=(x==y).mean();pe=sum((x==k).mean()*(y==k).mean() for k in set(x)|set(y));return (po-pe)/(1-pe)
out={}
out["n"]=len(f); out["releases"]=f.release.nunique()
out["agree"]={c:{"exact":round((f[c]==f.risk).mean()*100,1),"w1":round(((f["n_"+c]-f.n_risk).abs()<=1).mean()*100,1),"kappa":round(kappa(f.risk,f[c]),2),"higher":round((f["n_"+c]>f.n_risk).mean()*100,1),"lower":round((f["n_"+c]<f.n_risk).mean()*100,1)} for c in ["A","B"]}
out["AB"]=round((f.A==f.B).mean()*100,1)
out["gate"]={k:round(f["gate_"+k].mean()*100,1) for k in ["v","A","B"]}
eras={}
for e,g in f.groupby("era"):
    eras[e]={"n":len(g),"rels":f"{g.release.min()} to {g.release.max()}","v":round((g.risk=="High").mean()*100,1),"A":round((g.A=="High").mean()*100,1),"B":round((g.B=="High").mean()*100,1),"vHigh":int((g.risk=="High").sum()),"gate_v":round(g.gate_v.mean()*100,1),"gate_A":round(g.gate_A.mean()*100,1),"gate_B":round(g.gate_B.mean()*100,1),"exact_B":round((g.B==g.risk).mean()*100,1)}
out["eras"]=eras
def p(col,a,b):
    A=f[f.era==a];B=f[f.era==b];t=[[(A[col]=="High").sum(),(A[col]!="High").sum()],[(B[col]=="High").sum(),(B[col]!="High").sum()]];return float(fisher_exact(t)[1])
out["p"]={f"{c}_{a}{b}":round(p(c,a,b),4) for c in ["risk","A","B"] for a,b in [("1","2"),("1","3"),("2","3")]}
rel=[]
for k,g in f.groupby("release"):
    rel.append({"r":k,"n":len(g),"v":round((g.risk=="High").mean()*100,1),"a":round((g.A=="High").mean()*100,1),"b":round((g.B=="High").mean()*100,1)})
out["rel"]=rel
cats=["High","Medium","Low","N/A"]
out["mat"]={m:[[int(((f.risk==v)&(f[c]==x)).sum()) for x in cats] for v in cats] for m,c in [("gpt41","A"),("gpt51","B")]}
d=pd.read_csv("data/drift.csv",keep_default_na=False); d["fn"]=d["from"].map(o);d["tn"]=d["to"].map(o)
d["cross"]=(d.fn>=2)!=(d.tn>=2); d["down"]=d.tn<d.fn; d["era"]=np.where(d.release<"21R3","1",np.where(d.release<"23R1","2","3"))
out["corr"]={"n":len(d),"down":int(d.down.sum()),"up":int((d.tn>d.fn).sum()),"cross":int(d.cross.sum()),"off":int(((d.fn>=2)&(d.tn<2)).sum()),"on":int(((d.fn<2)&(d.tn>=2)).sum()),
 "by_era":{e:{"n":len(g),"down":int(g.down.sum())} for e,g in d.groupby("era")}}
out["dr"]=[{"r":k,"down":int(g.down.sum()),"up":int((g.tn>g.fn).sum())} for k,g in d.groupby("release")]
out["corrlist"]=d.rename(columns={"from":"frm"})[["release","feature","frm","to","cross"]].to_dict("records")
na=f[f.risk=="N/A"]; q2=f[(f.risk=="N/A")&f.A.isin(["High","Medium"])&f.B.isin(["High","Medium"])]
q1=f[(f.A=="High")&(f.B=="High")&(f.risk!="High")]
queue=f.loc[sorted(set(q1.index)|set(q2.index))]
out["queue"]={"na":len(na),"na_both":len(q2),"na_both_auto":int((q2.enablement.str.lower()=="auto-on").sum()),"bothHigh":len(q1),"total":len(queue)}
out["queue_rows"]=queue.rename(columns={"risk":"veeva","A":"gpt41","B":"gpt51","why_A":"w1","why_B":"w2"})[["release","application","feature","veeva","gpt41","gpt51","enablement","default_impact","w1","w2"]].to_dict("records")
# do models foresee corrections?  match by fuzzy name
import difflib
mm=[]
for _,r in d.iterrows():
    cand=f[f.release==r.release]
    b=difflib.get_close_matches(r.feature,list(cand.feature),1,0.6)
    if b:
        c=cand[cand.feature==b[0]].iloc[0]
        for k in ["A","B"]:
            mm.append((k,abs(o[c[k]]-r.tn),abs(o[c[k]]-r.fn)))
mm=pd.DataFrame(mm,columns=["k","df","di"])
out["foresee"]={k:{"n":int((mm.k==k).sum()),"closer_final":int(((mm.k==k)&(mm.df<mm.di)).sum()),"closer_initial":int(((mm.k==k)&(mm.df>mm.di)).sum())} for k in ["A","B"]}
json.dump(out,open("data/summary.json","w"),indent=1)
f[["release","section","application","feature","risk","A","B","enablement","default_impact"]].rename(columns={"risk":"veeva","A":"gpt41","B":"gpt51"}).to_csv("data/ratings_compared.csv",index=False)
queue.rename(columns={"risk":"veeva","A":"gpt41","B":"gpt51","why_A":"why_gpt-4.1","why_B":"why_gpt-5.1"})[["release","application","feature","veeva","gpt41","gpt51","enablement","default_impact","why_gpt-4.1","why_gpt-5.1"]].to_csv("data/review_queue.csv",index=False)
print(json.dumps({k:v for k,v in out.items() if k not in("rel","mat","dr","corrlist","queue_rows")},indent=1))
