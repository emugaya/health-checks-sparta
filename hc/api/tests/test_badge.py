from django.conf import settings
from django.core.signing import base64_hmac

from hc.api.models import Check
from hc.test import BaseTestCase


class BadgeTestCase(BaseTestCase):

    def setUp(self):
        super(BadgeTestCase, self).setUp()
        self.check = Check.objects.create(user=self.alice, tags="foo bar")

    def test_it_rejects_bad_signature(self):
        r = self.client.get("/badge/%s/12345678/foo.svg" % self.alice.username)
        self.assertEqual(r.status_code, 400)

    def test_it_returns_svg(self):
        sig = base64_hmac(str(self.alice.username), "foo", settings.SECRET_KEY)
        sig = sig[:8].decode("utf-8")
        url = "/badge/%s/%s/foo.svg" % (self.alice.username, sig)
        r = self.client.get(url)
        error_message = 'Content-Type header is "image/svg+xml", not "application/json'
        with self.assertRaisesMessage(ValueError, error_message):
            r.json()
            self.assertContains(r.content, "svg")
            self.assertEqual(r.status_code, 200)
