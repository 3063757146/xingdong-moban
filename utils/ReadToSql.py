#将爬取的jiukuaijiu.json写入数据库
#https://jsonviewer.stack.hu/  可以可视化json数据
import os
import django

# 设置环境变量
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "GoodShop.settings")

# 初始化 Django
django.setup()
import  json
from django.db.transaction import atomic
# 事务是一组数据库操作，这些操作要么全部成功，要么全部失败

from goodapp.models import *
@atomic
def read():
    with open("jiukuaijiu.json") as fr:
        datas = json.loads(fr.read())  #将数据读成字典列表格式
    #     自底向下剥出数据 插入数据库
    for data in datas:
        cate=Category.objects.create(cname=data['category'])
        _goods=data['goods']
        for goods in _goods:
            good=Goods.objects.create(gname=goods["goodsname"],gdesc=goods["goods_desc"]
                                      ,oldprice=goods['goods_oldprice'],price=goods['goods_price']
                                      ,category=cate)
                                    #外键插入时授对象
            sizes=[]
            for _size in goods["sizes"]:
                if Size.objects.filter(sname=_size[0]).count() == 1:
                    #此尺寸已经存在
                    size=Size.objects.get(sname=_size[0])  #获取此对象
                else :
                    size=Size.objects.create(sname=_size[0])
                sizes.append(size)
            colors=[]
            for color in goods["colors"]:
                color=Color.objects.create(colorname=color[0],colorurl=color[1])
                # 不同商品颜色不一样(图片存的是该商品的各种颜色)
                colors.append(color)
            for spec in goods["specs"]:
                if GoodsDetailName.objects.filter(gdname=spec[0]).count() == 1:
                    goodsdetail=GoodsDetailName.objects.get(gdname=spec[0])
                else:
                    goodsdetail=GoodsDetailName.objects.create(gdname=spec[0])
                for imgurl in spec[1]:  #spec是一个url列表
                    GoodsDetail.objects.create(goods=good,detailname=goodsdetail,gdurl=imgurl)
            for c in colors:
                for s in sizes:
                    Inventory.objects.create(count=100,goods=good,color=c,size=s)
                    # 默认库存100

read()