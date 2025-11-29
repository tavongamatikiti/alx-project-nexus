"""
WSGI config for Vercel deployment.
"""

import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')

try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    app = application
except Exception as e:
    # Log the error for debugging in Vercel logs
    import traceback
    print(f"ERROR: Failed to initialize Django application: {e}")
    print(traceback.format_exc())

    # Create a simple error response
    def app(environ, start_response):
        status = '500 Internal Server Error'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        error_msg = f"Django initialization failed: {str(e)}\n{traceback.format_exc()}"
        return [error_msg.encode()]