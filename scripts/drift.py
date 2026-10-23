import re, subprocess, glob, csv
R=r'(High|Medium|Low|N/A)'
rows=[]; lists=[]
for f in sorted(glob.glob("raw/RIA-*.pdf")):
    rel=re.search(r"RIA-(\w+)\.pdf",f).group(1)
    t=subprocess.run(["pdftotext",f,"-"],capture_output=True,text=True).stdout
    i=[m.start() for m in re.finditer(r"Change Log\n",t)]
    t=t[i[-1]:] if i else ""
    t=re.sub(r"\s+"," ",t)
    for m in re.finditer(r'"([^"]+)"\s*(?:Risk\s*)?from\s*"'+R+r'"\s*to\s*"'+R+'"',t):
        rows.append([rel,m.group(1),m.group(2),m.group(3)])
    for m in re.finditer(r'GxP Risk (?:of|from)',t): pass
    n=len(re.findall(r'Updated the GxP Risk',t)); lists.append((rel,n))
print(lists)
with open("data/drift.csv","w",newline="") as fh:
    w=csv.writer(fh); w.writerow(["release","feature","from","to"]); w.writerows(rows)
import collections
print(len(rows)); print(collections.Counter(r[0] for r in rows))
print(collections.Counter((r[2],r[3]) for r in rows).most_common())
