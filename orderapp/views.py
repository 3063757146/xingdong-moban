import uuid
import datetime
from itertools import chain

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.db.models import F
from spyder.dependencies import status

from cartapp.models import CartItem
from orderapp.models import Order, OrderItem
import jsonpickle

from userapp.models import Address
from orderapp.utils.alipay_p3 import  AliPay
from goodapp.models import  Inventory
def order(request):
    addrid = request.GET.get('address',-1)
    payway = request.GET.get('payway','alipay')
    cartitems=request.GET.get('cartitems',None)  #获取到的cartitems是json字符串
    cartitemlist=jsonpickle.loads(cartitems)  #pickle后为字典list
    totolprice=request.GET.get('totolprice')
    print(totolprice)
    # print(type(totolprice))
    # print(totolprice)
    user=request.session["user"] #session直接存的所登录的user对象
    userobj=jsonpickle.loads(user)
    addrobj=userobj.address_set.get(isdefault=True) #反向外键搜索此用户的默认地址

    cartobjlist=[]
    for cart in cartitemlist:
        cartitem=CartItem.objects.filter(**cart,user=userobj).first()
        print(cartitem.count,"count")
        # print(cartitem.goodsid)
        cartobjlist.append(cartitem)

    # print(type(userobj))
    # print(addrobj)
    # print(cartobjlist[0])
    context = {"addrobj":addrobj,"cartobjlist":cartobjlist,"totolprice":totolprice,"userobj":userobj}
    # print("order.html--------")
    return render(request,"order.html",context)

alipayObj = AliPay(appid='9021000149644414', app_notify_url='http://127.0.0.1:8000/order/checkPay/', app_private_key_path='orderapp/keys/my_private_key.txt',
                 alipay_public_key_path='orderapp/keys/alipay_public_key.txt', return_url='http://127.0.0.1:8000/order/checkPay/', debug=True)

def order_pay(request):
    # user = jsonpickle.loads(request.session.get('user', ''))
    # print(user,"user12312")
    totolprice=request.GET.get('totolprice',0.01)
    # print(totolprice)
    # print("order_pay")
    cartitems=request.GET.get('cartitems',None)
    addrid = request.GET.get('address', -1)
    payway = request.GET.get('payway', 'alipay')
    params = {
        'out_trade_num': uuid.uuid4().hex,
        'order_num': datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
        'address': Address.objects.get(id=addrid),
        'user': jsonpickle.loads(request.session.get('user', '')),
        'payway': payway
    }
    orderObj=Order.objects.create(**params)

    cartitems = jsonpickle.loads(cartitems)
    for cart in cartitems:
        OrderItem.objects.create(**cart,order=orderObj)

    urlparam = alipayObj.direct_pay(subject='迈克商城', out_trade_no=orderObj.out_trade_num,
                                    total_amount=totolprice)
    url = alipayObj.gateway + '?' + urlparam
    # print(url)
    # print("sadasdasd")
    user = jsonpickle.loads(request.session.get('user', ''))
    return HttpResponseRedirect(url)
    # return HttpResponse("支32432423付")


def checkpay(request):
    print("-------支付----------")
    # params = {
    #     'out_trade_num': uuid.uuid4().hex,
    #     'order_num': datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
    #     'address': Address.objects.get(id=addrid),
    #     'user': jsonpickle.loads(request.session.get('user', '')),
    #     'payway': payway
    # }
    params = request.GET.dict()
    #获取签名
    sign = params.pop('sign')
    #进行校验
    if alipayObj.verify(params,sign):
        print(params,"---------")
        # 修改订单状态
        Orderobject = Order.objects.filter(out_trade_num=params["out_trade_no"]).first()
        # Orderobject.update(status="待发货")
        Orderobject.status = '待发货'
        Orderobject.save()
        user=Orderobject.user
        # 修改库存
        objItemList = Orderobject.orderitem_set.all()  # 外键反向搜索
        # print(objItemList)
        for obj in objItemList:
            Inventory.objects.filter(goods_id=obj.goodsid, color_id=obj.colorid, size_id=obj.sizeid).update(
                count=F("count") - obj.count)

        # 更新购物车表中数据
        for obj in objItemList:
            user.cartitem_set.filter(goodsid=obj.goodsid, colorid=obj.colorid, sizeid=obj.sizeid,
                                     count=obj.count).delete()
        print("----------支付成功-------")
        return HttpResponse('支付成功！')

    return HttpResponse('支付失败！')


def order_list(request):
    userid=request.session["info"].get("userid")
    print(userid)
    orderlist=Order.objects.filter(user_id=userid,status="待发货").all()
    # print(orderlist,"orderlist")
    # 获取所有订单的订单项
    queryset = list(chain(*[order.orderitem_set.all() for order in orderlist]))

    context = {"queryset": queryset}
    print(queryset)
    return render(request,"order_list.html",context=context)
