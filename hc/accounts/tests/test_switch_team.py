""" Contains tests for the switch_team view """

from hc.test import BaseTestCase
from hc.api.models import Check


class SwitchTeamTestCase(BaseTestCase):
    """ Has tests for the several scenarios in the switch_team view """

    def test_it_switches(self):
        """ Creates a check for alice, logs in bob, switches bobs team
        to alice's and checks that bob is able to view alice's check """

        check = Check(user=self.alice, name="This belongs to Alice")
        check.save()
        self.client.login(username="bob@example.org", password="password")
        url = "/accounts/switch_team/%s/" % self.alice.username
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, '/checks/')
        self.assertContains(response, "This belongs to Alice")

    def test_it_checks_team_membership(self):
        """ Logs in charlie who is not a member of alice's team and try's
        to switch to alice's team which should fail with forbidden 403
        error """

        self.client.login(username="charlie@example.org", password="password")
        url = "/accounts/switch_team/%s/" % self.alice.username
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

    def test_it_switches_to_own_team(self):
        """ Logs in alice, tries to switch her team to her own team and
        should get switched redirected 302, to the new teams checks page """

        self.client.login(username="alice@example.org", password="password")
        url = "/accounts/switch_team/%s/" % self.alice.username
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)
