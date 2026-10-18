import unittest
from unittest.mock import patch
from crawler import crawl
from crypto import encrypt,decrypt
from crawler import parse_listing,classify
from cryptography.exceptions import InvalidTag
class Tests(unittest.TestCase):
 def test_encryption(self):
  data={'listings':[{'title':'私人房源'}]}; pw='a-very-long-test-password'
  a=encrypt(data,pw); self.assertEqual(decrypt(a,pw),data)
  self.assertNotEqual(a['ciphertext'],encrypt(data,pw)['ciphertext'])
  with self.assertRaises(InvalidTag):decrypt(a,'incorrect-password-value')
 def test_tamper(self):
  a=encrypt({'private':'yes'},'a-very-long-test-password'); a['iv']='AAAAAAAAAAAAAAAA'
  with self.assertRaises(InvalidTag):decrypt(a,'a-very-long-test-password')
 def test_short_password(self):
  with self.assertRaises(ValueError):encrypt({},'short')
 def test_related_price_never_used(self):
  html='<h1>Commonwealth Towers</h1><h2>Master En-suite Room</h2><p>Condominium Queenstown 3 mins walk private bathroom</p><h3>other options in this property</h3><p>SGD 1,500 / month booked</p>'
  x=parse_listing(html,'https://cove.sg/listings/1');self.assertIsNone(x['price']);self.assertEqual(x['availability'],'unknown');self.assertEqual(x['station'],'Queenstown')
 def test_unknown_and_old(self):
  x=parse_listing('<h1>Test</h1><h2>Master</h2><p>Condominium Queenstown 3 mins walk private bathroom SGD 2,400 / month Built: 2017</p>','https://cove.sg/listings/1')
  cfg={'budget':2500,'max_age':10,'stations':['Queenstown'],'optional_stations':[]}
  self.assertEqual(x['price'],2400);self.assertEqual(classify(x,cfg,2026),'review')
  x['availability']='available';self.assertEqual(classify(x,cfg,2026),'match')
  self.assertEqual(classify(x,cfg,2028),'excluded')
  x['price']=2600;self.assertEqual(classify(x,cfg,2026),'excluded')
 def test_source_failure_preserves_history(self):
  x=parse_listing('<h1>Test</h1><h2>Master</h2>','https://cove.sg/listings/1')
  x.update(first_seen='2026-01-01',last_seen='2026-01-01',price_history=[])
  cfg={'budget':2500,'max_age':10,'stations':['Queenstown'],'optional_stations':[], 'request_delay':0,'seed_urls':[x['url']],'discovery_urls':[],'max_pages':2}
  with patch('crawler.Client.get',side_effect=ValueError('403 blocked')):
   result=crawl(cfg,{'listings':[x],'last_success':'2026-01-01'})
  self.assertEqual(len(result['listings']),1)
  self.assertTrue(result['listings'][0]['stale'])
  self.assertEqual(result['last_success'],'2026-01-01')
  self.assertEqual(result['source_status']['refreshed'],0)
if __name__=='__main__':unittest.main()
