from django.db import models

# Create your models here.

class Area(models.Model):
    areaid = models.IntegerField(primary_key=True)
    areaname = models.CharField(max_length=50)
    parentid = models.IntegerField()
    arealevel = models.IntegerField()
    status = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'area'


class UserInfo(models.Model):
    uname = models.CharField(max_length=100,verbose_name="用户名")
    pwd = models.CharField(max_length=100,verbose_name="密码")
    score=models.IntegerField(default=100,verbose_name="用户积分")
    email=models.CharField(max_length=25,default="default@163.com",verbose_name="邮箱")

    def __str__(self):
        return self.uname


class RechargeOrder(models.Model):
    STATUS_CHOICES = (
        (0, "待支付"),
        (1, "已支付"),
        (2, "已关闭"),
    )
    user = models.ForeignKey(UserInfo, on_delete=models.CASCADE, verbose_name="用户")
    out_trade_no = models.CharField(max_length=64, unique=True, verbose_name="商户订单号")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="金额")
    score = models.IntegerField(default=0, verbose_name="赠送积分")
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=0)
    create_time = models.DateTimeField(auto_now_add=True)
    pay_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "recharge_order"


