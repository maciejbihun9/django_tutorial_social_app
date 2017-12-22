from django.apps import AppConfig

class ImagesConfig(AppConfig):
    # ścieżka dostępu do aplikacji
    name = 'images'
     # czytelna nazwa aplikacji
    verbose_name = 'Dodawanie obrazów'
    def ready(self):
        # Import procedur obsługi sygnałów.
        import images.signals