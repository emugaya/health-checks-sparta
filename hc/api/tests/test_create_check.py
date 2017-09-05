import json

from django.utils.encoding import force_text
from hc.api.models import Channel, Check
from hc.test import BaseTestCase


class CreateCheckTestCase(BaseTestCase):
    URL = "/api/v1/checks/"

    def setUp(self):
        super(CreateCheckTestCase, self).setUp()

    def post(self, data, expected_error=None, *args, **kwargs):
        r = self.client.post(self.URL, json.dumps(data),
                             content_type="application/json", *args, **kwargs)

        if expected_error:
            self.assertEqual(r.status_code, 400)
            self.assertEqual(json.loads(force_text(r.content))['error'], expected_error)

        return r

    def test_it_works(self):
        r = self.post({
            "api_key": "abc",
            "name": "Foo",
            "tags": "bar,baz",
            "timeout": 3600,
            "grace": 60
        })

        self.assertEqual(r.status_code, 201)

        doc = r.json()

        assert "ping_url" in doc

        self.assertEqual(doc["name"], "Foo")
        self.assertEqual(doc["tags"], "bar,baz")
        self.assertIsNone(doc["last_ping"])
        self.assertIsNone(doc["next_ping"])
        self.assertEqual(Check.objects.count(), 1)

        check = Check.objects.get()

        self.assertEqual(check.name, "Foo")
        self.assertEqual(check.tags, "bar,baz")
        self.assertEqual(check.timeout.total_seconds(), 3600)
        self.assertEqual(check.grace.total_seconds(), 60)

    def test_it_accepts_api_key_in_header(self):
        response = self.post(dict(name="foo"), HTTP_X_API_KEY="abc")
        self.assertEqual(response.status_code, 201)

    def test_it_handles_missing_request_body(self):
        response = self.post(dict(name="foo"))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), dict(error="wrong api_key"))

    def test_it_handles_invalid_json(self):
        response = self.post(dict(name=1, api_key="abc"))
        self.assertEqual(response.status_code, 400)
        error = "could not parse request body"
        self.assertEqual(json.loads(force_text(response.content))['error'], error)

    def test_it_rejects_wrong_api_key(self):
        self.post({"api_key": "wrong"},
                  expected_error="wrong api_key")

    def test_it_rejects_non_number_timeout(self):
        self.post({"api_key": "abc", "timeout": "oops"},
                  expected_error="timeout is not a number")

    def test_it_rejects_non_string_name(self):
        self.post({"api_key": "abc", "name": False},
                  expected_error="name is not a string")

    def test_it_handles_timeout_length(self):
        payload = dict(api_key="abc", name="foo", timeout=59)
        response = self.post(payload)
        self.assertEquals(response.status_code, 400)
        error = "timeout is too small"
        self.assertEqual(json.loads(force_text(response.content))['error'], error)
        payload['timeout'] = 604801
        response = self.post(payload)
        self.assertEquals(response.status_code, 400)
        error = "timeout is too large"
        self.assertEqual(json.loads(force_text(response.content))['error'], error)

    ### Test for the assignment of channels