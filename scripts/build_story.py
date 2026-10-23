import json, datetime
def log(m): print(datetime.datetime.now().strftime('%H:%M:%S'), m, flush=True)
S=json.load(open('data/story.json'))
html=open('scripts/story_template.html').read().replace('/*DATA*/null',json.dumps(S,separators=(',',':')))
open('index.html','w').write(html); log(f'index.html written, {len(html)//1024} KB, {len(S["items"])} revisions')
