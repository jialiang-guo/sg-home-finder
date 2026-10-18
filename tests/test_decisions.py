import copy
import json
import unittest
from apply_decision import apply
from listing_identity import identity

class Decisions(unittest.TestCase):
    def setUp(self):
        self.item={'id':'old-hash','url':'https://rentinsingapore.com.sg/ID365031','price':2400}
        self.data={'listings':[self.item]}
        self.store={'version':1,'decisions':{}}
    def event(self,decision='reject',number=1,role='OWNER'):
        return {'action':'opened','issue':{'title':'[Home decision] test','author_association':role,'body':json.dumps({'listing_key':'RentInSingapore:365031','decision':decision}),'number':number,'created_at':'2026-10-18T00:00:00Z'}}
    def test_identity_survives_tracking_query_and_cove_slug(self):
        other=dict(self.item,url=self.item['url']+'/?tracking=x',id='new-hash')
        self.assertEqual(identity(other),identity(self.item))
        self.assertEqual(identity({'url':'https://cove.sg/listings/334-new-title','id':'x'})[0],'Cove:334')
    def test_new_scrape_and_price_leave_choice_intact(self):
        result=apply(self.event(),self.data,self.store)
        refreshed={'listings':[dict(self.item,price=2200,id='changed-hash')]}
        self.assertEqual(result['decisions'][identity(refreshed['listings'][0])[0]]['decision'],'reject')
        self.assertEqual(apply(self.event('keep',2),refreshed,result)['decisions']['RentInSingapore:365031']['decision'],'keep')
    def test_old_jobs_cannot_overwrite_newer_and_reset_persists(self):
        result=apply(self.event('reset',5),self.data,self.store)
        snapshot=copy.deepcopy(result)
        self.assertEqual(apply(self.event('reject',3),self.data,result),snapshot)
    def test_unauthorized_and_invalid_leave_store_untouched(self):
        for event in [self.event(role='NONE'),self.event('delete')]:
            before=copy.deepcopy(self.store)
            with self.assertRaises(ValueError):apply(event,self.data,self.store)
            self.assertEqual(before,self.store)
    def test_unknown_id_rejected(self):
        with self.assertRaises(ValueError):apply(self.event(),{'listings':[]},self.store)
    def test_other_choices_survive(self):
        self.store['decisions']['Cove:334']={'decision':'keep','issue_number':10}
        apply(self.event(),self.data,self.store)
        self.assertEqual(self.store['decisions']['Cove:334']['decision'],'keep')

if __name__=='__main__':unittest.main()
