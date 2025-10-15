import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GoodShop.settings')
django.setup()

from userapp import models

print("测试开始...")
orders = models.RechargeOrder.objects.all()
print(f"订单数量: {orders.count()}")

if orders.exists():
    latest = orders.order_by('-id').first()
    print(f"最新订单ID: {latest.id}")
    print(f"订单号: {latest.out_trade_no}")
    print(f"状态: {latest.status}")
else:
    print("没有订单")
