from hc.api.models import Check
from hc.test import BaseTestCase
from datetime import timedelta as td
from django.utils import timezone


class MyChecksTestCase(BaseTestCase):

    post_data = {
        "interval": 3600,
        "emails": "test1@mail.com; test2@mail.com"
    }

    def setUp(self):
        super(MyChecksTestCase, self).setUp()
        self.client.login(username="alice@example.org", password="password")
        self.check = Check(user=self.alice, name="Alice Was Here")
        self.check.save()

    def test_it_works(self):
        for email in ("alice@example.org", "bob@example.org"):
            self.client.login(username=email, password="password")
            r = self.client.get("/checks/")
            self.assertContains(r, "Alice Was Here", status_code=200)

    def test_it_shows_unresolved(self):
        for email in ("alice@example.org", "bob@example.org"):
            self.client.login(username=email, password="password")
            r = self.client.get("/checks/unresolved")
            self.assertContains(r, "UNRESOLVED", status_code=200)


    def test_it_shows_green_check(self):
        self.check.last_ping = timezone.now()
        self.check.status = "up"
        self.check.save()

        
        r = self.client.get("/checks/")

        # Desktop
        self.assertContains(r, "icon-up")

        # Mobile
        self.assertContains(r, "label-success")

    def test_it_shows_red_check(self):
        self.check.last_ping = timezone.now() - td(days=3)
        self.check.status = "up"
        self.check.save()

        
        r = self.client.get("/checks/")

        # Desktop
        self.assertContains(r, "icon-down")

        # Mobile
        self.assertContains(r, "label-danger")

    def test_it_shows_amber_check(self):
        self.check.last_ping = timezone.now() - td(days=1, minutes=30)
        self.check.status = "up"
        self.check.save()

        
        r = self.client.get("/checks/")

        # Desktop
        self.assertContains(r, "icon-grace")

        # Mobile
        self.assertContains(r, "label-warning")

    def test_owner_can_update_priority(self):
        
        self.post_priority()
        self.check.refresh_from_db()
        self.assertEqual(self.check.priority, 3)

    def test_teammember_can_update_priority(self):
        self.client.login(username="bob@example.org", password="password")
        self.post_priority()
        self.check.refresh_from_db()
        self.assertEqual(self.check.priority, 3)

    def test_nonteammember_cannot_update_priorityr(self):
        self.client.login(username="charlie@example.org", password="password")
        response = self.post_priority()
        self.assertEqual(response.status_code, 403)
        self.check.refresh_from_db()
        self.assertNotEqual(self.check.priority, 3)

    def test_can_enable_escalation(self):

        self.post_data["enabled"] = True
        self.client.post('/checks/' + str(self.check.code) + '/escalations/',
                         self.post_data)
        self.check.refresh_from_db()
        self.assertTrue(self.check.escalation_enabled)
        self.assertEqual(self.check.escalation_interval, td(seconds=3600))
        self.assertEqual(self.check.escalation_list, self.post_data['emails'])

    def test_can_disable_escalation(self):
        
        self.post_data["enabled"] = False
        self.client.post('/checks/' + str(self.check.code) + '/escalations/',
                         self.post_data)
        self.check.refresh_from_db()
        self.assertFalse(self.check.escalation_enabled)

    def post_priority(self):
        return self.client.post('/checks/' + str(self.check.code) + '/priority/',
                                { "priority": 3 })
