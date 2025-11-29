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
    err_msg = f"Django initialization failed: {e}"
    err_tb = traceback.format_exc()

    print(f"ERROR: {err_msg}")
    print(err_tb)

    # Create a simple error response (bind captured values at definition time)
    def app(environ, start_response, _msg=err_msg, _tb=err_tb):
        status = '500 Internal Server Error'
        response_headers = [('Content-type', 'text/plain; charset=utf-8')]
        start_response(status, response_headers)
        return [(f"{_msg}\n{_tb}").encode("utf-8")]
