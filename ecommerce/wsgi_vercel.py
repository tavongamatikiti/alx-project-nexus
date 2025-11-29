"""
WSGI config for Vercel deployment.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')

# Get the WSGI application
application = get_wsgi_application()

# Vercel serverless function handler
app = application