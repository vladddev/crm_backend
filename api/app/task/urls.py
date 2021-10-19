from django.urls import path
from .views import *


app_name = 'tasks'
urlpatterns = [
    path('<int:pk>/', TaskDetailView.as_view()),
    path('mass/', TasksViewset.as_view({ 'post': 'mass_create' })),
    path('', TasksListView.as_view()),
]