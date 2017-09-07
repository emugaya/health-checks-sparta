from hc.api.models import Check
from hc.test import BaseTestCase


class PauseTestCase(BaseTestCase):

    def test_it_works(self):
        check = Check(user=self.alice, status="up")
        check.save()

        url = "/api/v1/checks/%s/pause" % check.code
        r = self.client.post(url, "", content_type="application/json",
                             HTTP_X_API_KEY="abc")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(check.status, "up")

    def test_it_validates_ownership(self):
        check = Check(user=self.bob, status="up")
        check.save()

        url = "/api/v1/checks/%s/pause" % check.code
        r = self.client.post(url, "", content_type="application/json",
                             HTTP_X_API_KEY="abc")

        self.assertEqual(r.status_code, 400)

        r = self.client.put(url, "", content_type="application/json",
                            HTTP_X_API_KEY="abc")

        self.assertEqual(r.status_code, 405)
