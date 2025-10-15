# GoodShop 电商系统

## 项目简介
GoodShop 是一个基于 Django 的电商系统，提供用户管理、支付等功能。

## 技术栈

### 后端技术
- **框架**: Django 4.2.16
- **数据库**: MySQL
- **Python 版本**: Python 3.x
- **依赖库**:
  - jsonpickle (对象序列化)
  - xarray (数据处理)
  - Pillow (图片处理/验证码生成)

### 前端技术
- **UI 框架**: 
  - Amaze UI (响应式前端框架)
  - Bootstrap 3.4.1
- **JavaScript 库**:
  - jQuery 3.6.0
  - ECharts (数据可视化)
  - md5-min.js (密码加密)
- **CSS 框架**: 
  - Font Awesome 4.7.0 (图标库)
  - Bootstrap Datepicker (日期选择器)

## 项目结构

```
GoodShop/
├── GoodShop/                  # Django 项目配置目录
│   ├── settings.py           # 项目配置文件
│   ├── urls.py               # 主路由配置
│   ├── wsgi.py               # WSGI 部署配置
│   └── asgi.py               # ASGI 异步部署配置
├── userapp/                   # 用户应用模块
│   ├── models.py             # 数据模型（UserInfo, Area）
│   ├── views.py              # 视图逻辑（注册、登录、用户中心）
│   ├── urls.py               # 用户模块路由
│   ├── templates/            # 用户模块模板
│   │   ├── login.html        # 登录页面
│   │   ├── register.html     # 注册页面
│   │   └── center.html       # 用户中心
│   └── migrations/           # 数据库迁移文件
├── templates/                 # 全局模板目录
│   ├── layout.html           # 主布局模板
│   └── layout2.html          # 次级布局模板
├── static/                    # 静态资源目录
│   ├── css/                  # 样式文件
│   │   ├── assets/           # Amaze UI 资源
│   │   ├── index.css         # 首页样式
│   │   ├── login.css         # 登录样式
│   │   ├── detail.css        # 详情页样式
│   │   ├── carts.css         # 购物车样式
│   │   └── ...
│   ├── js/                   # JavaScript 文件
│   │   ├── jquery-3.6.0.min.js
│   │   ├── echarts.min.js
│   │   ├── md5-min.js
│   │   ├── carts.js          # 购物车逻辑
│   │   ├── user.js           # 用户相关逻辑
│   │   └── ...
│   ├── images/               # 图片资源
│   └── plugins/              # 第三方插件
│       ├── bootstrap-3.4.1/
│       ├── bootstrap-datepicker/
│       └── font-awesome-4.7.0/
├── media/                     # 用户上传文件目录
│   └── [商品图片等媒体文件]
├── utils/                     # 工具类目录
│   ├── encrypt.py            # MD5 加密工具
│   ├── code.py               # 验证码生成工具
│   ├── forms.py              # 表单基类（BootstrapForm）
│   ├── ReadToSql.py          # 数据导入工具
│   └── jiukuaijiu.json       # 地区数据
├── manage.py                  # Django 管理脚本
└── readme.md                  # 项目说明文档
```

## 核心功能模块

### 1. 用户管理模块 (userapp)
- **用户注册**
  - 用户名唯一性验证
  - 密码强度验证（最小6位）
  - 邮箱格式验证和唯一性验证
  - 两次密码一致性验证
  - 密码 MD5 加密存储
  
- **用户登录**
  - 用户名密码验证
  - 图形验证码验证（60秒有效期）
  - Session 管理（7天免登录）
  - 自动跳转用户中心

- **用户中心**
  - 用户信息展示
  - 用户积分系统（默认100积分）
  - Session 验证保护
  - 积分充值功能

- **用户登出**
  - 清除 Session 信息
  - 重定向到登录页

### 2. 支付功能模块（支付宝当面付）
- **积分充值**
  - 1元充值10积分
  - 二维码扫码支付
  - 实时轮询支付状态
  - 支付成功自动到账
  - 订单记录管理
  
- **支付流程**
  - 用户点击充值按钮
  - 弹窗展示支付二维码
  - 支付宝扫码支付
  - 前端轮询订单状态
  - 支付成功后积分实时到账
  - 页面自动刷新显示新积分
  
- **安全保障**
  - RSA2 签名验证
  - 订单唯一性校验
  - 事务处理防重复到账
  - CSRF 豁免（仅异步通知接口）

### 3. 数据模型

#### UserInfo (用户信息表)
- `id`: 主键（自增）
- `uname`: 用户名（最大100字符）
- `pwd`: 密码（MD5加密，最大100字符）
- `score`: 用户积分（默认100）
- `email`: 邮箱（最大25字符，默认"default@163.com"）

#### Area (地区表)
- `areaid`: 地区ID（主键）
- `areaname`: 地区名称（最大50字符）
- `parentid`: 父级地区ID
- `arealevel`: 地区层级
- `status`: 状态

#### RechargeOrder (充值订单表)
- `id`: 主键（自增）
- `user`: 用户外键（关联 UserInfo）
- `out_trade_no`: 商户订单号（唯一，UUID格式）
- `amount`: 充值金额（最大10位，2位小数）
- `score`: 赠送积分（整数）
- `status`: 订单状态（0-待支付，1-已支付，2-已关闭）
- `create_time`: 创建时间（自动记录）
- `pay_time`: 支付时间（可为空）

