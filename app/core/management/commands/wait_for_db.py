"""
Django management command to wait for the database to activate
"""
import time

from psycopg2 import OperationalError as Psycopg2Error

from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command to wait for database"""

    def handle(self, *args, **extra_fields):
        """Entry point for command"""
        self.stdout.write('Waiting for the database...')
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2Error, OperationalError):
                self.stdout.write(self.style.WARNING(
                    'Database Unavailable, waiting for 1 second...'))
                time.sleep(0.5)

        self.stdout.write(self.style.SUCCESS('Database available!'))
