from django.apps import AppConfig


class MoviesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "movies"

    def ready(self):
        # Ensure signals are side-effect free and no circular imports occur
        import movies.signals # noqa
