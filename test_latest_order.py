#!/usr/bin/env python
"""
测试最新订单的支付状态
"""
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GoodShop.settings')
django.setup()

from userapp import models
from userapp.utils.alipay_utils import query_trade_status

# 获取最新的订单
latest_order = models.RechargeOrder.objects.order_by('-id').first()

if latest_order:
    print(f"最新订单:")
    print(f"ID: {latest_order.id}")
    print(f"订单号: {latest_order.out_trade_no}")
    print(f"用户: {latest_order.user.uname}")
    print(f"金额: {latest_order.amount}")
    print(f"积分: {latest_order.score}")
    print(f"状态: {latest_order.status}")
    print(f"创建时间: {latest_order.create_time}")
    print(f"支付时间: {latest_order.pay_time}")
    
    print(f"\n查询支付宝状态...")
    try:
        trade_result = query_trade_status(latest_order.out_trade_no)
        print(f"支付宝查询结果: {trade_result}")
        
        if trade_result:
            trade_status = trade_result.get("trade_status")
            print(f"交易状态: {trade_status}")
            
            if trade_status in ["TRADE_SUCCESS", "TRADE_FINISHED"]:
                print("✅ 支付宝显示支付成功！")
                print("正在更新订单状态...")
                
                # 更新订单状态
                latest_order.status = 1
                latest_order.save()
                
                # 增加用户积分
                user = latest_order.user
                old_score = user.score
                user.score += latest_order.score
                user.save()
                
                print(f"✅ 订单状态已更新")
                print(f"✅ 用户积分已更新: {old_score} -> {user.score}")
            else:
                print(f"❌ 支付宝显示支付未成功: {trade_status}")
        else:
            print("❌ 查询支付宝失败")
            
    except Exception as e:
        print(f"❌ 查询异常: {e}")
        import traceback
        traceback.print_exc()
else:
    print("没有找到订单")
