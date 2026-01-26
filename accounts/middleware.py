"""
Middleware to prevent browser caching of authenticated pages.
This ensures users cannot use the back button to access protected pages after logout.
"""

class NoCacheMiddleware:
    """
    Middleware that adds cache control headers to prevent caching of authenticated pages.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Apply no-cache headers to all responses
        # This prevents the browser from serving cached versions of protected pages
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        
        return response
