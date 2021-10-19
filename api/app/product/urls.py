from django.urls import path
from .views import *


app_name = 'products'
urlpatterns = [
    path('get-price/', ProductView.as_view({'get': 'get_price'})),
    path('legs/', LegsListView.as_view()),
    path('molding/', MoldingListView.as_view()),
    path('consumable/', ConsumableListView.as_view()),
    path('consumable/modify/', ProductView.as_view({'post': 'modify_consumables'})),
    path('consumable/load/', ProductView.as_view({'post': 'load_consumables'})),
    path('', ProductsListView.as_view()),
]