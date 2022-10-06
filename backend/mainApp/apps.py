from django.apps import AppConfig
from impact import settings


class MainappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mainApp'

    # Binding the signals:
    def ready(self):
        import mainApp.signals  # noqa


def constant_variables_processor(request):
    return {
        "APP_NAME": "Citympact platform",
        "CITY_NAME": settings.CITY_NAME,
    }
