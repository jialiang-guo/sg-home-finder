"""Reject corrupt snapshots before Git commit and before deployment."""
import json, math, sys
from urllib.parse import urlsplit

def validate(data):
    if not isinstance(data,dict): raise ValueError('Snapshot must be an object')
    if not isinstance(data.get('listings'),list): raise ValueError('Missing listings')
    cfg=data['criteria']
    for key in ('stations','optional_stations'):
        if not isinstance(cfg[key],list) or any(not isinstance(s,str) for s in cfg[key]): raise ValueError('Invalid stations')
    stats=data['source_status']
    if not isinstance(stats['errors'],list): raise ValueError('Invalid source health')
    ids=set()
    for item in data['listings']:
        for key in ('id','url','title','source','room','availability','first_seen','status'):
            if not isinstance(item.get(key),str) or not item[key]: raise ValueError('Invalid '+key)
        if item['id'] in ids: raise ValueError('Duplicate listing')
        ids.add(item['id'])
        u=urlsplit(item['url'])
        if u.scheme!='https' or not u.hostname or u.username or u.password: raise ValueError('Invalid URL')
        if item['status'] not in ('match','review','excluded'): raise ValueError('Invalid status')
        price=item.get('price')
        if price is not None and (type(price) not in (int,float) or not math.isfinite(price) or price<=0): raise ValueError('Invalid price')
        if not isinstance(item.get('stale'),bool): raise ValueError('Invalid freshness')
    return data
if __name__=='__main__':
    validate(json.load(open(sys.argv[1])));print('Snapshot validated')
