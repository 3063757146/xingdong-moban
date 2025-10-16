from django.urls import path
from sqlalchemy.dialects.mssql.information_schema import views
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.views.generic.base import RedirectView
from userapp import views

urlpatterns = [
    path('', RedirectView.as_view(url='/user/login/', permanent=True)),
    path("user/register/", views.register),
    path("user/login/", views.login),
    path("user/center/", views.center),
    path("user/logout/", views.logout),
    path("user/code/",views.user_code),
    path('user/recharge/', views.recharge_page, name='recharge'),          # 充值页（弹窗）
    path('user/alipay_qrcode/', views.alipay_qrcode, name='alipay_qrcode'), # 获取二维码
    path('user/query_order/<int:oid>/', views.query_order, name='query_order'), # 轮询订单状态
    path('user/alipay_notify/', views.alipay_notify, name='alipay_notify'), # 异步通知
    # path('user/simulate_pay/', views.simulate_pay, name='simulate_pay'),   # 模拟支付（测试用）
    # path('user/test_pay/', views.test_pay, name='test_pay'),
    # path('user/manual_check/', views.manual_check_payment, name='manual_check'),
    # path('user/payment_test/', views.payment_test_page, name='payment_test'),               # 测试支付（直接到账）
    path('test/', lambda r: HttpResponse("Django OK")),
]
