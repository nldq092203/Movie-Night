"""
ASGI config for movienight project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from chat.jwt_middleware import JWTAuthMiddleware
from configurations.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movienight.settings')
os.environ.setdefault('DJANGO_CONFIGURATION', 'Prod')

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

import chat.routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": 
            JWTAuthMiddleware(URLRouter(chat.routing.websocket_urlpatterns))
        ,
})

