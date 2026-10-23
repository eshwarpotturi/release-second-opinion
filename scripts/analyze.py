import pandas as pd, json, re, numpy as np
f=pd.read_csv("data/features.csv",keep_default_na=False)
for m in ["gpt-4.1","gpt-5.1"]:
    b=pd.DataFrame([json.loads(l) for l in open(f"data/blind_{m}.jsonl")]).set_index("i")
    f["r_"+m]=b.rating; f["why_"+m]=b.reason
f["A"]=f["r_gpt-4.1"]; f["B"]=f["r_gpt-5.1"]
order={"N/A":0,"Low":1,"Medium":2,"High":3}
for c in ["risk","A","B"]: f["n_"+c]=f[c].map(order)
print("n",len(f))
def kappa(x,y):
    po=(x==y).mean(); pe=sum((x==k).mean()*(y==k).mean() for k in set(x)|set(y)); return (po-pe)/(1-pe)
for c in ["A","B"]:
    print(c,"exact",(f[c]==f.risk).mean().round(3),"within1",((f["n_"+c]-f.n_risk).abs()<=1).mean().round(3),"kappa",round(kappa(f.risk,f[c]),3),
          "model>vendor",(f["n_"+c]>f.n_risk).mean().round(3),"model<vendor",(f["n_"+c]<f.n_risk).mean().round(3))
print("A vs B exact",(f.A==f.B).mean().round(3))
print(pd.crosstab(f.risk,f.A,rownames=["veeva"],colnames=["gpt4.1"]))
print(pd.crosstab(f.risk,f.B,rownames=["veeva"],colnames=["gpt5.1"]))
# test split
f["yr"]=f.release.str[:2].astype(int)
for name,g in [("19-20",f[f.yr<=20]),("21-22",f[f.yr>=21])]:
    print(name,len(g),[(g[c]==g.risk).mean().round(3) for c in ["A","B"]])
# consensus disagreement
f["cons"]=np.where(f.A==f.B,f.A,None)
cd=f[(f.cons.notna())&(f.cons!=f.risk)]
print("consensus agree",f.cons.notna().mean().round(3),"consensus!=vendor",len(cd),"of",f.cons.notna().sum())
print(pd.crosstab(cd.risk,cd.cons))
# the testing-gate view: Veeva tests High+Medium
f["gate_v"]=f.risk.isin(["High","Medium"]); f["gate_A"]=f.A.isin(["High","Medium"]); f["gate_B"]=f.B.isin(["High","Medium"])
print("gate share vendor",f.gate_v.mean().round(3),"A",f.gate_A.mean().round(3),"B",f.gate_B.mean().round(3))
print("gate flips: vendor low/NA but both models test:",((~f.gate_v)&f.gate_A&f.gate_B).sum(),"; vendor test but both models skip:",(f.gate_v&~f.gate_A&~f.gate_B).sum())
# by enablement/default impact
for k in ["enablement","default_impact","application"]:
    t=f.groupby(k).apply(lambda g:pd.Series({"n":len(g),"vendorHigh":(g.risk=="High").mean(),"modelHigh":((g.A=="High")|(g.B=="High")).mean(),"agree":(g.A==g.risk).mean()})).round(2)
    print(t[t.n>=15].sort_values("n",ascending=False).head(10))
f.to_pickle("data/merged.pkl")
# drift
d=pd.read_csv("data/drift.csv",keep_default_na=False)
m=[]
for _,r in d.iterrows():
    g=f[(f.release==r.release)&(f.feature==r.feature)]
    if len(g)==0:
        g=f[(f.release==r.release)&(f.feature.str.lower().str.contains(re.escape(r.feature.lower()[:25])))]
    if len(g): m.append((r.release,r.feature,r["from"],r["to"],g.iloc[0].risk,g.iloc[0].A,g.iloc[0].B))
dm=pd.DataFrame(m,columns="release feature from to final A B".split())
print("drift matched",len(dm),"of",len(d))
dm["fromn"]=dm["from"].map(order); dm["ton"]=dm["to"].map(order)
print("up",(dm.ton>dm.fromn).sum(),"down",(dm.ton<dm.fromn).sum())
for c in ["A","B"]:
    print(c,"matches FINAL",(dm[c]==dm["to"]).sum(),"matches INITIAL",(dm[c]==dm["from"]).sum(),"neither",((dm[c]!=dm["to"])&(dm[c]!=dm["from"])).sum())
print("drifted agree w vendor-final: A",(dm.A==dm.final).mean().round(3),"vs non-drifted",(f.A==f.risk).mean().round(3))
dm.to_csv("data/drift_vs_models.csv",index=False)
print(dm.to_string())
