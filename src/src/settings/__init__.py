"""
Settings package initialization.
Loads appropriate settings based on DJANGO_ENV environment variable.
"""

import os

# Determine which settings to use based on DJANGO_ENV
ENVIRONMENT = os.environ.get("DJANGO_ENV", "dev").lower()

if ENVIRONMENT == "production" or ENVIRONMENT == "prod":
    from .prod import *
elif ENVIRONMENT == "development" or ENVIRONMENT == "dev":
    from .dev import *
else:
    # Default to development settings
    from .dev import *

print(f"✓ Loaded settings for environment: {ENVIRONMENT}")
