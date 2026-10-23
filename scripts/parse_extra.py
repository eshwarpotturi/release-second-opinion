import openpyxl, re, csv, sys, warnings, datetime, glob
warnings.filterwarnings("ignore")
def log(m): print(datetime.datetime.now().strftime('%H:%M:%S'), m, flush=True)
src=sys.argv[1]; out=[]; files=sorted(glob.glob(src+'/*.xlsx'))
for i,f in enumerate(files,1):
    rel=re.search(r'(\d\dR\d)\.xlsx',f).group(1)
    wb=openpyxl.load_workbook(f,read_only=True); n=0
    for ws in wb.worksheets:
        t=ws.title.strip()
        if t.lower().startswith('econsent'): sec='eConsent, eCOA and Sites'
        elif t.lower().startswith('qualityone'): sec='QualityOne and RegulatoryOne'
        else: continue
        it=ws.iter_rows(values_only=True); h=[str(c).strip() if c else '' for c in next(it)]
        nm=h.index('Feature Name') if 'Feature Name' in h else h.index('Name')
        rk=h.index('GxP Risk'); ap=h.index('Application'); en=[j for j,x in enumerate(h) if x.startswith('Enablement')][0]
        ds=h.index('Feature Description'); app=None
        for r in it:
            risk=str(r[rk] or '').strip()
            if not r[nm] or risk not in('High','Medium','Low','N/A'): continue
            app=r[ap] or app
            out.append([rel,sec,app,str(r[nm]).replace('\n',' ').strip(),risk,r[en],'',str(r[ds] or '').replace('\n',' ').strip()[:300],''])
            n+=1
    log(f'{i}/{len(files)} {rel}: {n} extra features')
w=csv.writer(open('data/features_extra.csv','w',newline='')); w.writerow('release section application feature risk enablement default_impact description page'.split()); w.writerows(out)
log(f'total extra {len(out)}')
