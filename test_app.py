import io
import unittest
import numpy as np
from app import app, verify
from generate_samples import scene, generate

class VerificationTests(unittest.TestCase):
    def test_complete(self): self.assertTrue(verify(scene([1,2,3]))['verified'])
    def test_missing(self): self.assertFalse(verify(scene([1,2]))['verified'])
    def test_extra(self): self.assertFalse(verify(scene([1,2,3,3]))['verified'])
    def test_unknown(self): self.assertEqual(verify(scene([1,2,3,4]))['unexpected'], {'4':1})
    def test_blank(self): self.assertFalse(verify(np.full((400,400,3),255,np.uint8))['verified'])
    def test_invalid_upload(self):
        response=app.test_client().post('/verify',data={'image':(io.BytesIO(b'invalid'),'bad.png')})
        self.assertEqual(response.status_code,400)
    def test_sample_endpoint(self):
        generate()
        response=app.test_client().post('/verify',data={'sample':'complete'})
        self.assertTrue(response.json['verified'])
    def test_home(self): self.assertEqual(app.test_client().get('/').status_code,200)

if __name__ == '__main__': unittest.main()
