#!/usr/bin/env python
"""
修复待支付订单脚本
"""
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GoodShop.settings')
django.setup()

from userapp import models
from userapp.utils.alipay_utils import query_trade_status
import datetime

def fix_pending_orders():
    """检查并修复所有待支付的订单"""
    print("开始检查待支付订单...")
    
    # 获取所有待支付订单
    pending_orders = models.RechargeOrder.objects.filter(status=0)
    
    print(f"找到 {pending_orders.count()} 个待支付订单")
    
    fixed_count = 0
    
    for order in pending_orders:
        print(f"\n检查订单: ID={order.id}, 订单号={order.out_trade_no}")
        
        try:
            # 查询支付宝状态
            trade_result = query_trade_status(order.out_trade_no)
            
            if trade_result:
                trade_status = trade_result.get("trade_status")
                print(f"支付宝状态: {trade_status}")
                
                if trade_status in ["TRADE_SUCCESS", "TRADE_FINISHED"]:
                    print("✅ 发现支付成功，正在更新订单...")
                    
                    # 更新订单状态
                    order.status = 1
                    order.pay_time = datetime.datetime.now()
                    order.save()
                    
                    # 增加用户积分
                    user = order.user
                    old_score = user.score
                    user.score += order.score
                    user.save()
                    
                    print(f"✅ 订单已更新，用户积分: {old_score} -> {user.score}")
                    fixed_count += 1
                    
                elif trade_status == "TRADE_CLOSED":
                    print("❌ 交易已关闭")
                    order.status = 2
                    order.save()
                    
                else:
                    print(f"⏳ 订单状态: {trade_status}")
            else:
                print("❌ 查询支付宝失败")
                
        except Exception as e:
            print(f"❌ 处理订单异常: {e}")
    
    print(f"\n处理完成！共修复了 {fixed_count} 个订单")

if __name__ == "__main__":
    fix_pending_orders()
