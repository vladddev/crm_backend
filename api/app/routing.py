from django.urls import path
from django.conf.urls import url, include
from app.consumers import GeneralConsumer

websocket_urlpatterns = [
    url(r"ws/$", GeneralConsumer.as_asgi()),
]