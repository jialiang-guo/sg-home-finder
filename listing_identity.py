import re
from urllib.parse import urlsplit

def identity(item):
    u=urlsplit(item['url'])
    if u.hostname=='rentinsingapore.com.sg':
        m=re.fullmatch(r'/ID(\d+)/?',u.path)
        if m:return 'RentInSingapore:'+m[1],m[1]
    if u.hostname=='cove.sg':
        m=re.match(r'/listings/(\d+)(?:-|/|$)',u.path)
        if m:return 'Cove:'+m[1],m[1]
    return 'legacy:'+item['id'],item['id']
