from django.contrib.auth.hashers import make_password
from hc.test import BaseTestCase


class CheckTokenTestCase(BaseTestCase):

    def setUp(self):
        super(CheckTokenTestCase, self).setUp()
        self.profile.token = make_password("secret-token")
        self.profile.save()

    def test_it_shows_form(self):
        r = self.client.get("/accounts/check_token/alice/secret-token/")
        self.assertContains(r, "You are about to log in")

    def test_it_redirects(self):
        r = self.client.post("/accounts/check_token/alice/secret-token/")
        self.assertRedirects(r, "/checks/")

        # After login, token should be blank
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.token, "")

    ### Login and test it redirects already logged in
    def test_redirects_already_logged_in_user(self):
        # login user alice the first time
        self.client.post("/accounts/check_token/alice/secret-token/")

        # login user alice the second time redirects
        response = self.client.get("/accounts/check_token/alice/secret-token/")
        self.assertRedirects(response, "/checks/")

    ### Login with a bad token redirects to login page
    def test_redirects_with_bad_token(self):
        response = self.client.post("/accounts/check_token/alice/bad-token/")
        self.assertRedirects(response, '/accounts/login/')
    
    ### Any other tests?

    ### Login with a bad username redirects to login page
    def test_redirects_with_bad_username(self):
        response = self.client.post("/accounts/check_token/tom/secret-token/")
        self.assertRedirects(response, '/accounts/login/')
