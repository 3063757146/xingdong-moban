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


