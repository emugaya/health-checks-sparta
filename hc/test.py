""" Defines a base test for all other tests """

from django.contrib.auth.models import User
from django.test import TestCase

from hc.accounts.models import Member, Profile


class BaseTestCase(TestCase):
    """ Sets up parameters required by all tests """

    def setUp(self):
        """ Calls super's setUp, Creates three users; alice with team
        access enabled, bob on alice's team, and charlie. """

        super(BaseTestCase, self).setUp()
        self.alice = User(username="alice", email="alice@example.org")
        self.alice.set_password("password")
        self.alice.save()
        self.profile = Profile(user=self.alice, api_key="abc")
        self.profile.team_access_allowed = True
        self.profile.save()

        self.bob = User(username="bob", email="bob@example.org")
        self.bob.set_password("password")
        self.bob.save()
        self.bobs_profile = Profile(user=self.bob)
        self.bobs_profile.current_team = self.profile
        self.bobs_profile.save()
        member = Member(team=self.profile, user=self.bob)
        member.save()

        self.charlie = User(username="charlie", email="charlie@example.org")
        self.charlie.set_password("password")
        self.charlie.save()
