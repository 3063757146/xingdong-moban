from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from xarray.util.generate_ops import inplace

import  re
from userapp import models
from django import forms
import  jsonpickle
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
    pwd = forms.CharField(widget=forms.PasswordInput(render_value=True), label="密码", required=True)
    confirm_pwd = forms.CharField(widget=forms.PasswordInput(render_value=True), label="确认密码", required=True)
    email = forms.CharField(widget=forms.EmailInput(), label="邮箱", required=True)

    class Meta:
        model = models.UserInfo
        fields = ['uname', 'pwd', 'email']  # 确认密码不进入模型

    def clean_uname(self):
        uname = self.cleaned_data['uname']
        if models.UserInfo.objects.filter(uname=uname).exists():
            raise ValidationError("用户名已经存在")
        return uname

    def clean_pwd(self):
        pwd = self.cleaned_data.get("pwd")
        if len(pwd) < 6:
            raise ValidationError("密码必须大于等于六位")
        return md5(pwd)

    def clean_confirm_pwd(self):
        """两次密码一致性比对"""
        pwd = self.cleaned_data.get("pwd")        # 已加密的 md5 值
        confirm = self.cleaned_data.get("confirm_pwd")
        if pwd != md5(confirm):
            raise ValidationError("两次密码输入不一致")
        return confirm
    def clean_email(self):
        email = self.cleaned_data['email']
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            raise ValidationError("邮箱格式不正确（例：user@example.com）")
        if models.UserInfo.objects.filter(email=email).exists():
            raise ValidationError("该邮箱已被注册")
        return email

def register(request):
    if request.method == 'GET':
        form = RegisterForm()
        return render(request,"register.html",{'form':form})
    form = RegisterForm(data=request.POST)
    if form.is_valid():

        request.session.set_expiry(60 * 60 * 24 * 7)  # 7天免登录
        user=form.save()
        request.session["info"]={"uname":form.cleaned_data['uname'],
                                 "userid":user.id}
        request.session['user'] = jsonpickle.dumps(user)

        return redirect("/user/center/") #跳转账户中心
    return render(request, 'register.html', {"form": form})


def center(request):
    user_id = request.session.get("info", {}).get("userid")
    if not user_id:
        return redirect("/user/login/")

    user = models.UserInfo.objects.get(id=user_id)   # 拿到完整用户
    return render(request, "center.html", {"user": user})



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
            request.session["info"] = { "uname": userobj.uname,"userid":userobj.id}
            request.session['user'] = jsonpickle.dumps(userobj)

            # return redirect("/admin/list")
            return redirect("/user/center/") #跳转账户中心
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
