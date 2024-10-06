from django.apps import AppConfig
from django.db.models.signals import post_migrate


class MoviesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "movies"

    def ready(self):
        # Ensure signals are side-effect free and no circular imports occur
        import movies.signals  # noqa
        from django.db.models.signals import post_migrate
        from movies.schedule_setup import schedule_setup
        
        # Connect the schedule_setup function to the post_migrate signal
        post_migrate.connect(schedule_setup, sender=self)