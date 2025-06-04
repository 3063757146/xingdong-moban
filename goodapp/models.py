
from django.db import models

# Create your models here.

# 从表依赖底层往下写，先把外键所依赖的写上
class Category(models.Model):
    """类别表"""
    cname = models.CharField(max_length=10)#类别名称

    def __str__(self):
        return self.cname


class Goods(models.Model):
    """商品表"""
    gname = models.CharField(verbose_name='商品名称',max_length=100)
    gdesc = models.CharField(verbose_name='商品描述',max_length=100)
    oldprice = models.DecimalField(verbose_name='原价',max_digits=5,decimal_places=2)
    price = models.DecimalField(verbose_name='现价',max_digits=5,decimal_places=2)
    category = models.ForeignKey(Category,on_delete=models.CASCADE,verbose_name='类别ID')

    def __str__(self):
        return self.gname
    def getImgUrl(self):
        return self.inventory_set.first().color.colorurl
#      外键反向关联inventory表 获取color对象的colorurl 向前端传输图片地址

    def getColors(self):
#         获取该商品所有的颜色对象
        colors=[]
        for item in self.inventory_set.all():
            color=item.color
            if color not in colors:
                colors.append(color)
        return colors
    def getSizes(self):
        #         获取该商品所有的尺寸对象
        sizes = []
        for item in self.inventory_set.all():
            size = item.size
            if size not in sizes:
                sizes.append(size)
        return sizes
    def getDetailsDict(self):
        datas={}
        for detail in self.goodsdetail_set.all():
            detailname=detail.getDname()
            if detailname not in datas:
                datas[detailname]=[detail.gdurl]
            else :
                datas[detailname].append(detail.gdurl)
        return datas
class GoodsDetailName(models.Model):
    """详情名称表"""
    gdname = models.CharField(verbose_name='详情名称',max_length=30)


    def __str__(self):
        return self.gdname

class GoodsDetail(models.Model):
    """商品详情表"""
    gdurl = models.ImageField(verbose_name='详情图片地址',upload_to='')
    detailname = models.ForeignKey(GoodsDetailName,on_delete=models.CASCADE)
    goods = models.ForeignKey(Goods,on_delete=models.CASCADE)

    def __str__(self):
        return self.detailname.gdname
    def getDname(self):
        return  self.detailname.gdname

class Size(models.Model):
    """尺寸表"""
    sname = models.CharField(verbose_name='尺寸名称',max_length=10)

    def __str__(self):
        return self.sname

class Color(models.Model):
    colorname = models.CharField(verbose_name='颜色名称',max_length=10)
    colorurl = models.ImageField(verbose_name='颜色图片地址',upload_to='color/')


    def __str__(self):
        return self.colorname


class Inventory(models.Model):
    """库存表"""
    count = models.PositiveIntegerField(verbose_name='库存数量')
    color = models.ForeignKey(Color,on_delete=models.CASCADE)
    goods = models.ForeignKey(Goods,on_delete=models.CASCADE)
    size = models.ForeignKey(Size,on_delete=models.CASCADE)





