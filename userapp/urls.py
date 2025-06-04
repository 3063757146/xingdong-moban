from django.urls import path
from sqlalchemy.dialects.mssql.information_schema import views

from userapp import views

urlpatterns = [
    path("user/register/", views.register),
    path("user/login/", views.login),
    path("user/center/", views.center),
    path("user/logout/", views.logout),
    path("user/code/",views.user_code),
    path("user/address/",views.address),

    path("user/loadArea/",views.loadArea),
    path("user/updateDefaultAddr/",views.updateDefaultAddrView),
    path("user/addrdelete/",views.addrdelete),

    path("user/addredit/",views.addredit)

]
