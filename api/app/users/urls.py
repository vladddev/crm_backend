from django.urls import path
from .views import *


app_name = 'users'
urlpatterns = [
    path('create/', UserCreateView.as_view()),
    path('me/', CurrentUserDetailView.as_view()),
    path('<int:pk>/', UserDetailView.as_view()),
    path('', UsersListView.as_view()),
]