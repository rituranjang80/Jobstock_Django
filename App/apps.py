"""
App Configuration for Job Board Integration
Registers signals automatically
"""
from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'App'
    verbose_name = 'Reetch Application'
    
    def ready(self):
        """
        Import signals when the app is ready
        This ensures signals are registered
        """
        try:
            # Import job board signals
            import App.signals.job_board_signals
        except ImportError:
            pass
    
    def ready(self):
        """Import signals when app is ready"""
        import App.signals
