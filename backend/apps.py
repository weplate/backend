from django.apps import AppConfig
from django.conf import settings


class BackendConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend'

    def ready(self):
        print('Init Log Messages')
        for k, v in settings.SETTINGS_LOG_MSG:
            print(f'{k}: {v}')
