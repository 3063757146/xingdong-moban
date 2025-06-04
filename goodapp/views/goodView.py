from django.http import HttpResponse
from django.shortcuts import render
from goodapp import models
from goodapp.models import Goods
from goodapp.utils.pagination import Pagination
def good_list(request,category_id=2):
    goodList=models.Goods.objects.filter(category_id=category_id)

    categoryList=models.Category.objects.filter() #用于展示类别

    page_object = Pagination(request, goodList,page_size=8)

    # 使用这个分页轮子需要    <link rel="stylesheet" href="{% static 'plugins/bootstrap-3.4.1/css/bootstrap.min.css' %}">
    context = {
        "goodList": page_object.page_queryset,  # 分完页的数据
        "page_string": page_object.html(),  # 生成页码
        "categoryList": categoryList,
        "category_id": category_id
    }
    return render(request, 'good_list.html', context)


#★★★★★推荐功能
def recommend(request,nid):
    #返回最近访问过的四个商品，可用cookie或者session
    good_category=models.Goods.objects.get(id=nid).category_id
    if "c_goodid" not in request.session:
        request.session['c_goodid'] = []
    goodid_list=request.session['c_goodid']
    goodobj_list=[]
    for gid in goodid_list:
        if gid!=nid:#当前详情这个不放在推荐里面
            obj=models.Goods.objects.get(id=gid)
            if obj.category_id==good_category:
#                 必须和当前商品同类别 同女装 /同日用等等
                goodobj_list.append(obj)
    if nid in goodid_list: #如果当前访问的已有 则移到最前面
        goodid_list.remove(nid)
        goodid_list.insert(0,nid)
    else :
        goodid_list.insert(0,nid)
    request.session['c_goodid']=goodid_list
    return goodobj_list[:4]

def good_details(request, nid):
    recommend_list=recommend(request,nid)
    # nid为good的id
    goodObj=models.Goods.objects.get(id=nid)
    context = {"goodObj":goodObj,
               "recommend_list":recommend_list}
    return render(request, "good_details.html",context=context)