"""Conservative Cove HTML adapter. Unknown facts remain unknown; never infer availability.
No browser evasion, login, CAPTCHA bypass or price extraction from related rooms.
"""
import datetime as dt
import hashlib, json, os, re, time
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.robotparser import RobotFileParser
from urllib.error import HTTPError
from validate_data import validate
from listing_identity import identity
import xml.etree.ElementTree as ET
ROOT = Path(__file__).parent
AGENT = 'SGHomeFinder/1.0'
class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise ValueError('Redirect requires adapter review')
class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.text=[]; self.links=[]; self.skip=0; self.title=[]; self.heading=None
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if tag in ('script','style'): self.skip+=1
        if tag in ('h1','h2'): self.heading=tag
        if tag=='a' and attrs.get('href'): self.links.append(attrs['href'])
    def handle_endtag(self, tag):
        if tag in ('script','style'): self.skip=max(0,self.skip-1)
        if tag in ('h1','h2'): self.heading=None
    def handle_data(self, data):
        if not self.skip and data.strip():
            self.text.append(data.strip())
            if self.heading: self.title.append(data.strip())
def parse_listing(html, url):
    page=Page(); page.feed(html)
    # Related-room prices must never be attributed to the room being viewed.
    body=re.split(r'other options in this property', ' '.join(page.text), flags=re.I)[0]
    body=body.replace('Queestown','Queenstown')
    title=' · '.join(page.title[:2])
    if not title: raise ValueError('No room heading: adapter needs review')
    low=body.lower()
    # Only an explicitly labelled SGD monthly price qualifies.
    prices=re.findall(r'(?:SGD|S\$)\s*([\d,]+(?:\.\d{2})?)\s*/\s*month',body,re.I)
    price=float(prices[0].replace(',','')) if len(set(prices))==1 else None
    station=next((s for s in ['Buona Vista','Commonwealth','Queenstown','Redhill','Tiong Bahru','one-north'] if re.search(re.escape(s)+r'\s*(?:MRT\s*)?\d+\s*mins?\s*walk',body,re.I)),None)
    walk=re.search(r'(\d+)\s*mins?\s*walk',body,re.I)
    built=re.search(r'(?:built|completed|TOP)\s*[:\-]?\s*(20\d{2}|19\d{2})',body,re.I)
    room='master' if 'private bathroom' in low or 'en-suite' in title.lower() else ('common' if 'shared bathroom' in low else 'unknown')
    return dict(id=hashlib.sha256(url.encode()).hexdigest()[:20],url=url,title=title,
        source='Cove',station=station,walk_minutes=int(walk[1]) if walk else None,
        price=price,room=room,built=int(built[1]) if built else None,
        condo='condominium' in low,availability='unavailable' if re.search(r'\bbooked\b|sold out|fully booked',low) else 'unknown')
def classify(item,cfg,year):
    if item['price'] is not None and item['price']>cfg['budget']: return 'excluded'
    if item['built'] is not None and year-item['built']>cfg['max_age']: return 'excluded'
    if item['station'] and item['station'] not in cfg['stations']+cfg['optional_stations']: return 'excluded'
    if item.get('property_type')=='hdb': return 'excluded'
    if item['availability']=='unavailable': return 'excluded'
    # Common rooms require subjective review, as do unknown price/year/availability.
    if (item['price'] is None or item['built'] is None or not item['station'] or not item['condo'] or item['room']!='master' or item['availability']!='available'): return 'review'
    return 'match'
class Client:
    def __init__(self,delay,host='cove.sg'): self.delay=delay; self.robots=None; self.last=0; self.host=host; self.blocked=False
    def raw(self,url):
        parts=urlsplit(url)
        if parts.scheme!='https' or parts.netloc!=self.host: raise ValueError('Source outside allowlist')
        time.sleep(max(0,self.delay-(time.monotonic()-self.last)))
        self.last=time.monotonic()
        with build_opener(NoRedirect()).open(Request(url,headers={'User-Agent':AGENT}),timeout=12) as r:
            data=r.read(4_000_001)
            if len(data)>4_000_000: raise ValueError('Response too large')
            return data.decode('utf-8')
    def get(self,url):
        if self.blocked: raise ValueError('Source paused after access error')
        if self.robots is None:
            try:
                content=self.raw('https://'+self.host+'/robots.txt')
            except HTTPError as e:
                if e.code==404: content='User-agent: *\nAllow: /'
                else: self.blocked=True; raise
            except Exception:
                self.blocked=True; raise
            rp=RobotFileParser();rp.parse(content.splitlines());self.robots=rp
            self.delay=max(self.delay,rp.crawl_delay(AGENT) or 0)
        if not self.robots.can_fetch(AGENT,url):
            self.blocked=True;raise ValueError('Disallowed by robots.txt')
        try:return self.raw(url)
        except HTTPError as e:
            if e.code in (401,403,429):self.blocked=True
            raise
