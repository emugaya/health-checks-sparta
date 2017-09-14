""" Contains tests for the profile view """

from django.core import mail
from hc.test import BaseTestCase
from hc.accounts.models import Member, User
from hc.api.models import Check


class ProfileTestCase(BaseTestCase):
    """ Holds tests for the various scenarios when using the profile view. """

    def setUp(self):
        """ Calls super's setup method and logs in a user, Alice, before
        each test is run. """

        super(ProfileTestCase, self).setUp()
        self.client.login(username="alice@example.org", password="password")

    def test_it_sends_set_password_link(self):
        """ Requests to set a password for the logged in user and verifies that
        an email with the link to do so is sent """

        self.client.post("/accounts/profile/", {"set_password": "1"})
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject,
                         'Set password on healthchecks.io')
        self.assertIn("Here's a link to set a password", mail.outbox[0].body)

    def test_it_sends_monthly_report(self):
        """ Creates a check for the user, sends a report and verifies that an
        email with this check as a content is sent to the user """

        Check(name="Test Check", user=self.alice).save()
        self.alice.profile.send_report()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Monthly Report')
        self.assertIn("This is a monthly report sent by healthchecks.io.",
                      mail.outbox[0].body)

    def test_it_sends_daily_report(self):
        """ Creates a check for the user, sends a report and verifies that an
        email with this check as a content is sent to the user """

        Check(name="Test Check", user=self.alice, ).save()
        self.alice.profile.daily_reports_allowed = True
        self.alice.profile.save()
        self.alice.profile.send_report()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Daily Report')
        self.assertIn("This is a daily report sent by healthchecks.io.",
                      mail.outbox[0].body)

    def test_it_sends_weekly_report(self):
        """ Creates a check for the user, sends a report and verifies that an
        email with this check as a content is sent to the user """

        Check(name="Test Check", user=self.alice).save()
        self.alice.profile.weekly_reports_allowed = True
        self.alice.profile.save()
        self.alice.profile.send_report()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Weekly Report')
        self.assertIn("This is a weekly report sent by healthchecks.io.",
                      mail.outbox[0].body)

    def test_it_adds_team_member(self):
        """ Sends an invite to another user, verifies that the invite is
        emailed and confirms that the new users email is among the members
        emails """

        post_data = {"invite_team_member": "1", "email": "frank@example.org"}
        self.client.post("/accounts/profile/", post_data)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('You have been invited to join',
                      mail.outbox[0].subject)
        self.assertIn("You will be able to manage their existing",
                      mail.outbox[0].body)
        member_emails = set()
        for member in self.alice.profile.member_set.all():
            member_emails.add(member.user.email)
        self.assertIn("frank@example.org", member_emails)

    def test_team_access_flag_false(self):
        """ Logs in Charlie whose profile by default doesn't allow team
        access, tests adding Frank to his team which should return
        HTTP forbidden code 403 """

        self.client.login(username="charlie@example.org", password="password")
        post_data = {"invite_team_member": "1", "email": "frank@example.org"}
        response = self.client.post("/accounts/profile/", post_data)
        self.assertEqual(response.status_code, 403)

    def test_it_removes_team_member(self):
        """ Removes Bob from Alice's team and verifies that he's no longer
        on the team"""

        post_data = {"remove_team_member": "1", "email": "bob@example.org"}
        self.client.post("/accounts/profile/", post_data)
        self.assertEqual(Member.objects.count(), 0)
        self.bobs_profile.refresh_from_db()
        self.assertEqual(self.bobs_profile.current_team, None)

    def test_it_sets_team_name(self):
        """ Requests to set Alice's team name and verifies that it's set """

        post_data = {"set_team_name": "1", "team_name": "Alpha Team"}
        self.client.post("/accounts/profile/", post_data)
        self.alice.profile.refresh_from_db()
        self.assertEqual(self.alice.profile.team_name, "Alpha Team")

    def test_it_switches_to_own_team(self):
        """ Logs in Bob whose current team profile was set to Alice's and
        checks that on visiting profile page, the current profile is changed
        to Bobs default """

        self.client.login(username="bob@example.org", password="password")
        self.client.get("/accounts/profile/")
        self.bobs_profile.refresh_from_db()
        self.assertEqual(self.bobs_profile.current_team, self.bobs_profile)

    def test_it_shows_badges(self):
        """ Creates checks with valid and invalid tags for Alice and Bob
        and verifies that only valid tag badges are returned for the
        appropriate users """

        Check.objects.create(user=self.alice, tags="foo a-B_1  baz@")
        Check.objects.create(user=self.bob, tags="bobs-tag")
        response = self.client.get("/accounts/profile/")
        self.assertContains(response, "foo.svg")
        self.assertContains(response, "a-B_1.svg")
        self.assertNotContains(response, "baz@.svg")
        self.assertNotContains(response, "bobs-tag.svg")

    def test_creates_api_key(self):
        """ Calls profile view to create an API key and verifies that it's
        created for the user  """

        self.client.post("/accounts/profile/", {"create_api_key": '1'})
        api_key = User.objects.get(email='alice@example.org').profile.api_key
        self.assertTrue(api_key)

    def test_revokes_api_key(self):
        """ Creates an API key, revokes it and verifies that it's no longer
        existent """
        self.client.post("/accounts/profile/", {"create_api_key": '1'})
        self.client.post("/accounts/profile/", {"revoke_api_key": '1'})
        api_key = User.objects.get(email='alice@example.org').profile.api_key
        self.assertFalse(api_key)
