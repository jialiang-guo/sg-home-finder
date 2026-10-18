import unittest
from sources import parse_amenities, parse_ris
class Amenities(unittest.TestCase):
    def test_explicit_facilities(self):
        a=parse_amenities(['Facilities: gym, swimming pool, BBQ pits and tennis court'])
        for k in ('gym','pool','bbq','tennis'): self.assertIs(a[k]['value'],True)
        self.assertIsNone(a['security']['value'])
    def test_absent_is_unknown(self):
        self.assertTrue(all(v['value'] is None for v in parse_amenities(['Condo master room']).values()))
    def test_negative_and_nearby(self):
        self.assertIs(parse_amenities(['No gym'])['gym']['value'],False)
        self.assertIsNone(parse_amenities(['Public swimming pool nearby'])['pool']['value'])
        self.assertIsNone(parse_amenities(['No gym or swimming pool'])['pool']['value'])
    def test_conflicting_claims(self):
        self.assertIsNone(parse_amenities(['Gym','No gym'])['gym']['value'])
    def test_related_room_facilities_ignored(self):
        a=parse_ris('<h1>Room</h1><p>Room details</p><p>2000 SGD per month</p><p>Gym</p><p>Related listings</p><p>Swimming pool</p>','https://rentinsingapore.com.sg/ID123')
        self.assertIs(a['amenities']['gym']['value'],True)
        self.assertIsNone(a['amenities']['pool']['value'])
