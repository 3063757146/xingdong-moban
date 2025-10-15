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
import uuid
import datetime
from django.conf import settings
from django.db import transaction

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


# ==================== 支付宝支付功能 ====================
# 延迟初始化 alipay SDK（避免启动时密钥文件不存在报错）
_alipay = None
_alipay_appid = None  # 记录当前初始化的 AppID

def get_alipay():
    """获取支付宝 SDK 实例，支持配置热更新"""
    global _alipay, _alipay_appid
    
    current_appid = settings.ALIPAY["appid"]
    
    # 如果 AppID 变化了，重新初始化
    if _alipay is None or _alipay_appid != current_appid:
        try:
            from alipay import AliPay
            print(f"[支付宝] 初始化 SDK - AppID: {current_appid}, Debug: {settings.ALIPAY['debug']}")
            _alipay = AliPay(
                appid=current_appid,
                app_notify_url=settings.ALIPAY["notify_url"],
                app_private_key_string=open(settings.ALIPAY["private_key_path"]).read(),
                alipay_public_key_string=open(settings.ALIPAY["public_key_path"]).read(),
                sign_type="RSA2",
                debug=settings.ALIPAY["debug"]
            )
            _alipay_appid = current_appid
            print(f"[支付宝] SDK 初始化成功")
        except Exception as e:
            print(f"[支付宝] SDK 初始化失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    return _alipay


def recharge_page(request):
    """充值弹窗页，单独模板"""
    return render(request, "recharge.html")


def alipay_qrcode(request):
    """下单并返回二维码地址"""
    user = request.session.get("info")
    if not user:
        return JsonResponse({"code": 401, "msg": "请先登录"})
    
    alipay = get_alipay()
    if not alipay:
        return JsonResponse({"code": 500, "msg": "支付功能未配置，请检查密钥文件"})
    
    out_trade_no = str(uuid.uuid4()).replace("-", "")
    amount = 0.1  # 0.1 元
    score = 10   # 送 10 积分
    
    # 创建订单
    order = models.RechargeOrder.objects.create(
        user_id=user["userid"],
        out_trade_no=out_trade_no,
        amount=amount,
        score=score
    )
    
    # 调用支付宝当面付（生成二维码）
    try:
        result = alipay.api_alipay_trade_precreate(
            subject="GoodShop-积分充值",
            out_trade_no=out_trade_no,
            total_amount=str(amount)
        )
        
        # 打印完整返回结果用于调试
        print(f"支付宝返回结果: {result}")
        
        # 检查返回结果
        if isinstance(result, dict):
            # 检查是否有错误
            if "code" in result and result["code"] != "10000":
                error_msg = result.get("msg", "未知错误") + " - " + result.get("sub_msg", "")
                print(f"支付宝接口错误: {error_msg}")
                return JsonResponse({"code": 500, "msg": f"支付宝接口错误: {error_msg}"})
            
            # 获取二维码
            qr = result.get("qr_code")
            if not qr:
                print(f"未找到二维码，完整响应: {result}")
                return JsonResponse({"code": 500, "msg": "获取二维码失败，请查看后台日志"})
            
            # 同时生成网页支付链接（方便电脑端测试）
            # 使用 alipay.trade.page.pay 生成网页支付链接
            try:
                # 生成网页支付URL
                page_pay_url = alipay.api_alipay_trade_page_pay(
                    subject="GoodShop-积分充值",
                    out_trade_no=out_trade_no,
                    total_amount=str(amount),
                    return_url=settings.ALIPAY.get("return_url", "http://127.0.0.1:8000/user/center/")
                )
                # 拼接完整URL
                if settings.ALIPAY["debug"]:
                    web_url = "https://openapi.alipaydev.com/gateway.do?" + page_pay_url
                else:
                    web_url = "https://openapi.alipay.com/gateway.do?" + page_pay_url
                
                print(f"网页支付链接: {web_url}")
                return JsonResponse({"code": 0, "qr": qr, "web_url": web_url, "oid": order.id})
            except:
                # 如果网页支付生成失败，只返回二维码
                return JsonResponse({"code": 0, "qr": qr, "oid": order.id})
        else:
            return JsonResponse({"code": 500, "msg": f"支付宝返回格式错误: {type(result)}"})
            
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"支付宝接口调用异常:\n{error_detail}")
        return JsonResponse({"code": 500, "msg": f"支付宝接口调用失败: {str(e)}"})


