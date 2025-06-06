import uuid

from bokeh.server.auth_provider import User
from django.db import models
from goodapp.models import Color,Goods,Size
from userapp.models import Address,UserInfo

class Order(models.Model):
    out_trade_num=models.UUIDField(default=uuid.uuid4)
    order_num=models.CharField(max_length=50)
    trade_no=models.CharField(max_length=120,default="")
    status=models.CharField(max_length=20,default="待支付")
    payway=models.CharField(max_length=20,default="alipay")
    address=models.ForeignKey(Address,on_delete=models.CASCADE)
    user=models.ForeignKey(UserInfo,on_delete=models.CASCADE)
# Create your models here.
    def __str__(self):
        return self.order_num

class OrderItem(models.Model):
    goodsid = models.PositiveIntegerField(verbose_name="商品编号")
    colorid = models.PositiveIntegerField(verbose_name="颜色编号")
    sizeid = models.PositiveIntegerField(verbose_name="尺寸编号")
    count = models.PositiveIntegerField(verbose_name="数量", default=0)
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    def getcolor(self):
        color=Color.objects.filter(id=self.colorid).first()
        return color
    def getgood(self):
        good=Goods.objects.filter(id=self.goodsid).first()
        return good
    def getsize(self):
        size=Size.objects.filter(id=self.sizeid).first()
        return size
    def getTotolPrice(self):
        return self.getgood().price *self.count