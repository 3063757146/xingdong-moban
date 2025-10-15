# AI生图平台 - 完整支付功能实现

## 🎯 项目简介

AI生图平台是一个基于Django的现代化Web应用，集成了支付宝支付功能，支持用户积分充值和AI图像生成服务。

### ✨ 核心功能
- 👤 **用户系统**：注册、登录、用户中心
- 💰 **支付系统**：支付宝扫码支付、网页支付
- 🎨 **AI生图**：基于积分的图像生成服务
- 📱 **响应式设计**：支持PC和移动端

---

## 🏗️ 技术栈

### 后端技术
- **Django 4.x** - Web框架
- **Python 3.x** - 编程语言
- **SQLite/MySQL** - 数据库
- **python-alipay-sdk** - 支付宝SDK

### 前端技术
- **HTML5/CSS3** - 页面结构
- **JavaScript/jQuery** - 交互逻辑
- **Bootstrap** - UI框架
- **qrcodejs** - 二维码生成

### 支付集成
- **支付宝当面付** - 扫码支付
- **支付宝网页支付** - 电脑端支付
- **沙箱环境** - 开发测试
- **生产环境** - 正式部署

---

## 📁 项目结构

```
GoodShop/
├── GoodShop/                 # 项目配置
│   ├── settings.py          # 项目设置
│   ├── urls.py             # 主路由
│   └── wsgi.py             # WSGI配置
├── userapp/                 # 用户应用
│   ├── models.py           # 数据模型
│   ├── views.py            # 视图函数
│   ├── urls.py             # 应用路由
│   ├── utils/              # 工具类
│   │   └── alipay_utils.py # 支付宝工具
│   └── templates/          # 模板文件
│       ├── login.html      # 登录页面
│       ├── register.html   # 注册页面
│       ├── center.html     # 用户中心
│       └── recharge.html   # 充值页面
├── templates/              # 全局模板
│   └── layout.html         # 基础布局
├── static/                 # 静态文件
│   ├── css/               # 样式文件
│   ├── js/                # JavaScript文件
│   └── images/            # 图片资源
├── keys/                   # 密钥文件
│   ├── my_private_key.txt # 应用私钥
│   └── alipay_public_key.txt # 支付宝公钥
└── media/                  # 媒体文件
```

---

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd GoodShop

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置设置

#### 支付宝配置
在 `GoodShop/settings.py` 中配置支付宝参数：

```python
# 沙箱环境配置
SANDBOX_ALIPAY = {
    "appid": "9021000149644414",  # 你的沙箱APPID
    "gateway": "https://openapi.alipaydev.com/gateway.do",
    "notify_url": "http://127.0.0.1:8000/user/alipay_notify/",
    "return_url": "http://127.0.0.1:8000/user/center/",
    "private_key_path": os.path.join(BASE_DIR, "keys/my_private_key.txt"),
    "public_key_path": os.path.join(BASE_DIR, "keys/alipay_public_key.txt"),
    "debug": True,
}
```

#### 密钥文件
1. 生成RSA密钥对
2. 上传公钥到支付宝开放平台
3. 下载支付宝公钥
4. 将密钥文件放在 `keys/` 目录下

### 3. 数据库迁移

```bash
# 生成迁移文件
python manage.py makemigrations

# 执行迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser
```

### 4. 启动服务

```bash
# 启动开发服务器
python manage.py runserver

# 访问应用
http://127.0.0.1:8000
```

---

## 💰 支付功能详解

### 支付流程

1. **用户充值**：在用户中心点击"充值"按钮
2. **生成订单**：系统创建充值订单记录
3. **调用支付宝**：生成支付二维码和网页支付链接
4. **用户支付**：扫码或网页支付
5. **异步通知**：支付宝回调更新订单状态
6. **积分到账**：自动增加用户积分

### 支付方式

#### 扫码支付
- 生成二维码供手机支付宝APP扫码
- 支持当面付功能
- 实时轮询支付状态

#### 网页支付
- 跳转到支付宝网页支付页面
- 适合电脑端用户
- 支付完成后自动跳转回平台

### 订单状态

