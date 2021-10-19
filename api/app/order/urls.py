from django.urls import path
from .views import *


app_name = 'orders'
urlpatterns = [
    path('<int:pk>/guest/', GuestOrderDetailView.as_view()),
    path('items/<int:pk>/', ItemDetailView.as_view()),
    path('items/', ItemsListView.as_view()),
    path('<int:pk>/', OrderDetailView.as_view()),
    path('next-order-code/', OrderView.as_view({'get': 'get_next_code'})),
    path('get-document/', OrderView.as_view({'get': 'create_document'})),
    path('', OrdersListView.as_view()),
]

