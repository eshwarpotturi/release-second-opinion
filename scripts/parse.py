import pdfplumber, glob, re, sys, csv, os
rows=[]; logs=[]
for f in sorted(glob.glob("raw/RIA-*.pdf")):
    rel=re.search(r"RIA-(\w+)\.pdf",f).group(1)
    sect=None; n0=len(rows)
    with pdfplumber.open(f) as p:
        for pi,pg in enumerate(p.pages):
            for t in pg.extract_tables():
                if not t or not t[0]: continue
                h=[(c or '').replace('\n',' ').strip() for c in t[0]]
                if len(h)==7 and 'Feature Name' in h:
                    sect=h[0] or sect
                    body=t[1:]
                elif len(t[0])==7 and sect and t[0][2] and not t[0][3] is None and (t[0][3] or '').strip() in ('High','Medium','Low','N/A'):
                    body=t
                else:
                    continue
                for r in body:
                    if len(r)!=7: continue
                    c=[(x or '').replace('\n',' ').strip() for x in r]
                    if c[0]: sect=c[0]
                    if c[3] not in ('High','Medium','Low','N/A'): continue
                    rows.append([rel,sect,c[1],c[2],c[3],c[4],c[5],c[6],pi+1])
    # change log text
    txt=os.popen(f"pdftotext -layout {f} -").read()
    i=txt.find("Change Log")
    open(f"data/changelog_{rel}.txt","w").write(txt[i:] if i>=0 else "")
    print(rel,len(rows)-n0,"features; changelog" , i>=0)
with open("data/features.csv","w",newline="") as fh:
    w=csv.writer(fh); w.writerow("release section application feature risk enablement default_impact description page".split()); w.writerows(rows)