| 状态码 | 状态名称 | 描述 |
|--------|----------|------|
| 0 | 待支付 | 订单已创建，等待支付 |
| 1 | 已支付 | 支付成功，积分已到账 |
| 2 | 已关闭 | 订单已取消或超时 |

---

## 🎨 界面设计

### 登录注册页面
- 现代化渐变背景
- 毛玻璃卡片效果
- 响应式设计
- 密码强度检测

### 用户中心
- 个人信息展示
- 积分余额显示
- 充值功能入口
- 菜单导航

### 充值页面
- 美观的支付界面
- 二维码展示
- 支付状态提示
- 成功动画效果

---

## 🔧 开发指南

### 环境切换

```bash
# 切换到生产环境
export ALIPAY_ENV=prod

# 切换到沙箱环境
export ALIPAY_ENV=sandbox
```

### 测试支付

```bash
# 使用模拟支付（跳过支付宝）
POST /user/simulate_pay/
{
    "oid": "订单ID"
}

# 使用测试支付（直接到账）
POST /user/test_pay/
```

### 调试工具

```python
# 查看当前支付宝配置
python -c "
from django.conf import settings
print('环境:', settings.ALIPAY_ENV)
print('AppID:', settings.ALIPAY['appid'])
print('网关:', settings.ALIPAY['gateway'])
"
```

---

## 📱 API接口

### 用户相关
- `POST /user/register/` - 用户注册
- `POST /user/login/` - 用户登录
- `GET /user/center/` - 用户中心
- `GET /user/logout/` - 用户登出

### 支付相关
- `GET /user/recharge/` - 充值页面
- `GET /user/alipay_qrcode/` - 获取支付二维码
- `GET /user/query_order/<oid>/` - 查询订单状态
- `POST /user/alipay_notify/` - 支付宝异步通知

### 测试接口
- `POST /user/simulate_pay/` - 模拟支付
- `POST /user/test_pay/` - 测试支付

---

## 🚀 部署指南

### 生产环境配置

1. **修改settings.py**
```python
# 生产环境配置
PROD_ALIPAY = {
    "appid": "你的正式APPID",
    "gateway": "https://openapi.alipay.com/gateway.do",
    "notify_url": "https://yourdomain.com/user/alipay_notify/",
    "return_url": "https://yourdomain.com/user/center/",
    "private_key_path": os.path.join(BASE_DIR, "keys/prod_app_private_key.pem"),
    "public_key_path": os.path.join(BASE_DIR, "keys/prod_alipay_public_key.pem"),
    "debug": False,
}
```

2. **设置环境变量**
```bash
export ALIPAY_ENV=prod
```

3. **配置HTTPS**
- 确保域名支持HTTPS
- 配置SSL证书
- 更新支付宝回调地址

### 服务器部署

```bash
# 安装依赖
pip install gunicorn

# 启动服务
gunicorn GoodShop.wsgi:application --bind 0.0.0.0:8000

# 使用Nginx反向代理
# 配置静态文件服务
# 配置HTTPS证书
```

---

## 🛠️ 故障排除

### 常见问题

1. **密钥文件错误**
   - 检查密钥文件路径
   - 确认密钥格式正确
   - 验证公钥已上传到支付宝

2. **支付回调失败**
   - 检查notify_url是否可访问
   - 确认HTTPS配置正确
   - 查看服务器日志

3. **二维码显示异常**
   - 检查qrcodejs库是否加载
   - 确认CDN连接正常
   - 验证二维码数据格式

### 调试技巧

```python
# 开启详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 查看支付宝返回结果
print(f"支付宝返回: {result}")

# 验证签名
from .utils.alipay_utils import verify_notify
success = verify_notify(data, sign)
print(f"签名验证: {success}")
```

---

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

## 🤝 贡献指南

1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📞 技术支持

如有问题或建议，请通过以下方式联系：

- 📧 邮箱：support@example.com
- 🐛 问题反馈：[GitHub Issues](https://github.com/your-repo/issues)
- 📖 文档：[项目Wiki](https://github.com/your-repo/wiki)

---

**🎉 感谢使用AI生图平台！**
