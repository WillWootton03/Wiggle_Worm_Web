from django.apps import AppConfig


class WiggleWormConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'wiggle_worm'

    def ready(self):
        import wiggle_worm.signals

