from django.apps import AppConfig


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    # added part for execution of signals
    def ready(self) -> None:

        from . import signals

        return super().ready()
        