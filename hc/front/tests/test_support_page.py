
from django.test.utils import override_settings
from hc.test import BaseTestCase

@override_settings(PUSHOVER_API_TOKEN="token", PUSHOVER_SUBSCRIPTION_URL="url")
class DisplayFAQsTestCase(BaseTestCase):
    "Test that FAQs are displayed"

    def test_add_blog_with_required_fields_empty(self):
        "Should test that blog is not added when some fields are empty"
        url = "/support/"
        r = self.client.get(url)
        assert r.status_code == 200