def query_order(request, oid):
    """前端轮询支付结果"""
    try:
        order = models.RechargeOrder.objects.get(id=oid)
        return JsonResponse({"status": order.status})
    except models.RechargeOrder.DoesNotExist:
        return JsonResponse({"status": -1, "msg": "订单不存在"})


@csrf_exempt
@transaction.atomic
def alipay_notify(request):
    """支付宝异步 POST 通知"""
    if request.method != "POST":
        return HttpResponse("fail")
    
    alipay = get_alipay()
    if not alipay:
        return HttpResponse("fail")
    
    data = {k: request.POST[k] for k in request.POST.keys()}
    sign = data.pop("sign", None)
    
    # 验证签名
    if not alipay.verify(data, sign):
        return HttpResponse("fail")
    
    out_trade_no = data.get("out_trade_no")
    trade_status = data.get("trade_status")
    
    if trade_status == "TRADE_SUCCESS":
        try:
            order = models.RechargeOrder.objects.select_for_update().get(out_trade_no=out_trade_no)
            if order.status == 0:
                order.status = 1
                order.pay_time = datetime.datetime.now()
                order.save()
                # 到账积分
                user = order.user
                user.score += order.score
                user.save()
        except models.RechargeOrder.DoesNotExist:
            return HttpResponse("fail")
    
    return HttpResponse("success")


@csrf_exempt
@transaction.atomic
def simulate_pay(request):
    """模拟支付成功（仅用于测试）"""
    if request.method != "POST":
        return JsonResponse({"code": 400, "msg": "请求方法错误"})
    
    oid = request.POST.get("oid")
    if not oid:
        return JsonResponse({"code": 400, "msg": "缺少订单ID"})
    
    try:
        order = models.RechargeOrder.objects.select_for_update().get(id=oid)
        if order.status == 0:
            order.status = 1
            order.pay_time = datetime.datetime.now()
            order.save()
            
            # 到账积分
            user = order.user
            user.score += order.score
            user.save()
            
            print(f"[测试] 模拟支付成功 - 订单:{order.id}, 用户:{user.uname}, 积分+{order.score}")
            return JsonResponse({"code": 0, "msg": "支付成功"})
        else:
            return JsonResponse({"code": 400, "msg": "订单已处理"})
    except models.RechargeOrder.DoesNotExist:
        return JsonResponse({"code": 404, "msg": "订单不存在"})
    except Exception as e:
        print(f"[测试] 模拟支付失败: {e}")
        return JsonResponse({"code": 500, "msg": str(e)})


@csrf_exempt
@transaction.atomic
def test_pay(request):
    """测试支付（直接创建订单并到账，跳过支付宝）"""
    if request.method != "POST":
        return JsonResponse({"code": 400, "msg": "请求方法错误"})
    
    user_info = request.session.get("info")
    if not user_info:
        return JsonResponse({"code": 401, "msg": "请先登录"})
    
    try:
        # 创建订单
        out_trade_no = "TEST" + str(uuid.uuid4()).replace("-", "")
        order = models.RechargeOrder.objects.create(
            user_id=user_info["userid"],
            out_trade_no=out_trade_no,
            amount=0.1,
            score=10,
            status=1,  # 直接标记为已支付
            pay_time=datetime.datetime.now()
        )
        
        # 直接到账积分
        user = order.user
        user.score += order.score
        user.save()
        
        print(f"[测试] 测试支付成功 - 订单:{order.id}, 用户:{user.uname}, 积分+{order.score}")
        return JsonResponse({"code": 0, "msg": "测试支付成功"})
    except Exception as e:
        print(f"[测试] 测试支付失败: {e}")
        return JsonResponse({"code": 500, "msg": str(e)})
