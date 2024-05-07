# #
# # SEA / SMART ENGINEERING ASSISTANT
# # Copyright (c) 2024 SilentByte <https://silentbyte.com/>
# #

import sys
import os

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

from core import businesslogic
from core.models import UserAccount


def eprint(*args):
    print(*args, file=sys.stderr, flush=True)


class Command(BaseCommand):
    help = 'Creates a Django Super User and an initial system user'

    def handle(self, *args, **options):
        eprint('CREATING ADMIN USER...')

        admin_user_name = os.environ.get('ADMIN_USER_NAME')
        admin_user_email = os.environ.get('ADMIN_USER_EMAIL')
        admin_user_password = os.environ.get('ADMIN_USER_PASSWORD')

        if not admin_user_name or not admin_user_email or not admin_user_password:
            eprint('Skipping admin user creation (credentials not specified)')
            return

        with transaction.atomic():
            if get_user_model().objects.filter(username=admin_user_name).exists():
                eprint('Skipping Django admin user creation (already exists)')
            else:
                get_user_model().objects.create_superuser(
                    username=admin_user_name,
                    email=admin_user_email,
                    password=admin_user_password,
                )

            if UserAccount.objects.filter(email=admin_user_email).exists():
                eprint('Skipping system admin user account creation (already exists)')
            else:
                print('PASSWORD IS ', admin_user_password)
                businesslogic.create_user_account(
                    display_name=admin_user_name,
                    email=admin_user_email,
                    raw_credentials=admin_user_password,
                )
