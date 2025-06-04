from django.urls import path
from goodapp.views import goodView

urlpatterns = [
    path('goods/list/', goodView.good_list),
    path("goods/details/<int:nid>",goodView.good_details)
#     list页面跳转goods/details/5
]
