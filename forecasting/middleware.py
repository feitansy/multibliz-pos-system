"""
Middleware to automatically trigger forecast generation.
Checks on each request if forecasts need to be regenerated (every 30 days).
"""
import threading
import logging
import os

logger = logging.getLogger(__name__)


class AutoForecastMiddleware:
    """
    Middleware that checks if forecasts need to be regenerated.
    Runs the generation in a background thread to not block requests.
    Skips during deployment/build processes.
    """
    
    # Class-level flag to prevent multiple simultaneous generations
    _generation_in_progress = False
    _lock = threading.Lock()
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip during build/deployment process
        if not os.environ.get('RENDER'):
            # Only check on dashboard or forecast page access
            if request.path in ['/', '/dashboard/', '/forecasting/']:
                self._check_and_generate_forecasts()
        
        response = self.get_response(request)
        return response
    
    def _check_and_generate_forecasts(self):
        """Check if forecasts need to be generated and trigger if needed"""
        # Avoid circular import
        from forecasting.models import ForecastConfig
        
        try:
            config = ForecastConfig.get_config()
            
            if not config.should_generate():
                return
            
            # Use lock to prevent multiple simultaneous generations
            with self._lock:
                if self._generation_in_progress:
                    return
                
                # Re-check after acquiring lock
                config.refresh_from_db()
                if not config.should_generate():
                    return
                
                self._generation_in_progress = True
            
            # Run generation in background thread
            thread = threading.Thread(target=self._run_forecast_generation)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            logger.error(f"Error checking forecast generation: {e}")
    
    def _run_forecast_generation(self):
        """Run forecast generation in background"""
        from django.core.management import call_command
        
        try:
            logger.info("Starting automatic forecast generation...")
            call_command('auto_generate_forecast', '--force')
            logger.info("Automatic forecast generation completed.")
        except Exception as e:
            logger.error(f"Error during forecast generation: {e}")
        finally:
            with self._lock:
                AutoForecastMiddleware._generation_in_progress = False
