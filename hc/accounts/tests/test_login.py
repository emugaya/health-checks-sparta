""" Contains tests for the login view """

from django.contrib.auth.models import User
from django.core import mail
from hc.api.models import Check
from hc.test import BaseTestCase


class LoginTestCase(BaseTestCase):
    """ Defines tests for the various possibilities in the login
    view """

    def test_it_sends_link(self):
        """ Creates a check, calls login with a new user email, checks that
        a login link is emailed, user is redirected 302, to a page informing
        them of this, add the check is associated to this new user """

        check = Check()
        check.save()
        session = self.client.session
        session["welcome_code"] = str(check.code)
        session.save()
        post_data = {"email": "jeff@example.org"}
        response = self.client.post("/accounts/login/", post_data)
        assert response.status_code == 302
        user = User.objects.get(email=post_data['email'])
        self.assertEqual(post_data['email'], user.email)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Log in to healthchecks.io')
        assert ('To log into healthchecks.io, please ' +
                'open the link below' in mail.outbox[0].body)
        checks = User.objects.get(email=post_data['email']).check_set.all()
        print(len(checks))
        self.assertTrue(check in checks)

    def test_pops_bad_link_from_session(self):
        """ Sets a bad_link session variable and verifies that logging in
        removes it """

        self.client.session["bad_link"] = True
        self.client.get("/accounts/login/")
        assert "bad_link" not in self.client.session

    def test_renders_login_page(self):
        """ Tests that the login page is returned on a get request """

        response = self.client.get("/accounts/login/")
        self.assertContains(response, "Please enter your email address.")

    def test_redirects_new_user(self):
        """ Tests redirection to login link sent page for new user """

        response = self.client.post("/accounts/login/",
                                    {"email": "test@test.com"})
        self.assertRedirects(response, "/accounts/login_link_sent/")

    def test_redirects_email_login_sent(self):
        """ Redirects to login link sent page for valid email only login """

        response = self.client.post("/accounts/login/",
                                    {"email": "alice@example.org"})
        self.assertRedirects(response, "/accounts/login_link_sent/")

    def test_redirects_valid_to_checks(self):
        """ Tests redirects to checks for valid credentials """

        response = self.client.post("/accounts/login/",
                                    {"email": "alice@example.org",
                                     "password": "password"})
        self.assertRedirects(response, "/checks/")

    def test_invalid_credentials(self):
        """ Check if it redirects to login page for invalid credentials """

        response = self.client.post("/accounts/login/",
                                    {"email": "test@test.com",
                                     "password": "pass"})
        self.assertContains(response, "Incorrect email or password.")
