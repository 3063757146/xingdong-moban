from django.urls import path
from cartapp import views
urlpatterns = [
    path("cart/add/",views.cart_add),
    path("cart/list/",views.cart_list)
#     list页面跳转goods/details/5
]
