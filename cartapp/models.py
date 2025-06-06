from django.db import models
from userapp.models import  UserInfo
from goodapp.models import Color, Goods, Size


# Create your models here.
class CartItem(models.Model):
    goodsid=models.PositiveIntegerField(verbose_name="商品编号")
    colorid=models.PositiveIntegerField(verbose_name="颜色编号")
    sizeid=models.PositiveIntegerField(verbose_name="尺寸编号")
    count=models.PositiveIntegerField(verbose_name="数量",default=0)
    isdelete=models.BooleanField(default=False)
    user=models.ForeignKey(UserInfo,on_delete=models.CASCADE)
    def __str__(self):
        return "haha"

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