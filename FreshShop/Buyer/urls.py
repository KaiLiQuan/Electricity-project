from django.urls import path, include
from Buyer.views import *
urlpatterns = [
    path('register/', register),
    path('login/', login),
    path('index/', index),
    path('logout/', logout),
    path('goods_list/', goods_list),
    path('pay_result/', pay_result),
    path('pay_order/', pay_order),
]

urlpatterns += [
    path('base/', base),

]


# http://127.0.0.1:8000/Buyer/pay_order/?order_id=234&money=6543