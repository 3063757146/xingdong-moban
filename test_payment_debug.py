#!/usr/bin/env python
"""
支付功能调试脚本
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GoodShop.settings')
django.setup()

from django.conf import settings
from userapp import models
from userapp.utils.alipay_utils import get_alipay_client, query_trade_status

def test_alipay_config():
    """测试支付宝配置"""
    print("=" * 50)
    print("支付宝配置检查")
    print("=" * 50)
    
    try:
        print(f"环境变量: {settings.ALIPAY_ENV}")
        print(f"AppID: {settings.ALIPAY['appid']}")
        print(f"网关: {settings.ALIPAY['gateway']}")
        print(f"通知地址: {settings.ALIPAY['notify_url']}")
        print(f"返回地址: {settings.ALIPAY['return_url']}")
        print(f"调试模式: {settings.ALIPAY['debug']}")
        
        # 检查密钥文件
        private_key_path = settings.ALIPAY['private_key_path']
        public_key_path = settings.ALIPAY['public_key_path']
        
        print(f"\n密钥文件检查:")
        print(f"私钥文件: {private_key_path}")
        print(f"私钥存在: {os.path.exists(private_key_path)}")
        
        print(f"公钥文件: {public_key_path}")
        print(f"公钥存在: {os.path.exists(public_key_path)}")
        
        if os.path.exists(private_key_path):
            with open(private_key_path, 'r') as f:
                private_key = f.read()
                print(f"私钥长度: {len(private_key)}")
                print(f"私钥开头: {private_key[:50]}...")
        
        if os.path.exists(public_key_path):
            with open(public_key_path, 'r') as f:
                public_key = f.read()
                print(f"公钥长度: {len(public_key)}")
                print(f"公钥开头: {public_key[:50]}...")
        
        # 测试支付宝客户端初始化
        print(f"\n支付宝客户端测试:")
        alipay = get_alipay_client()
        print("✅ 支付宝客户端初始化成功")
        
    except Exception as e:
        print(f"❌ 配置检查失败: {e}")
        import traceback
        traceback.print_exc()

def test_recent_orders():
    """测试最近的订单"""
    print("\n" + "=" * 50)
    print("最近订单检查")
    print("=" * 50)
    
    try:
        # 获取最近10个订单
        orders = models.RechargeOrder.objects.all().order_by('-id')[:10]
        
        if not orders:
            print("没有找到任何订单")
            return
        
        print(f"找到 {len(orders)} 个订单:")
        
        for order in orders:
            print(f"\n订单ID: {order.id}")
            print(f"订单号: {order.out_trade_no}")
            print(f"用户: {order.user.uname}")
            print(f"金额: {order.amount}")
            print(f"积分: {order.score}")
            print(f"状态: {order.status} ({'待支付' if order.status == 0 else '已支付' if order.status == 1 else '已关闭'})")
            print(f"创建时间: {order.create_time}")
            print(f"支付时间: {order.pay_time}")
            
            # 如果订单状态是待支付，尝试查询支付宝
            if order.status == 0:
                print("尝试查询支付宝状态...")
                try:
                    trade_result = query_trade_status(order.out_trade_no)
                    if trade_result:
                        print(f"支付宝查询结果: {trade_result}")
                    else:
                        print("支付宝查询失败或返回空结果")
                except Exception as e:
                    print(f"查询支付宝异常: {e}")
            
            print("-" * 30)
            
    except Exception as e:
        print(f"❌ 订单检查失败: {e}")
        import traceback
        traceback.print_exc()

def test_users():
    """测试用户积分"""
    print("\n" + "=" * 50)
    print("用户积分检查")
    print("=" * 50)
    
    try:
        users = models.UserInfo.objects.all()
        print(f"找到 {users.count()} 个用户:")
        
        for user in users:
            print(f"用户: {user.uname}, 积分: {user.score}")
            
    except Exception as e:
        print(f"❌ 用户检查失败: {e}")

if __name__ == "__main__":
    test_alipay_config()
    test_recent_orders()
    test_users()
