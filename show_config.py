#!/usr/bin/env python
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GoodShop.settings')
import django
django.setup()
from django.conf import settings

print("=" * 60)
print("当前支付宝配置")
print("=" * 60)
print(f"AppID: {settings.ALIPAY['appid']}")
print(f"环境: {'沙箱' if settings.ALIPAY['debug'] else '正式'}")
print(f"异步通知: {settings.ALIPAY['notify_url']}")
print("=" * 60)
print("\n✅ 配置正确！")
print("\n接下来请：")
print("1. 访问 https://open.alipay.com/develop/sandbox/app")
print("2. 获取「沙箱买家账号」")
print("3. 用支付宝APP扫码后，使用沙箱账号登录")

