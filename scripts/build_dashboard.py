import pandas as pd, json
r=pd.read_csv("data/ratings_compared.csv",keep_default_na=False)
q=pd.read_csv("data/review_queue.csv",keep_default_na=False)
d=pd.read_csv("data/drift.csv",keep_default_na=False)
o={"N/A":0,"Low":1,"Medium":2,"High":3}
rel=[]
for k,g in r.groupby("release"):
    rel.append({"r":k,"n":len(g),"v":round((g.veeva=="High").mean()*100,1),"a":round((g.gpt41=="High").mean()*100,1),"b":round((g.gpt51=="High").mean()*100,1)})
cats=["High","Medium","Low","N/A"]
mat={m:[[int(((r.veeva==v)&(r[m]==c)).sum()) for c in cats] for v in cats] for m in ["gpt41","gpt51"]}
d["fn"]=d["from"].map(o); d["tn"]=d["to"].map(o)
dr=[]
for k,g in d.groupby("release"):
    dr.append({"r":k,"down":int((g.tn<g.fn).sum()),"up":int((g.tn>g.fn).sum())})
corr=d.assign(cross=((d.fn>=2)!=(d.tn>=2))).rename(columns={"from":"frm"})[["release","feature","frm","to","cross"]].to_dict("records")
queue=q.rename(columns={"why_gpt-4.1":"w1","why_gpt-5.1":"w2"}).to_dict("records")
data={"rel":rel,"mat":mat,"cats":cats,"dr":dr,"corr":corr,"queue":queue,
 "gate":{"v":45.1,"a":77.6,"b":82.7}}
html=open("scripts/template.html").read().replace("/*DATA*/",json.dumps(data))
open("index.html","w").write(html)
print(len(html))
