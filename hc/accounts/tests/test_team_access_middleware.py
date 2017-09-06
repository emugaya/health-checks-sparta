""" Holds tests form the team access middleware """

from django.contrib.auth.models import User
from django.test import TestCase
from hc.accounts.models import Profile


class TeamAccessMiddlewareTestCase(TestCase):
    """ Tests the middleware for Team Access """

    def test_it_handles_missing_profile(self):
        """ Creates a user ned, does not assign a profile, logs in and
        checks that the middleware creates a profile for the user when
        they try to visit any page """

        user = User(username="ned", email="ned@example.org")
        user.set_password("password")
        user.save()
        self.client.login(username="ned@example.org", password="password")
        self.client.get("/about/")
        self.assertEqual(Profile.objects.all().count(), 1)
