import base64
import os
import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core import signing
from django.db import models
from django.urls import reverse
from django.utils import timezone
from hc.lib import emails


class Profile(models.Model):
    # Owner:
    user = models.OneToOneField(User, blank=True, null=True)
    team_name = models.CharField(max_length=200, blank=True)
    team_access_allowed = models.BooleanField(default=False)
    next_report_date = models.DateTimeField(null=True, blank=True)
    daily_reports_allowed = models.BooleanField(default=False)
    monthly_reports_allowed = models.BooleanField(default=True)
    weekly_reports_allowed = models.BooleanField(default=False)
    ping_log_limit = models.IntegerField(default=100)
    token = models.CharField(max_length=128, blank=True)
    api_key = models.CharField(max_length=128, blank=True)
    current_team = models.ForeignKey("self", null=True)

    def __str__(self):
        return self.team_name or self.user.email

    def send_instant_login_link(self, inviting_profile=None):
        token = str(uuid.uuid4())
        self.token = make_password(token)
        self.save()

        path = reverse("hc-check-token", args=[self.user.username, token])
        ctx = {
            "login_link": settings.SITE_ROOT + path,
            "inviting_profile": inviting_profile
        }
        emails.login(self.user.email, ctx)

    def send_set_password_link(self):
        token = str(uuid.uuid4())
        self.token = make_password(token)
        self.save()

        path = reverse("hc-set-password", args=[token])
        ctx = {"set_password_link": settings.SITE_ROOT + path}
        emails.set_password(self.user.email, ctx)

    def set_api_key(self):
        self.api_key = base64.urlsafe_b64encode(os.urandom(24))
        self.save()

    def send_report(self):
        # reset next report date first:
        now = timezone.now()

        def save_daily_reports():
            self.next_report_date = now + timedelta(days=1)
            self.save()

        def save_weekly_reports():
            self.next_report_date = now + timedelta(days=7)
            self.save()

        def save_monthly_reports():
            self.next_report_date = now + timedelta(days=30)
            self.save()

        def set_status():
            if self.daily_reports_allowed:
                return "daily"
            elif self.weekly_reports_allowed:
                return "weekly"
            else:
                return "monthly"

        def set_checks():
            if self.daily_reports_allowed:
                return self.user.check_set.filter(created__date=now.date()).order_by("created")

            elif self.weekly_reports_allowed:
                start_date = now.date() - timedelta(days=7)
                return self.user.check_set.filter(created__gt=start_date).order_by("created")

            return self.user.check_set.order_by("created")

        if self.daily_reports_allowed:
            save_daily_reports()

        elif self.weekly_reports_allowed and not all(
                [self.daily_reports_allowed, self.monthly_reports_allowed]):
            save_weekly_reports()

        elif self.monthly_reports_allowed and not all(
                [self.weekly_reports_allowed, self.daily_reports_allowed]):
            save_monthly_reports()

        elif self.daily_reports_allowed and \
                (self.weekly_reports_allowed or self.monthly_reports_allowed):
            save_daily_reports()

        elif self.monthly_reports_allowed and self.weekly_reports_allowed:
            save_weekly_reports()

        elif all(
                [self.monthly_reports_allowed, self.weekly_reports_allowed,
                 self.daily_reports_allowed]):
            save_daily_reports()

        else:
            save_daily_reports()

        token = signing.Signer().sign(uuid.uuid4())
        path = reverse("hc-unsubscribe-reports", args=[self.user.username])
        unsub_link = "%s%s?token=%s" % (settings.SITE_ROOT, path, token)

        ctx = {
            "checks": set_checks(),
            "status": set_status(),
            "now": now,
            "unsub_link": unsub_link
        }

        emails.report(self.user.email, ctx)

    def invite(self, user):
        member = Member(team=self, user=user)
        member.save()

        # Switch the invited user over to the new team so they
        # notice the new team on next visit:
        user.profile.current_team = self
        user.profile.save()

        user.profile.send_instant_login_link(self)


class Member(models.Model):
    team = models.ForeignKey(Profile)
    user = models.ForeignKey(User)
