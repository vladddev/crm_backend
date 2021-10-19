from datetime import datetime
from django.urls import path
from django.contrib import admin
from django.conf.urls import url, include
from django.conf.urls.static import static

from rest_framework import routers, serializers, viewsets
from app.views import *
from . import settings

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/orders/', include('app.order.urls')),
    path('api/v1/materials/', include('app.material.urls')),
    path('api/v1/tasks/', include('app.task.urls')),
    path('api/v1/users/', include('app.users.urls')),
    path('api/v1/system/', include('app.system.urls')),
    path('api/v1/products/', include('app.product.urls')),
    path('api/v1/workpoints/', include('app.workpoints.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT, show_indexes=True) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT, show_indexes=True) 

# handler404 = 'app.views.handler404'