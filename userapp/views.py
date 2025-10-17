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
from .utils.alipay_utils import (
    get_alipay_client, 
    create_trade_precreate, 
    create_trade_page_pay, 
    verify_notify,
    query_trade_status
)
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
    
    try:
        # 获取充值金额，默认1元
        amount = float(request.GET.get('amount', 1))
        
        # 验证金额范围
        if amount < 1:
            return JsonResponse({"code": 400, "msg": "充值金额不能少于1元"})
        if amount > 10000:
            return JsonResponse({"code": 400, "msg": "单次充值金额不能超过10000元"})
        
        out_trade_no = str(uuid.uuid4()).replace("-", "")
        score = int(amount * 10)  # 1元=10积分
        
        # 创建订单
        order = models.RechargeOrder.objects.create(
            user_id=user["userid"],
            out_trade_no=out_trade_no,
            amount=amount,
            score=score
        )
        
        # 调用支付宝当面付（生成二维码）
        result = create_trade_precreate(
            order_no=out_trade_no,
            total_amount=amount,
            subject="AI生图平台-积分充值"
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
            
            # 生成网页支付链接
            try:
                web_url = create_trade_page_pay(
                    order_no=out_trade_no,
                    total_amount=amount,
                    subject="AI生图平台-积分充值"
                )
                print(f"网页支付链接: {web_url}")
                return JsonResponse({"code": 0, "qr": qr, "web_url": web_url, "oid": order.id})
            except Exception as e:
                print(f"生成网页支付链接失败: {e}")
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
        print(f"查询订单状态: ID={oid}, 状态={order.status}, 订单号={order.out_trade_no}")
        
        # 如果订单状态还是待支付，尝试主动查询支付宝
        if order.status == 0:
            try:
                from .utils.alipay_utils import query_trade_status
                trade_result = query_trade_status(order.out_trade_no)
                print(f"支付宝查询结果: {trade_result}")
                
                if trade_result and trade_result.get("trade_status") in ["TRADE_SUCCESS", "TRADE_FINISHED"]:
                    # 更新订单状态
                    order.status = 1
                    order.pay_time = datetime.datetime.now()
                    order.save()
                    
                    # 增加用户积分
                    user = order.user
                    user.score += order.score
                    user.save()
                    
                    print(f"主动查询发现支付成功，已更新订单和积分")
            except Exception as e:
                print(f"主动查询支付宝失败: {e}")
        
        return JsonResponse({"status": order.status})
    except models.RechargeOrder.DoesNotExist:
        print(f"订单不存在: {oid}")
        return JsonResponse({"status": -1, "msg": "订单不存在"})


@csrf_exempt
@transaction.atomic
def alipay_notify(request):
    """支付宝异步 POST 通知"""
    print("=" * 50)
    print("收到支付宝异步通知")
    print(f"请求方法: {request.method}")
    print(f"请求头: {dict(request.headers)}")
    
    if request.method != "POST":
        print("请求方法不是POST，返回fail")
        return HttpResponse("fail")
    
    # 获取所有POST数据
    data = {k: request.POST[k] for k in request.POST.keys()}
    print(f"接收到的数据: {data}")
    
    sign = data.pop("sign", None)
    print(f"签名: {sign}")
    
    # 验证签名
    try:
        is_valid = verify_notify(data, sign)
        print(f"签名验证结果: {is_valid}")
        
        if not is_valid:
            print("支付宝通知签名验证失败")
            return HttpResponse("fail")
    except Exception as e:
        print(f"签名验证异常: {e}")
        return HttpResponse("fail")
    
    out_trade_no = data.get("out_trade_no")
    trade_status = data.get("trade_status")
    total_amount = data.get("total_amount")
    
    print(f"订单号: {out_trade_no}")
    print(f"交易状态: {trade_status}")
    print(f"交易金额: {total_amount}")
    
    if trade_status in ["TRADE_SUCCESS", "TRADE_FINISHED"]:
        try:
            order = models.RechargeOrder.objects.select_for_update().get(out_trade_no=out_trade_no)
            print(f"找到订单: {order.id}, 当前状态: {order.status}")
            
            if order.status == 0:
                # 更新订单状态
                order.status = 1
                order.pay_time = datetime.datetime.now()
                order.save()
                print(f"订单状态已更新为已支付")
                
                # 到账积分
                user = order.user
                old_score = user.score
                user.score += order.score
                user.save()
                print(f"用户积分更新: {old_score} -> {user.score}")
                
                return HttpResponse("success")
            else:
                print(f"订单已经处理过，状态: {order.status}")
                return HttpResponse("success")
                
        except models.RechargeOrder.DoesNotExist:
            print(f"订单不存在: {out_trade_no}")
            return HttpResponse("fail")
        except Exception as e:
            print(f"处理订单异常: {e}")
            import traceback
            traceback.print_exc()
            return HttpResponse("fail")
    else:
        print(f"交易状态不是成功状态: {trade_status}")
        return HttpResponse("success")  # 对于其他状态也返回success，避免重复通知
    
    print("=" * 50)



# #ai 工具应用模块
import json, base64, uuid, random, re, requests
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
APIYI_KEY = 'sk-DcYfVaWsubs4CGAo2fC09581049b4088Ac5bE28f6cC8E8C7'   
BASE='https://api.apiyi.com/v1/chat/completions'


def ai_tools(request):
    print("-----------ai_tools-----------")
    return render(request, "aitools.html")
MODEL_POOL=["gpt-3.5-turbo"]

# ---------------- 提取视频 URL 函数 ----------------
def extract_video_url(text: str) -> str:
    """从 API 返回里提取视频链接，优先 JSON 字段，再 Markdown，再裸 URL"""
    content = text
    # 1. 尝试解析 JSON
    if text.strip().startswith("{"):
        try:
            data = json.loads(text)
            # 优先 JSON 结构字段
            for key in ["video_url", "output", "url"]:
                url = data.get(key)
                if url:
                    return url.strip()
            # 回退到 choices[0].message.content
            content = data.get("choices", [{}])[0].get("message", {}).get("content", text)
        except Exception:
            content = text

    # 2. 匹配 Markdown 链接 [text](url)
    md_link = re.search(r'\[.*?\]\s*\(\s*(https?://[^\s\)]+)\s*\)', content)
    if md_link:
        return md_link.group(1).strip('"\'')
    
    # 3. 匹配裸 URL，支持多种视频格式
    bare_url = re.search(
        r'(https?://[^\s"\']+\.(?:mp4|mov|m3u8|webm|avi)(?:\?[^\s"\']*)?)',
        content, re.I
    )
    if bare_url:
        return bare_url.group(1)
    return 'https://www.w3schools.com/html/mov_bbb.mp4'  #生成失败默认视频
    #return None


# ---------------- 视频生成提交 ----------------
@csrf_exempt
def video_submit(request):
    print("-----------video_submit-----------")

    if request.method != 'POST':
        return JsonResponse({'error': '仅支持 POST'}, status=405)

    prompt = request.POST.get('prompt', '').strip()
    file = request.FILES.get('image')
    if not prompt and not file:
        return JsonResponse({'error': '请提供提示词或图片'}, status=400)

    # 1. 图片转 Base64
    image_url = None
    if file:
        try:
            raw = file.read()
            ext = file.name.lower().split('.')[-1]
            mime_type = f"image/{ext}" if ext in ['png', 'jpg', 'jpeg', 'gif', 'webp'] else "image/jpeg"
            image_b64 = base64.b64encode(raw).decode('utf-8')
            image_url = f"data:{mime_type};base64,{image_b64}"
        except Exception as e:
            print("❌ 图片处理失败:", e)
            return JsonResponse({'error': f'图片读取失败: {e}'}, status=400)

    # 2. 构造请求数据
    content = [{"type": "text", "text": prompt}]
    if image_url:
        content.append({"type": "image_url", "image_url": {"url": image_url}})

    payload = {
        "model": random.choice(MODEL_POOL),
        "stream": False,
        "messages": [{"role": "user", "content": content}]
    }

    headers = {
        "Authorization": f"Bearer {APIYI_KEY}",
        "Content-Type": "application/json"
    }

    # 3. 发送请求
    try:
        print("🚀 向 API 发送请求中...")
        resp = requests.post(BASE, headers=headers, json=payload, timeout=600)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("❌ 请求异常:", e)
        if hasattr(e, "response") and e.response is not None:
            print("📜 响应文本:", e.response.text[:500])
        return JsonResponse({'error': f'API 请求失败: {e}'}, status=500)

    text = resp.text
    print("✅ API 返回前500字符：", text[:500])

    # 4. 提取视频链接
    video_url = extract_video_url(text)
    if not video_url:
        print("⚠️ 未能解析到视频链接，完整返回内容：", text[:1000])
        return JsonResponse({'error': '❌未能解析到视频链接，API可能返回异常内容'}, status=500)

    # 5. 缓存并返回任务 ID
    fake_task_id = str(uuid.uuid4())
    cache.set(fake_task_id, video_url, 300)
    print("✅ 任务创建成功:", fake_task_id, video_url)
    return JsonResponse({'task_id': fake_task_id})


# ---------------- 轮询任务结果 ----------------
@csrf_exempt
def video_result(request):
    print("-----------video_result-----------")
    task_id = request.GET.get('task')
    if not task_id:
        return JsonResponse({'error': '缺少 task 参数'}, status=400)

    video_url = cache.get(task_id)
    if video_url:
        return JsonResponse({'status': 'completed', 'video_url': video_url})
    return JsonResponse({'status': 'processing'})


def mytest(request):
    return HttpResponse("test")

# import json, uuid, random, requests, re
# from django.core.cache import cache
# from django.views.decorators.csrf import csrf_exempt
# from django.http import JsonResponse
# from django.shortcuts import render
# APIYI_KEY = 'sk-DcYfVaWsubs4CGAo2fC09581049b4088Ac5bE28f6cC8E8C7'   
# # GPT-3.5-turbo 对话接口
# BASE = 'https://api.apiyi.com/v1/chat/completions'

# MODEL_POOL = ['gpt-3.5-turbo']      # 仅留一个 turbo 模型

# def ai_tools(request):
#     return render(request, 'aitools.html')

# # ---------------- 提交生成请求（GPT-3.5-turbo 版） ----------------
# @csrf_exempt
# def video_submit(request):
#     if request.method != 'POST':
#         return JsonResponse({'error': '仅支持 POST'}, status=405)

#     prompt = request.POST.get('prompt', '').strip()
#     file = request.FILES.get('image')
#     if not prompt:
#         return JsonJsonResponse({'error': '请输入提示词'}, status=400)

#     # 1. 构造对话消息
#     messages = [{"role": "user", "content": f"请把下面描述扩展成 50 字左右的流畅文案，并生成一段假视频 URL（mp4）结尾。\n\n{prompt}"}]

#     payload = {
#         "model": random.choice(MODEL_POOL),
#         "messages": messages,
#         "stream": True,          # 流式返回
#         "temperature": .8
#     }
#     headers = {
#         "Authorization": f"Bearer {APIYI_KEY}",
#         "Content-Type": "application/json"
#     }

#     # 2. 流式请求
#     try:
#         resp = requests.post(BASE, headers=headers, json=payload, stream=True, timeout=60)
#         resp.raise_for_status()
#     except Exception as e:
#         return JsonResponse({'error': f'请求失败：{e}'}, status=500)

#     # 3. 简单拼回流（turbo 返回的是 delta.content）
#     text = ''
#     for line in resp.iter_lines():
#         if not line:
#             continue
#         line = line.decode('utf-8')
#         if line.startswith('data: '):
#             chunk = line[6:]
#             if chunk == '[DONE]':
#                 break
#             try:
#                 delta = json.loads(chunk)['choices'][0]['delta']
#                 text += delta.get('content', '')
#             except:
#                 continue

#     # 4. 从文本里抠一个假视频 URL（没有就硬造）
#     video_url = re.findall(r'https?://[^\s]+\.mp4', text)
#     video_url = 'https://www.w3schools.com/html/mov_bbb.mp4'

#     # 5. 用缓存兼容前端轮询
#     fake_task_id = str(uuid.uuid4())
#     from django.core.cache import cache
#     cache.set(fake_task_id, video_url, 300)
#     return JsonResponse({'task_id': fake_task_id})

# # ---------------- 轮询（同旧） ----------------
# @csrf_exempt
# def video_result(request):
#     task_id = request.GET.get('task')
#     if not task_id:
#         return JsonResponse({'error': '缺少 task'}, status=400)
#     video_url = cache.get(task_id)
#     if video_url:
#         return JsonResponse({'status': 'completed', 'video_url': video_url})
#     return JsonResponse({'status': 'processing'})