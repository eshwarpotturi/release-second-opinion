import pandas as pd, re, difflib, numpy as np
f=pd.read_pickle("data/merged.pkl")
order={"N/A":0,"Low":1,"Medium":2,"High":3}
f["modelHigh"]=(f.A=="High")|(f.B=="High")
f["bothHigh"]=(f.A=="High")&(f.B=="High")
g=f.groupby("release").agg(n=("risk","size"),vHigh=("risk",lambda s:(s=="High").sum()),aHigh=("A",lambda s:(s=="High").sum()),bHigh=("B",lambda s:(s=="High").sum()),
   vNA=("risk",lambda s:(s=="N/A").sum()),aNA=("A",lambda s:(s=="N/A").sum()),bNA=("B",lambda s:(s=="N/A").sum()))
print(g)
f["period"]=np.where(f.release<"21R3","19R1-21R2","21R3-22R3")
p=f.groupby("period").agg(n=("risk","size"),vH=("risk",lambda s:(s=="High").mean()),aH=("A",lambda s:(s=="High").mean()),bH=("B",lambda s:(s=="High").mean()),
   vNA=("risk",lambda s:(s=="N/A").mean()),aNA=("A",lambda s:(s=="N/A").mean()),bNA=("B",lambda s:(s=="N/A").mean()),
   vGate=("gate_v","mean"),aGate=("gate_A","mean"),bGate=("gate_B","mean")).round(3)
print(p)
# keyword consistency
kw=r"audit trail|e-?signature|electronic signature|signature|permission|security|access control|confidential|password|authentication|login"
f["kw"]=(f.feature+" "+f.description).str.lower().str.contains(kw)
k=f[f.kw]
print("keyword feats",len(k)); print(k.risk.value_counts())
print("keyword-but-NA/Low:",k.risk.isin(["N/A","Low"]).sum())
print(k[k.risk.isin(["N/A","Low"])][["release","feature","risk","A","B"]].to_string())
# Same-name across releases w different rating
dup=f.groupby("feature").filter(lambda g:len(g)>1)
print("dup names",dup.feature.nunique()); print(dup.sort_values("feature")[["release","feature","risk"]].head(20).to_string())
# drift all 53 gate crossing
d=pd.read_csv("data/drift.csv",keep_default_na=False)
d["fn"]=d["from"].map(order); d["tn"]=d["to"].map(order)
d["dir"]=np.sign(d.tn-d.fn); d["cross"]=((d.fn>=2)!=(d.tn>=2))
print("drift n",len(d),"up",(d.dir>0).sum(),"down",(d.dir<0).sum(),"cross test gate",d.cross.sum(),"gate-> off",((d.fn>=2)&(d.tn<2)).sum(),"gate-> on",((d.fn<2)&(d.tn>=2)).sum())
print(d.groupby(d.release.str[:2]).agg(n=("dir","size"),down=("dir",lambda s:(s<0).sum())))
# fuzzy match all drift
rows=[]
for _,r in d.iterrows():
    cand=f[f.release==r.release]
    best=difflib.get_close_matches(r.feature,list(cand.feature),1,0.6)
    if best:
        c=cand[cand.feature==best[0]].iloc[0]
        rows.append(dict(release=r.release,feature=r.feature,frm=r["from"],to=r["to"],final=c.risk,A=c.A,B=c.B))
m=pd.DataFrame(rows); print("matched",len(m),"of",len(d))
for c in ["A","B"]:
    dist_to=(m[c].map(order)-m.to.map(order)).abs(); dist_fr=(m[c].map(order)-m.frm.map(order)).abs()
    print(c,"closer to final",(dist_to<dist_fr).sum(),"closer to initial",(dist_to>dist_fr).sum(),"tie",(dist_to==dist_fr).sum(),"mean dist final",dist_to.mean().round(2),"initial",dist_fr.mean().round(2))
m.to_csv("data/drift_vs_models.csv",index=False)
# top consensus disagreement N/A
cd=f[(f.risk=="N/A")&(f.A.isin(["High","Medium"]))&(f.B.isin(["High","Medium"]))]
print("N/A but both models Med/High:",len(cd),"of",(f.risk=="N/A").sum())
print(cd[(cd.A=="High")&(cd.B=="High")][["release","feature","enablement","default_impact"]].to_string())
print(cd.enablement.value_counts(), cd.default_impact.value_counts())
