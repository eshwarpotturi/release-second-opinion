import re, os, csv, subprocess, glob
out=[]
for f in sorted(glob.glob("raw/RIA-*.pdf")):
    rel=re.search(r"RIA-(\w+)\.pdf",f).group(1)
    t=subprocess.run(["pdftotext","-layout",f,"-"],capture_output=True,text=True).stdout
    ls=t.split("\n")
    idx=[i for i,l in enumerate(ls) if l.strip().startswith("Change Log") and len(l.strip())<60]
    start=idx[-1] if idx else None
    if start is None: print(rel,"no changelog"); continue
    # join into text; take left column (actions) + date col
    date=None; action=None; cur=None; items=[]
    for l in ls[start+1:]:
        m=re.match(r"^\s*(\d{1,2} \w{3} \d{4})\s+(.*)$",l)
        if m: date=m.group(1); l=" "*18+m.group(2)
        if "Release Impact Assessment" in l and "Page" in l: continue
        body=l[:88].strip() if len(l)>0 else ""
        # strip right-hand column
        body=re.split(r"\s{6,}",l.strip())[0]
        if not body: continue
        a=re.match(r"(Updated the (GxP Risk|Enablement|Default Impact|Feature Description)[^:]*|Added the following feature[s]?|Removed the following feature[s]?|Updated the name[^:]*|Updated the \w[^:]*)[:]?",body)
        if a and not body.startswith("-"):
            action=body.rstrip(":"); continue
        if body.startswith("-"):
            cur=body[1:].strip(); items.append([rel,date,action,cur])
        elif cur is not None and items and items[-1][3] and not re.match(r"^(Initial|The RIA)",body):
            items[-1][3]+=" "+body
    out+=items
    print(rel,len(items))
with open("data/changelog.csv","w",newline="") as fh:
    w=csv.writer(fh); w.writerow(["release","date","action","detail"]); w.writerows(out)
