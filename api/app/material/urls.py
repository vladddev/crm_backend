from django.urls import path
from .views import *


app_name = 'materials'
urlpatterns = [
    path('<int:pk>/', MaterialOrderDetailView.as_view()),
    path('type/', MaterialView.as_view({'get': 'get_pair'})),
    path('', MaterialOrdersListView.as_view()),
]