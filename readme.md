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

- **用户登出**
  - 清除 Session 信息
  - 重定向到登录页

### 2. 数据模型

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

### 3. 辅助功能
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
4. **安全性考虑**: 密码加密、验证码、Session 管理等安全措施
5. **可扩展性强**: 采用 Django 应用模块化设计，便于添加新功能

## 开发环境配置

1. 安装 Python 3.x
2. 安装 MySQL 数据库
3. 安装项目依赖（需要创建 requirements.txt）
4. 配置数据库连接
5. 执行数据库迁移
6. 运行开发服务器


根据项目文件结构和样式文件判断，以下功能可能正在开发或计划开发：
- 支付功能 (way01.jpg, way02.jpg, way03.jpg)
