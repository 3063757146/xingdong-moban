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


    def __str__(self):
        return self.uname


class Address(models.Model):
    aname = models.CharField(max_length=30,verbose_name="收货人")
    aphone = models.CharField(max_length=11,verbose_name="电话")
    addr = models.CharField(max_length=100,verbose_name="详细地址")
    isdefault = models.BooleanField(default=False)
    userinfo = models.ForeignKey(UserInfo,on_delete=models.CASCADE)


    def __str__(self):
        return self.aname