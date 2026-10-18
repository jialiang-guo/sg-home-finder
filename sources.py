"""Public RentInSingapore pages; no login, contact details or gated content."""
import hashlib, re
from urllib.parse import urljoin, urlsplit
from html.parser import HTMLParser

class PublicRoom(HTMLParser):
    def __init__(self):
        super().__init__(); self.active=False; self.ended=False; self.skip=0; self.in_title=False; self.title=[]; self.body=[]
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style'): self.skip+=1
        if tag=='h1' and not self.ended:self.active=True;self.in_title=True
        if tag=='footer':self.ended=True
    def handle_endtag(self,tag):
        if tag in ('script','style'):self.skip=max(0,self.skip-1)
        if tag=='h1':self.in_title=False
    def handle_data(self,text):
        t=text.strip()
        if not self.active or self.ended or self.skip or not t:return
        if re.match(r'^(Contact\b|View more|Login to continue|Similar|Related)',t,re.I):self.ended=True;return
        self.body.append(t)
        if self.in_title:self.title.append(t)

def parse_ris(html,url):
    p=PublicRoom();p.feed(html);title=' '.join(p.title);body=' '.join(p.body);low=body.lower()
    if not title or not re.search(r'\bRoom details\b',body,re.I):raise ValueError('Room details missing; parser review required')
    m=re.search(r'([\d,]+)\s*SGD\s*per month',body,re.I)
    if not m:raise ValueError('Primary monthly price missing')
    station=next((s for s in ['Buona Vista','Commonwealth','Queenstown','Redhill','Tiong Bahru','one-north'] if re.search(re.escape(s)+r'\s*MRT',body,re.I)),None)
    b=re.search(r'(?:built|completed|TOP)\s*[:\-]?\s*(20\d{2}|19\d{2})',body,re.I)
    published=re.search(r'Published on\s*(\d{2}\.\d{2}\.\d{4})',body,re.I)
    return dict(id=hashlib.sha256(url.encode()).hexdigest()[:20],url=url,title=title[:200],source='RentInSingapore',
        price=float(m[1].replace(',','')),station=station,walk_minutes=None,
        room='master' if re.search(r'master|en.?suite|attached bathroom|private bathroom|own bathroom',low) else ('common' if 'common room' in low else 'unknown'),
        built=int(b[1]) if b else None,condo=bool(re.search(r'\bcondo(?:minium)?\b',low)),
        property_type='hdb' if re.search(r'\bHDB\b',body) else ('condo' if re.search(r'\bcondo(?:minium)?\b',low) else 'unknown'),
        availability='unavailable' if re.search(r'no longer available|already rented|listing expired',low) else 'unknown',
        published=published[1] if published else None)

def collect_ris(cfg,old,Client,Page):
    client=Client(cfg.get('request_delay',3),host='rentinsingapore.com.sg')
    errors=[];urls=[];items=[];attempted=0
    def links(html,base):
        p=Page();p.feed(html)
        return [urljoin(base,u).split('?')[0] for u in p.links if re.fullmatch(r'/ID\d+|https://rentinsingapore\.com\.sg/ID\d+',u)]
    # Bound discovery and detail reads; a blocked domain stops immediately.
    for u in cfg.get('ris_discovery',[])[:4]:
        try:urls.extend(links(client.get(u),u))
        except Exception as e:
            errors.append({'source':'RentInSingapore discovery','error':str(e)[:180]})
            if client.blocked: return items,errors,attempted
    urls+=cfg.get('ris_seed_urls',[])
    urls += [i['url'] for i in (old or {}).get('listings',[]) if i.get('source')=='RentInSingapore']
    for u in list(dict.fromkeys(urls))[:cfg.get('ris_max_pages',20)]:
        if urlsplit(u).netloc!='rentinsingapore.com.sg':continue
        attempted+=1
        try:items.append(parse_ris(client.get(u),u))
        except Exception as e:
            errors.append({'url':u,'error':str(e)[:180]})
            if client.blocked:break
    if not urls and not errors:errors.append({'source':'RentInSingapore','error':'Discovery returned no room links; review adapter'})
    return items,errors,attempted
