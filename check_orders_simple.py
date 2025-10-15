import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GoodShop.settings')
django.setup()

from userapp import models
from userapp.utils.alipay_utils import query_trade_status

print("检查最近的5个订单:")
orders = models.RechargeOrder.objects.order_by('-id')[:5]

for order in orders:
    print(f"\n订单 {order.id}: {order.out_trade_no}")
    try:
        result = query_trade_status(order.out_trade_no)
        if result:
            if result.get('code') == '10000':
                print(f"  查询成功: {result.get('trade_status', '未知')}")
                print(f"  详细信息: {result}")
            else:
                print(f"  查询失败: {result.get('msg', '未知错误')}")
        else:
            print("  查询返回空结果")
    except Exception as e:
        print(f"  查询异常: {e}")

print("\n检查完成")
