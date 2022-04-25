from django.core.management import BaseCommand
from django.core.cache import cache


class Command(BaseCommand):
    help = 'Clears Django cache'

    def handle(self, *args, **options):
        cache.clear()
        self.stdout.write('Cleared cache')
