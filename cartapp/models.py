from django.db import models
from userapp.models import  UserInfo
# Create your models here.
class CartItem(models.Model):
    goodid=models.PositiveIntegerField(verbose_name="商品编号")
    colorid=models.PositiveIntegerField(verbose_name="颜色编号")
    sizeid=models.PositiveIntegerField(verbose_name="尺寸编号")
    count=models.PositiveIntegerField(verbose_name="数量",default=0)
    isdelete=models.BooleanField(default=False)
    user=models.ForeignKey(UserInfo,on_delete=models.CASCADE)
    def __str__(self):
        return self.goodid