def crawl(cfg,old=None):
    now=dt.datetime.now(dt.timezone.utc).isoformat(); year=dt.datetime.now(dt.timezone.utc).year
    client=Client(cfg['request_delay']); errors=[]; records={i['id']:dict(i) for i in (old or {}).get('listings',[])}
    queue=list(cfg['seed_urls']); discovery=list(cfg['discovery_urls']); seen=set(); count=0; success=0
    for url in discovery[:5]:
        try:
            root=ET.fromstring(client.get(url))
            links=[n.text for n in root.iter() if n.tag.endswith('}loc') or n.tag=='loc']
            if root.tag.endswith('sitemapindex'):
                for child in links[:5]:
                    sub=ET.fromstring(client.get(child)); queue += [n.text for n in sub.iter() if n.tag.endswith('}loc')]
            else: queue+=links
        except Exception as e: errors.append({'source':'Cove discovery','error':str(e)[:180]})
    for item in records.values():
        if cfg.get('cove_enabled',True) and item.get('source')=='Cove': queue.append(item['url'])
    for url in queue:
        if not isinstance(url,str) or not re.match(r'^https://cove\.sg/listings/\d',url) or url in seen: continue
        if count>=cfg['max_pages']: break
        seen.add(url); count+=1
        try:
            html=client.get(url); item=parse_listing(html,url); prior=records.get(item['id'],{})
            item.update(first_seen=prior.get('first_seen',now),last_seen=now,stale=False)
            item['price_history']=prior.get('price_history',[])
            if item['price'] is not None and item['price']!=prior.get('price'):
                item['price_history'].append({'at':now,'price':item['price']})
            item['price_history']=item['price_history'][-60:]
            item['status']=classify(item,cfg,year); records[item['id']]=item; success+=1
            p=Page();p.feed(html)
            queue.extend(urljoin(url,l) for l in p.links if '/listings/' in l)
        except Exception as e: errors.append({'url':url,'error':str(e)[:180]})
    if cfg.get('ris_enabled',False):
        from sources import collect_ris
        found,source_errors,attempts=collect_ris(cfg,old,Client,Page)
        errors.extend(source_errors);count+=attempts
        for item in found:
            prior=records.get(item['id'],{})
            item.update(first_seen=prior.get('first_seen',now),last_seen=now,stale=False)
            item['price_history']=list(prior.get('price_history',[]))
            if item['price']!=prior.get('price'):item['price_history'].append({'at':now,'price':item['price']})
            item['price_history']=item['price_history'][-60:]
            item['status']=classify(item,cfg,year);records[item['id']]=item;success+=1
    for item in records.values():
        item['listing_key'],item['source_id']=identity(item)
        item['stale']=item.get('last_seen')!=now
        item['status']=classify(item,cfg,year)
    return dict(updated_at=now,last_success=now if success else (old or {}).get('last_success'),
        criteria=cfg,source_status=dict(attempted=count,refreshed=success,errors=errors),listings=list(records.values()))
def main():
    cfg=json.loads((ROOT/'config.json').read_text()); state=ROOT/'site/data.json'; old=None
    if state.exists(): old=json.loads(state.read_text())
    data=validate(crawl(cfg,old))
    temp=state.with_suffix('.tmp'); temp.write_text(json.dumps(data,ensure_ascii=False,indent=2)); temp.replace(state)
    errors=len(data['source_status']['errors'])
    print(f"Refreshed {data['source_status']['refreshed']} pages; {errors} source errors.")
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'],'a') as f: f.write(f"degraded={'true' if errors or not data['source_status']['refreshed'] else 'false'}\n")
if __name__=='__main__':main()
