from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from hc.api.models import Check
from hc.test import BaseTestCase


class LoginTestCase(BaseTestCase):

    def test_it_sends_link(self):
        check = Check()
        check.save()

        session = self.client.session
        session["welcome_code"] = str(check.code)
        session.save()

        form = {"email": "jeff@example.org"}

        r = self.client.post("/accounts/login/", form)
        assert r.status_code == 302

        ### Assert that a user was created
        user = User.objects.get(email=form['email'])
        self.assertEqual(form['email'], user.email)
        # And email sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Log in to healthchecks.io')
        ### Assert contents of the email body
        assert ('To log into healthchecks.io, please ' +
                'open the link below' in mail.outbox[0].body)
                            
        ### Assert that check is associated with the new user
        checks = User.objects.get(email=form['email']).check_set.all()
        print(len(checks))
        self.assertTrue(check in checks)

    def test_it_pops_bad_link_from_session(self):
        self.client.session["bad_link"] = True
        self.client.get("/accounts/login/")
        assert "bad_link" not in self.client.session

    ### Any other tests?

    ### Returns login form on get request
    def test_gives_login_page_on_get_request(self):
        response = self.client.get("/accounts/login/")
        self.assertContains(response, "Please enter your email address.")

    ### Redirects to login link sent page for new user
    def test_redirects_to_login_link_sent_for_new_user(self):
        response = self.client.post("/accounts/login/",
                                    {"email": "test@test.com"})
        self.assertRedirects(response, "/accounts/login_link_sent/")

    ### Redirects to login link sent page for valid email address
    def test_redirects_to_login_link_sent_for_email_only_login(self):
        response = self.client.post("/accounts/login/",
                                    {"email": "alice@example.org"})
        self.assertRedirects(response, "/accounts/login_link_sent/")

    ### Redirects to checks for valid credentials
    def test_redirects_to_checks_for_valid_credentials(self):
        response = self.client.post("/accounts/login/",
                                    {"email": "alice@example.org",
                                     "password": "password"})
        self.assertRedirects(response, "/checks/")
    
    ### Redirects to login page fon invalid credentials
    def test_renders_login_for_invalid_credentials(self):
        response = self.client.post("/accounts/login/",
                                    {"email": "test@test.com",
                                     "password": "pass"})
        self.assertContains(response, "Incorrect email or password.")
