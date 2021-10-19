from django.urls import path
from .views import *


app_name = 'workpoints'
urlpatterns = [
    path('', WorkpointsListView.as_view()),
]