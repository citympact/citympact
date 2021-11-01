from django.apps import AppConfig


class MainappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mainApp'


def constant_variables_processor(request):
    return {
        "APP_NAME": "Imp_ACT platform",
    }
