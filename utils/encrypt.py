from django.conf import  settings
import hashlib

def md5(data): #md5加密
    obj = hashlib.md5(settings.SECRET_KEY.encode("utf-8"))
#       django配置里面内置了SECRET_KEY 密钥
    obj.update(data.encode("utf-8"))
    return obj.hexdigest()
print(md5("123"))