from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from xarray.util.generate_ops import inplace

from userapp import models
from django import forms

from userapp.models import Address
from utils.forms import BootstrapForm,BootstrapModelForm
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from utils.encrypt import md5
from django import forms
from utils.code import check_code
from io import BytesIO
from django.core.serializers import serialize


class RegisterForm(BootstrapModelForm):
    uname = forms.CharField(widget=forms.TextInput(), label="用户名", required=True)
    pwd = forms.CharField(widget=forms.PasswordInput(render_value=True)
                               , label="密码", required=True)  # required表示前端不填会验证失败
    class Meta:
        model = models.UserInfo
        fields = "__all__"
    def clean_uname(self):
        uname = self.cleaned_data['uname']
        ifexist=models.UserInfo.objects.filter(uname=uname).exists()
        if ifexist:
            raise ValidationError("用户名已经存在")
        return uname

    def clean_pwd(self):
        pwd=self.cleaned_data.get("pwd")
        if len(pwd) < 6:
            raise ValidationError("密码必须大于等于六位")
        return md5(pwd)


def register(request):
    if request.method == 'GET':
        form = RegisterForm()
        return render(request,"register.html",{'form':form})
    form = RegisterForm(data=request.POST)
    if form.is_valid():
        request.session.set_expiry(60 * 60 * 24 * 7)  # 7天免登录
        request.session["info"]={"uname":form.cleaned_data['uname']}
        form.save()
        return redirect("/user/center/") #跳转账户中心
    return render(request, 'register.html', {"form": form})


def center(request):
    # 账户中心
    return render(request,"center.html")



class LoginForm(BootstrapForm):
    uname = forms.CharField(widget=forms.TextInput(),label="用户名",required=True)
    pwd = forms.CharField(widget=forms.PasswordInput(render_value=True)
                               ,label="密码",required=True) #required表示前端不填会验证失败
    code = forms.CharField(widget=forms.TextInput(),label="请输入验证码",required=True)                                  #
    def clean_pwd(self):
        pwd=self.cleaned_data.get("pwd")
        return md5(pwd)#因为数据库存储的是加密后的 此处验证先加密
def login(request):
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'login.html', {"form": form})
    form = LoginForm(request.POST)
    if form.is_valid():
        # form.cleaned_data为{"username":xx,"password":xxx}
        # print(form.cleaned_data)
        code_input = form.cleaned_data.pop("code")  # ⭐ 拿到用户输入的验证码 并且弹出  否则数据库没有code字段报错
        userobj = models.UserInfo.objects.filter(**form.cleaned_data).first()
        if not userobj:
            # form自动给字段名加错误信息
            form.add_error("pwd", "用户名或密码错误")
            return render(request, 'login.html', {"form": form})
            # django自动实现  网站生成随机字符串;写到用户浏览器的cookie中;在数据库写入到session表中;
        code = request.session["code"]
        if code_input == code:  # 验证成功
            request.session.set_expiry(60 * 60 * 24 * 7)  # 7天免登录
            request.session["info"] = { "uname": userobj.uname}
            # return redirect("/admin/list")
            return render(request, "center.html")
        form.add_error("code", "验证码错误")  # ⭐在view加error方法
    return render(request, 'login.html', {"form": form})


def user_code(request):
    img,code_string=check_code()

    request.session["code"] = code_string#写到session中 以便后续校验
    request.session.set_expiry(60)#设置session60s超时
    stream=BytesIO()
    img.save(stream,'png')  #将图片保存在内存中
    return HttpResponse(stream.getvalue())  #前端显示图片
def logout(request):
    request.session.clear()
    return redirect("/user/login/")

class AddressForm(BootstrapModelForm):
    aname = forms.CharField(widget=forms.TextInput(),label="收货人",required=True)
    aphone = forms.CharField(widget=forms.TextInput()
                               ,label="手机号",required=True) #required表示前端不填会验证失败
    class Meta:
        model = models.Address
        fields = ["aname","aphone","addr"]

@csrf_exempt

def address(request):
    uname = request.session["info"]["uname"]
    user = models.UserInfo.objects.get(uname=uname)
    addr_list=models.Address.objects.filter(userinfo=user)
    if request.method == 'GET':
        form=AddressForm()
        return render(request,"address.html",{'form':form,"addr_list":addr_list})
    form=AddressForm(data=request.POST)
    if form.is_valid():
        aname=form.cleaned_data.get("aname")
        aphone=form.cleaned_data.get("aphone")
        addr=form.cleaned_data.get("addr")
        # 同时只有一个isdefault=true
        models.Address.objects.create(aname=aname,aphone=aphone,addr=addr,userinfo=user,isdefault=(lambda count:True if count==0 else False)(user.address_set.count()))
        return JsonResponse({"status": True})
    return JsonResponse({"status": False,"error":form.errors})

def loadArea(request):
    pid = request.GET.get('pid', -1)
    pid = int(pid)
    areaList = models.Area.objects.filter(parentid=pid)
    jareaList = serialize('json',areaList)

    res={"status":True,"jareaList":jareaList}

    return JsonResponse(res)


def updateDefaultAddrView(request):
    #获取请求参数
    addrid = request.GET.get('addrid',-1)
    addrid = int(addrid)
    #修改数据 设置id的默认为true 其他的都置为false
    Address.objects.filter(id=addrid).update(isdefault=True)
    Address.objects.exclude(id=addrid).update(isdefault=False)

    return HttpResponseRedirect('/user/address/')

def addrdelete(request):
    print("delete")
    addrid = request.GET.get('addrid',-1)
    addrid = int(addrid)
    Address.objects.filter(id=addrid).delete()
    return HttpResponseRedirect('/user/address/')



class AddressEditForm(BootstrapModelForm):
    aname = forms.CharField(widget=forms.TextInput(),label="收货人",required=True)
    aphone = forms.CharField(widget=forms.TextInput()
                               ,label="手机号",required=True) #required表示前端不填会验证失败
    class Meta:
        model = models.Address
        fields = ["aname","aphone","addr"]


@csrf_exempt
def addredit(request):
    addrid = request.GET.get('addrid')
    uname = request.session["info"]["uname"]
    user = models.UserInfo.objects.get(uname=uname)
    print("------------",addrid)
    form = AddressForm(data=request.POST)
    if form.is_valid():
        aname = form.cleaned_data.get("aname")
        aphone = form.cleaned_data.get("aphone")
        addr = form.cleaned_data.get("addr")
        print("修改----------------")
        # 同时只有一个isdefault=true
        Address.objects.filter(id=addrid).update(aname=aname,aphone=aphone,addr=addr,userinfo=user,isdefault=(lambda count:True if count==0 else False)(user.address_set.count()))
        return JsonResponse({"status": True})
    return JsonResponse({"status": False, "error": form.errors})