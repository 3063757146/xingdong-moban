from django.urls import path
from orderapp import views
urlpatterns = [
    path("order/",views.order),
    path("order/pay/",views.order_pay),
    path("order/checkPay/",views.checkpay),
    path("order/list/",views.order_list),
]
