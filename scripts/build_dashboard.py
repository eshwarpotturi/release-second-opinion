import json, pandas as pd
S=json.load(open("data/summary.json"))
q=pd.DataFrame(S["queue_rows"])
top=q[(q.gpt41=="High")&(q.gpt51=="High")&(q.veeva.isin(["N/A","Low"]))].copy()
kw=r"audit|signature|permission|security|access|authentic|login|password|confidential|encrypt"
top["kw"]=top.feature.str.lower().str.contains(kw)
top=top.sort_values(["kw","release"],ascending=[False,False])
S["queue"]["top"]=len(top); S["queue"]["kw"]=int(top.kw.sum())
D={k:S[k] for k in ["n","agree","AB","gate","eras","p","rel","mat","corr","dr","corrlist","queue"]}
D["cats"]=["High","Medium","Low","N/A"]
D["qrows"]=top.drop(columns="kw").to_dict("records")
html=open("scripts/template.html").read().replace("/*DATA*/",json.dumps(D))
open("index.html","w").write(html); print(len(html),D["queue"])