### 4. 辅助功能
- **表单验证**: 基于 Django Forms 的自定义验证
- **图形验证码**: 动态生成验证码图片
- **密码加密**: MD5 加密算法
- **Session 管理**: 用户状态持久化（7天免登录）
- **媒体文件管理**: 支持图片上传和访问
- **静态资源管理**: CSS、JS、图片等静态文件服务

## 数据库配置

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'xingdong',
        'USER': 'root',
        'PASSWORD': 'liu021003',
        'HOST': '127.0.0.1',
        'PORT': 3306,
    }
}
```

## URL 路由

### 用户模块路由
- `/user/register/` - 用户注册
- `/user/login/` - 用户登录
- `/user/center/` - 用户中心
- `/user/logout/` - 用户登出
- `/user/code/` - 验证码图片

### 支付模块路由
- `/user/recharge/` - 充值页面（弹窗模板）
- `/user/alipay_qrcode/` - 获取支付二维码接口（返回JSON）
- `/user/query_order/<oid>/` - 轮询订单状态接口
- `/user/alipay_notify/` - 支付宝异步通知回调

### 管理后台
- `/admin/` - Django Admin 管理后台

## 安全特性

1. **密码安全**: 所有密码使用 MD5 加密存储
2. **CSRF 保护**: Django 内置 CSRF 中间件
3. **Session 安全**: 设置过期时间，防止会话劫持
4. **表单验证**: 前后端双重验证机制
5. **验证码机制**: 防止恶意登录尝试

## 前端界面特性

- **响应式设计**: 支持多种设备屏幕
- **现代化 UI**: 使用 Amaze UI 和 Bootstrap
- **图表可视化**: 集成 ECharts 数据展示
- **图标库**: Font Awesome 图标支持
- **日期选择器**: Bootstrap Datepicker 插件

## 功能截图

详见项目根目录下的图片文件：
- `img.png` - 功能概览
- `1.png` - 数据库模型图1
- `2.png` - 数据库模型图2

## 项目特点

1. **清晰的项目结构**: 模块化设计，易于维护和扩展
2. **完善的用户系统**: 注册、登录、认证、积分等功能完备
3. **现代化前端**: 响应式设计，良好的用户体验
4. **安全性考虑**: 密码加密、验证码、Session 管理、支付签名验证等安全措施
5. **可扩展性强**: 采用 Django 应用模块化设计，便于添加新功能
6. **完整的支付闭环**: 支付宝当面付集成，从下单到到账全流程自动化

## 开发环境配置

### 基础环境
1. 安装 Python 3.x
2. 安装 MySQL 数据库
3. 安装项目依赖：
   ```bash
   pip install django==4.2.16
   pip install pymysql
   pip install pillow
   pip install jsonpickle
   pip install python-alipay-sdk
   ```

### 数据库配置
1. 创建数据库：
   ```sql
   CREATE DATABASE xingdong CHARACTER SET utf8mb4;
   ```
2. 修改 `GoodShop/settings.py` 中的数据库配置
3. 执行迁移：
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

### 支付宝配置

#### 沙箱环境（开发测试）
1. 访问 [支付宝开放平台沙箱](https://open.alipay.com/develop/sandbox/app)
2. 获取沙箱 AppID 和密钥（详见 `keys/README.md`）
3. 将应用私钥和支付宝公钥放到 `keys/` 目录
4. 本地开发需配置内网穿透（ngrok）以接收异步通知

#### 正式环境（生产部署）
1. 准备正式应用密钥（详见 `PRODUCTION_DEPLOYMENT.md`）
2. 修改 `settings.py` 中的正式域名（HTTPS）
3. 在支付宝后台签约「当面付」产品
4. 设置环境变量启动：
   ```bash
   ALIPAY_ENV=prod python manage.py runserver
   ```

#### 环境切换
- **默认运行沙箱**：不设置环境变量
- **切换到正式**：`ALIPAY_ENV=prod`
- **回滚到沙箱**：`unset ALIPAY_ENV` 或 `ALIPAY_ENV=sandbox`

### 运行项目
```bash
python manage.py runserver
```

访问 http://127.0.0.1:8000/user/login/ 即可开始使用


根据项目文件结构和样式文件判断，以下功能可能正在开发或计划开发：
- 商品列表和详情展示 (proList.css, detail.css)
- 购物车功能 (carts.css, carts.js)
- 收货地址管理 (peraddressbg.png)
- 个人信息管理 (personal.css)
- 订单管理系统
- 商品分类和搜索

## 支付功能使用说明

### 充值流程
1. 登录系统进入用户中心
2. 点击积分旁的「充值」按钮
3. 弹窗显示充值金额和二维码
4. 使用支付宝扫码支付（沙箱环境使用沙箱买家账号）
5. 支付成功后页面自动刷新，积分实时到账

### 测试说明
- **沙箱环境**: 默认使用支付宝沙箱环境进行测试
- **测试金额**: 固定为 1 元充值 10 积分
- **测试账号**: 使用支付宝沙箱提供的买家账号
- **注意事项**: 异步通知需要外网可访问地址，本地开发需使用内网穿透工具

### 正式环境部署
1. 申请正式支付宝应用并签约「当面付」产品
2. 更换正式环境的 AppID 和密钥
3. 修改 `settings.py` 中 `ALIPAY["debug"]` 为 `False`
4. 配置正式域名的 `notify_url` 和 `return_url`
5. 根据业务需求调整充值金额和积分比例
