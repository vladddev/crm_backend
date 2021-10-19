from app.middleware import TokenAuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from app.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    'websocket': TokenAuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
