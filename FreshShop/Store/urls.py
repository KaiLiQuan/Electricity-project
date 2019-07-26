from django.urls import path,re_path
from Store.views import *

urlpatterns = [
    path('register/', register),
    path('login/', login),
    path('index/', index),
    re_path('^$', index),
    path('register_store/', register_store),
    path('add_goods/', add_goods),
    re_path(r'list_goods/(?P<state>\w+)', list_goods),
    re_path(r'^goods/(?P<goods_id>\d+)', goods),
    re_path(r'update_goods/(?P<goods_id>\d+)', update_goods),
    re_path(r'set_goods/(?P<state>\w+)/', set_goods),
    path('Logout/', logout),
    path('list_goods_type/', list_goods_type),
    path('delete_goods_type/', delete_goods_type),

]

urlpatterns +=[
    path('base/', base),
]