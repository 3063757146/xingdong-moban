#!/usr/bin/env python
"""
简单检查订单数据
"""
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GoodShop.settings')
django.setup()

from userapp import models

# 检查订单
orders = models.RechargeOrder.objects.all()
print(f"总订单数: {orders.count()}")

if orders.exists():
    print("\n最近的订单:")
    for order in orders.order_by('-id')[:5]:
        print(f"ID: {order.id}, 订单号: {order.out_trade_no}, 用户: {order.user.uname}, 状态: {order.status}, 金额: {order.amount}")

# 检查用户
users = models.UserInfo.objects.all()
print(f"\n总用户数: {users.count()}")

if users.exists():
    print("\n用户列表:")
    for user in users:
        print(f"用户: {user.uname}, 积分: {user.score}")
