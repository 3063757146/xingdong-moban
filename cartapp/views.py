from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F
from cartapp import  models

@csrf_exempt
def cart_add(request):
    goodsid=request.POST['goodsid']
    colorid=request.POST['colorid']
    sizeid=request.POST['sizeid']
    uid=request.session["info"].get("userid")
    flag=request.POST['flag']
    # print(flag)
    # print("---",uid)
    # print(goodsid,colorid,sizeid,count,uid)
    if flag =="add":
        count = request.POST['count']
        models.CartItem.objects.create(goodsid=goodsid,colorid=colorid,sizeid=sizeid,count=count,user_id=uid)
    elif flag=="plus":
        # print(goodsid,"-----------")
        models.CartItem.objects.filter(goodsid=goodsid,colorid=colorid,sizeid=sizeid,user_id=uid).update(count=F('count') + 1)
    #使用f表达式 count在数据库里自增
    elif flag=="minus":
        models.CartItem.objects.filter(goodsid=goodsid,colorid=colorid,sizeid=sizeid,user_id=uid).update(count=F('count') - 1)
    elif flag=="delete":
        # print("-------------")
        # print(goodsid,colorid,sizeid,uid)
        models.CartItem.objects.filter(goodsid=goodsid,colorid=colorid,sizeid=sizeid,user_id=uid).delete()
    return redirect("/cart/list/")


def cart_list(request):
    userid=request.session["info"].get("userid")
    queryset = models.CartItem.objects.filter(user_id=userid)
    context = {"queryset": queryset}
    return render(request,"cartlist.html",context)
# Create your views here.
