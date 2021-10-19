from django.urls import path
from .views import *


app_name = 'system'
urlpatterns = [
    path('menu/', MenuView.as_view({ 'get': 'get_menu' })),
    path('time/', SystemView.as_view({ 'get': 'get_time' })),

    path('specifications-document/', SystemView.as_view({ 'get': 'create_sp_xls' })),
    path('specifications-parse/', SpParserView.as_view()),
    path('fabric-document/', SystemView.as_view({ 'get': 'create_fsp_xls' })),
    path('fabric-parse/', FSpParserView.as_view()),
    path('products-document/', SystemView.as_view({ 'get': 'create_prods_xls' })),
    path('products-parse/', ProdsParserView.as_view()),
    path('consumables-document/', SystemView.as_view({ 'get': 'create_cons_xls' })),
    path('consumables-parse/', ConsParserView.as_view()),

    path('password-reset/', PasswordResetView.as_view({ 'post': 'send_reset_emeil' })),
    path('password-confirm/', PasswordResetView.as_view({ 'post': 'confirm_reset' })),
    path('notifications/<int:pk>/', NotificationDetailsView.as_view()),
    path('notifications/', NotificationsView.as_view({ 'get': 'list', 'post': 'update' })),
    path('user-queries/<int:pk>/', UserChangeQueryDetailView.as_view()),
    path('user-queries/', UserChangeQueryListView.as_view()),
    path('news/<int:pk>/', SystemPostDetailView.as_view()),
    path('news/', SystemPostListView.as_view()),
    path('pages/', PageListView.as_view()),
    path('roles/<int:pk>/', UserRoleDetailView.as_view()),
    path('roles/', UserRoleListView.as_view()),
]