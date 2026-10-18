"""Apply a collaborator's explicit room decision; no crawler writes this file."""
import json, os
from pathlib import Path
from listing_identity import identity

def apply(event,data,store):
    issue=event['issue']
    if event.get('action')!='opened' or not issue.get('title','').startswith('[Home decision] '):raise ValueError('Not a decision request')
    if issue.get('author_association') not in ('OWNER','MEMBER','COLLABORATOR'):raise ValueError('Repository collaborator required')
    body=issue.get('body') or ''
    if len(body)>2000:raise ValueError('Request too large')
    payload=json.loads(body)
    if set(payload)!={'listing_key','decision'} or payload['decision'] not in ('keep','reject','reset'):raise ValueError('Invalid decision')
    known={identity(i)[0] for i in data['listings']}
    key=payload['listing_key']
    if key not in known:raise ValueError('Unknown listing')
    old=store.setdefault('decisions',{}).get(key,{})
    # Issue number orders user submissions, even when jobs finish out of order.
    if old.get('issue_number',0)>=issue['number']:return store
    store['version']=1
    store['decisions'][key]={'decision':payload['decision'],'updated_at':issue['created_at'],'issue_number':issue['number']}
    return store
if __name__=='__main__':
    event=json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text())
    path=Path('site/decisions.json')
    result=apply(event,json.loads(Path('site/data.json').read_text()),json.loads(path.read_text()))
    temp=path.with_suffix('.tmp');temp.write_text(json.dumps(result,ensure_ascii=False,indent=2));temp.replace(path)
