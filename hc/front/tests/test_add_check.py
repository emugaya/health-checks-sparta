from hc.api.models import Check, Ping, User
from hc.accounts.models import Profile
from hc.test import BaseTestCase


class AddCheckTestCase(BaseTestCase):

    def test_it_works(self):
        url = "/checks/add/"
        self.client.login(username="alice@example.org", password="password")
        r = self.client.post(url)
        self.assertRedirects(r, "/checks/")
        assert Check.objects.count() == 1

    ### Test that team access works
    def test_team_access_works(self):
        url = "/checks/add/"

        # Logging in as bob, not alice. bob is on Alice's team
        self.client.login(username="bob@example.org", password="password")
        self.client.post(url)

        # Logging in as charlie. charlie has no team access
        self.client.login(username="charlie@example.org", password="password")
        self.client.post(url)

        alice = User.objects.get(email="alice@example.org")

        # Alice should access only the team's check
        assert Check.objects.filter(user=alice).count() == 1
