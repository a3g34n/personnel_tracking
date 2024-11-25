import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import notifications.routing  # Notifications routing'e erişim

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'personnel_tracker.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            notifications.routing.websocket_urlpatterns  # WebSocket yönlendirme
        )
    ),
})
