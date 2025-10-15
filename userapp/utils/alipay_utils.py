"""
支付宝支付工具类
"""
import os
from alipay import AliPay
from django.conf import settings


def get_alipay_client():
    """
    获取支付宝客户端实例
    """
    try:
        # 读取私钥文件
        with open(settings.ALIPAY['private_key_path'], 'r') as f:
            app_private_key_string = f.read()
        
        # 读取支付宝公钥文件
        with open(settings.ALIPAY['public_key_path'], 'r') as f:
            alipay_public_key_string = f.read()
        
        alipay = AliPay(
            appid=settings.ALIPAY['appid'],
            app_notify_url=settings.ALIPAY['notify_url'],
            app_private_key_string=app_private_key_string,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",
            debug=settings.ALIPAY['debug']
        )
        
        return alipay
    except Exception as e:
        print(f"支付宝客户端初始化失败: {e}")
        raise e


def create_trade_precreate(order_no, total_amount, subject):
    """
    创建扫码支付订单
    """
    try:
        alipay = get_alipay_client()
        
        result = alipay.api_alipay_trade_precreate(
            out_trade_no=order_no,
            total_amount=str(total_amount),
            subject=subject,
        )
        
        return result
    except Exception as e:
        print(f"创建扫码支付订单失败: {e}")
        raise e


def create_trade_page_pay(order_no, total_amount, subject, return_url=None):
    """
    创建网页支付订单
    """
    try:
        alipay = get_alipay_client()
        
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_no,
            total_amount=str(total_amount),
            subject=subject,
            return_url=return_url or settings.ALIPAY['return_url'],
            notify_url=settings.ALIPAY['notify_url']
        )
        
        # 构建完整支付链接
        pay_url = f"{settings.ALIPAY['gateway']}?{order_string}"
        
        return pay_url
    except Exception as e:
        print(f"创建网页支付订单失败: {e}")
        raise e


def verify_notify(data, sign):
    """
    验证支付宝异步通知签名
    """
    try:
        alipay = get_alipay_client()
        return alipay.verify(data, sign)
    except Exception as e:
        print(f"验证签名失败: {e}")
        return False


def query_trade_status(out_trade_no):
    """
    查询交易状态
    """
    try:
        alipay = get_alipay_client()
        
        result = alipay.api_alipay_trade_query(
            out_trade_no=out_trade_no
        )
        
        return result
    except Exception as e:
        print(f"查询交易状态失败: {e}")
        return None
