import datetime
import itertools
import json
import os
from pathlib import Path
from typing import Union

from alive_progress import alive_bar
from django.apps import apps
from django.conf import settings
from django.core.management import BaseCommand
from django.core.management import call_command
from django.db import transaction

KEY_FUN_FOR_MODEL = {
    'backend.MealItem': lambda item: (item.school.id, item.cafeteria_id),
    'backend.MealSelection': lambda item: (item.school.id, item.timestamp)
}

KEY_FUN_FOR_DICT = {
    'backend.MealItem': lambda item: (item['school'], item['cafeteria_id']),
    'backend.MealSelection': lambda item: (item['school'], datetime.datetime.fromisoformat(
        item['timestamp'].replace('Z', '+00:00')))  # Fix issue with UTC=Z
}

DATA_FIXTURE_PATH = settings.BASE_DIR / 'backend_data_parsing'
SCHOOLS = ('babson',)


class Command(BaseCommand):
    help = 'Uploads meal data in the form of fixtures to the DB.  '

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.keyfun_cache = {}

    def check_conflict(self, fixture_obj: dict[str, any]) -> Union[None, tuple[int, int]]:
        """
        Checks for conflicts between fixture objects and DB objects.  DB keyfun results are cached
        @param fixture_obj: The fixture being checked
        @return: If a fixture object conflicts (has the same key fun but different PK to another object in the DB), then
        the tuple (new_id, old_id) is returned, where the IDs are PKs of the new (fixture object) and old (DB object)
        objects respectively.  Returns None otherwise
        """

        model_str = fixture_obj['model']
        if model_str not in self.keyfun_cache:
            # expects <app name>, <model class> as args
            Model = apps.get_model(*fixture_obj['model'].split('.', maxsplit=1))
            self.keyfun_cache[model_str] = {KEY_FUN_FOR_MODEL[model_str](obj): obj.id for obj in Model.objects.all()}
        keyfun_dict = self.keyfun_cache[model_str]
        keyfun_eval = KEY_FUN_FOR_DICT[model_str](fixture_obj['fields'])

        if keyfun_eval in keyfun_dict and fixture_obj['pk'] != keyfun_dict[keyfun_eval]:
            return fixture_obj['pk'], keyfun_dict[keyfun_eval]
        else:
            return None

    def add_arguments(self, parser):
        parser.add_argument('-l', '--all', dest='all', action='store_const', const=True, default=False,
                            help='Upload all fixture files found, regardless of which fixture files are specified')
        parser.add_argument('-l', '--list', dest='list', action='store_const', const=True, default=False,
                            help='Lists available fixture files, nothing will be uploaded')
        parser.add_argument('files', nargs='*', type=int,
                            help='List of indices of fixture files to upload.  Use option --list to see available '
                                 'fixture indices, or --all to upload all')

    def handle(self, *args, **options):
        if all(Path(DATA_FIXTURE_PATH / school).exists() for school in SCHOOLS):
            files: list[Path] = list(itertools.chain(*(
                (DATA_FIXTURE_PATH / school / file
                 for file in os.listdir(DATA_FIXTURE_PATH / school) if file.endswith('.json'))
                for school in SCHOOLS)))

            if options['list']:
                self.stdout.write('-- [ Fixture List ] --')
                for i, path in enumerate(files):
                    self.stdout.write(f'- (Index: {i}) {path}')
            else:
                ids = set(list(range(len(files))) if options['all'] else options['files'])
                if not all(0 <= x < len(files) for x in ids):
                    self.stdout.write('Fixture file indices are out of range', self.style.ERROR)
                    return

                cnt = 0
                with transaction.atomic():
                    for i, fixture_path in enumerate(files):
                        if i in ids:
                            self.stdout.write(f'Validating fixture {fixture_path}')
                            with open(fixture_path) as f:
                                # I wanted to use alivebar here, but it wouldn't work as self.check_conflict hangs only
                                # on the first call and nothing else (since it has to create the cache)
                                for obj in json.load(f):
                                    if t := self.check_conflict(obj):
                                        self.stdout.write(f'DB conflict (expected id {t[1]}, got id {t[0]}) with '
                                                          f'object {obj}', self.style.ERROR)
                                        return

                            self.stdout.write(f'Loading fixture {fixture_path}')

                            call_command('loaddata', fixture_path)
                            cnt += 1
                self.stdout.write(f'Loaded {cnt} fixtures')
        else:
            self.stdout.write('Could not find data fixture path for some school.  Please check that '
                              'the backend_data_parsing submodule was cloned correctly', self.style.ERROR)
