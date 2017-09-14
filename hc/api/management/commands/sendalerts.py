import logging
import time

from datetime import timedelta as td
from concurrent.futures import ThreadPoolExecutor
from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone
from hc.api.models import Check
from hc.lib import emails

executor = ThreadPoolExecutor(max_workers=10)
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sends UP/DOWN email alerts'

    def handle_many(self):
        """ Send alerts for many checks simultaneously. """
        query = Check.objects.filter(user__isnull=False).select_related("user")

        now = timezone.now()

        for check in query:
            if check.get_status() == "down":
                if check.escalation_enabled:
                    if not check.escalation_down:
                        if not check.escalation_time:
                            check.escalation_time = now + check.escalation_interval
                            check.save()
                        if check.escalation_time <= now:
                            self.stdout.write(check.name+" is "+check.get_status())
                            check.escalation_down = True
                            check.escalation_up = False
                            check.save()
                            executor.submit(self.escalate_one(check, now))

            elif check.get_status() == "up":
                if check.escalation_enabled and not check.escalation_up:
                    check.escalation_down = False
                    check.escalation_up = True
                    check.escalation_time = None
                    check.save()
                    executor.submit(self.escalate_one(check, now))
        
        going_down = query.filter(alert_after__lt=now, status="up")
        going_up = query.filter(alert_after__gt=now, status="down")
        # Don't combine this in one query so Postgres can query using index:
        checks = list(going_down.iterator()) + list(going_up.iterator())
        if not checks:
            return False

        futures = [executor.submit(self.handle_one, check) for check in checks]
        for future in futures:
            future.result()


        return True

    def escalate_one(self, check, now):
        ctx = {
            "check": check,
            "now": now
        }
        emails.escalate(check.escalation_list, ctx)

    def handle_one(self, check):
        """ Send an alert for a single check.

        Return True if an appropriate check was selected and processed.
        Return False if no checks need to be processed.

        """

        # Save the new status. If sendalerts crashes,
        # it won't process this check again.
        check.status = check.get_status()
        check.save()

        tmpl = "\nSending alert, status=%s, code=%s\n"
        self.stdout.write(tmpl % (check.status, check.code))
        errors = check.send_alert()
        for ch, error in errors:
            self.stdout.write("ERROR: %s %s %s\n" % (ch.kind, ch.value, error))

        connection.close()
        return True

    def handle(self, *args, **options):
        self.stdout.write("sendalerts is now running")

        ticks = 0
        while True:
            if self.handle_many():
                ticks = 1
            else:
                ticks += 1

            time.sleep(1)
            if ticks % 60 == 0:
                formatted = timezone.now().isoformat()
                self.stdout.write("-- MARK %s --" % formatted)
