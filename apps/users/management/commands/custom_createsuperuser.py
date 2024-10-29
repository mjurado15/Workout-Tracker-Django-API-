from django.contrib.auth.management.commands.createsuperuser import (
    Command as SuperUserCommand,
)
from django.core import exceptions
from django.utils.text import capfirst

from allauth.account.models import EmailAddress


class Command(SuperUserCommand):
    help = "Custom command to create superusers with additional validations"

    def _validate_username(self, username, verbose_field_name, database):
        """Validate username. If invalid, return a string error message."""
        if username:
            emails = EmailAddress.objects.filter(email=username, verified=True)
            if emails.exists():
                return "Error: That %s is already taken." % verbose_field_name

        if not username:
            return "%s cannot be blank." % capfirst(verbose_field_name)

        try:
            self.username_field.clean(username, None)
        except exceptions.ValidationError as e:
            return "; ".join(e.messages)
