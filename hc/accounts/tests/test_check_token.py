""" Defines tests for the check token view """

from django.contrib.auth.hashers import make_password
from hc.test import BaseTestCase


class CheckTokenTestCase(BaseTestCase):
    """ Holds methods that test the various logic blocks in the check
    token view """

    def setUp(self):
        """ Calls super's setUp method and a test token for Alice's
        profile """

        super(CheckTokenTestCase, self).setUp()
        self.profile.token = make_password("secret-token")
        self.profile.save()

    def test_it_shows_form(self):
        """ Test that the token submit form is shown when a get request
        is made """
        response = self.client.get("/accounts/check_token/alice/secret-token/")
        self.assertContains(response, "You are about to log in")

    def test_it_redirects(self):
        """ Submits a valid username and token, verifies that user is
        redirected to their checks page and the toke removed """

        response = self.client.post("/accounts/check_token/alice/secret-token/")
        self.assertRedirects(response, "/checks/")
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.token, "")

    def test_redirects_already_loggedin(self):
        """ Logs in alice twice and verifies that she's immediately
        redirected to the checks page on the second attempt """

        self.client.post("/accounts/check_token/alice/secret-token/")
        response = self.client.get("/accounts/check_token/alice/secret-token/")
        self.assertRedirects(response, "/checks/")

    def test_redirects_with_bad_token(self):
        """ Logs in a user with an invalid token and verifies that the user is
        redirected to the login page """

        response = self.client.post("/accounts/check_token/alice/bad-token/")
        self.assertRedirects(response, '/accounts/login/')

    def test_redirects_bad_username(self):
        """ Logs in a user with an invalid username and verifies that the user
        is redirected to the login page """

        response = self.client.post("/accounts/check_token/tom/secret-token/")
        self.assertRedirects(response, '/accounts/login/')
