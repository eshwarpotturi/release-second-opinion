import csv, json, sys, time, concurrent.futures as cf, urllib.request, os, datetime
TOK=open(""+os.environ["FOUNDRY_TOKEN_FILE"]+"").read().strip()
URL="https://llmfoundry.straivedemo.com/openai/v1/chat/completions"
MODEL=sys.argv[1]; OUT=f"data/blind_{MODEL}.jsonl"
RUBRIC="""You are a GxP computer-system-validation reviewer. Rate the GxP risk of a software release feature using this rubric (Veeva's published definition; risk assumes the feature is turned on):
High: may affect security, patient confidentiality, application areas that support GxP functions (audit trails, eSignature, etc.) or other ERES controls data.
Medium: may affect core application functions (workflows, revision history, etc.).
Low: may affect metadata/notifications.
N/A: minor UI enhancement, not a functional change, no validation impact.
Reply with JSON only: {"rating":"High|Medium|Low|N/A","reason":"<=25 words"}"""
rows=list(csv.DictReader(open("data/features.csv")))
done=set()
if os.path.exists(OUT): done={json.loads(l)["i"] for l in open(OUT)}
def call(i):
    r=rows[i]
    msg=f"Application: {r['application']}\nFeature: {r['feature']}\nEnablement: {r['enablement']}\nDefault impact: {r['default_impact']}\nDescription: {r['description']}"
    body=json.dumps({"model":MODEL,"messages":[{"role":"system","content":RUBRIC},{"role":"user","content":msg}],"response_format":{"type":"json_object"}}).encode()
    for a in range(4):
        try:
            req=urllib.request.Request(URL,body,{"Authorization":"Bearer "+TOK,"Content-Type":"application/json"})
            d=json.load(urllib.request.urlopen(req,timeout=90))
            j=json.loads(d["choices"][0]["message"]["content"]); u=d.get("usage",{})
            return {"i":i,"rating":j.get("rating"),"reason":j.get("reason"),"pt":u.get("prompt_tokens"),"ct":u.get("completion_tokens")}
        except Exception as e:
            err=str(e)[:100]; time.sleep(2*(a+1))
    return {"i":i,"error":err}
todo=[i for i in range(len(rows)) if i not in done]; n=0
with open(OUT,"a") as fh, cf.ThreadPoolExecutor(8) as ex:
    for res in ex.map(call,todo):
        fh.write(json.dumps(res)+"\n"); fh.flush(); n+=1
        if n%50==0 or n==len(todo): print(datetime.datetime.now().strftime("%H:%M:%S"),MODEL,f"done {n}/{len(todo)}",flush=True)
