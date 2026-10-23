import re,glob,csv,collections
R=r'(High|Medium|Low|N/A)'
rows=[]; tot=collections.Counter(); ft=collections.Counter()
for f in sorted(glob.glob("data/changelog_2[3-6]R*.txt")):
    rel=re.search(r"changelog_(\w+)\.txt",f).group(1)
    t=open(f).read().replace("“",'"').replace("”",'"')
    for m in re.finditer(r'^[-\s]*(.+?)(?: \([\w-]+\))?: .*?GxP Risk (?:updated )?from "?'+R+r'"? to "?'+R+'"?',t,re.M):
        rows.append([rel,m.group(1).strip().strip('"'),m.group(2),m.group(3)]); ft[rel]+=1
    for m in re.finditer(r'"([^"]+)" (?:feature )?from "?'+R+r'"? to "?'+R+'"?',t): pass
    tot[rel]=len(re.findall("GxP Risk",t))
print("from/to rows per release:",dict(ft)); print(len(rows))
old=list(csv.reader(open("data/drift.csv")))
seen={(r[0],r[1],r[2],r[3]) for r in old[1:]}
with open("data/drift.csv","w",newline="") as fh:
    w=csv.writer(fh); w.writerow(old[0]); w.writerows(old[1:])
    for r in rows:
        if tuple(r) not in seen: w.writerow(r)
f=list(csv.reader(open("data/features.csv"))); n=list(csv.reader(open("data/features_new.csv")))
with open("data/features.csv","w",newline="") as fh:
    w=csv.writer(fh); w.writerow(f[0]); w.writerows(f[1:]); w.writerows(n[1:])
print("features total",len(f)-1+len(n)-1)
