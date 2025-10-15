# 支付宝密钥配置说明

## 密钥文件说明

此目录用于存放支付宝支付所需的密钥文件。请按以下步骤配置：

## 配置步骤

### 1. 获取支付宝沙箱密钥

1. 访问 [支付宝开放平台](https://open.alipay.com/)
2. 登录后进入「开发者中心」→「研发服务」→「沙箱环境」
3. 在沙箱应用中找到「接口加签方式（密钥/证书）」

### 2. 生成应用密钥

#### 方式一：使用支付宝密钥生成工具（推荐）

1. 下载 [支付宝密钥生成工具](https://opendocs.alipay.com/common/02kipk)
2. 选择「PKCS1（非JAVA适用）」格式
3. 选择「RSA2（SHA256）」密钥长度为 2048
4. 点击「生成密钥」

#### 方式二：使用 OpenSSL 命令行

```bash
# 生成私钥
openssl genrsa -out app_private_key.pem 2048

# 从私钥中提取公钥
openssl rsa -in app_private_key.pem -pubout -out app_public_key.pem
```

### 3. 上传应用公钥到支付宝

1. 将生成的「应用公钥」内容复制（app_public_key.pem 的内容，去掉头尾标识）
2. 在支付宝沙箱页面点击「设置应用公钥」
3. 选择「公钥」模式，粘贴公钥内容并保存
4. 保存后，支付宝会生成「支付宝公钥」，点击查看并复制

### 4. 在本目录创建两个密钥文件

#### app_private_key.pem（应用私钥）

```
-----BEGIN RSA PRIVATE KEY-----
[你的应用私钥内容]
-----END RSA PRIVATE KEY-----
```

#### alipay_public_key.pem（支付宝公钥）

```
-----BEGIN PUBLIC KEY-----
[支付宝返回的公钥内容]
-----END PUBLIC KEY-----
```

### 5. 注意事项

- **私钥必须保密**，不要泄露或上传到代码仓库
- 已在 `.gitignore` 中添加 `keys/*.pem` 规则，防止误提交
- 正式环境需要重新申请正式应用的密钥，并修改 `settings.py` 中的配置

## 文件结构

```
keys/
├── README.md                    # 本说明文件
├── app_private_key.pem         # 应用私钥（需要创建）
└── alipay_public_key.pem       # 支付宝公钥（需要创建）
```

## 测试环境配置

### 沙箱环境信息

- AppID: 已在 `settings.py` 中配置（默认为示例 AppID）
- 网关地址: 沙箱环境会自动使用测试网关
- 支付宝账号: 使用沙箱提供的买家账号进行测试

### 沙箱买家账号

在支付宝沙箱页面可以查看测试买家账号信息，用于扫码支付测试。

## 异步通知配置

如果是本地开发环境，异步通知地址 `notify_url` 需要外网能访问：

### 使用 ngrok 内网穿透（推荐）

```bash
# 安装 ngrok
# 访问 https://ngrok.com/ 注册并下载

# 启动内网穿透
ngrok http 8000

# 将生成的外网地址配置到 settings.py 的 notify_url
# 例如: https://xxxx.ngrok.io/user/alipay_notify/
```

### 其他内网穿透工具

- 花生壳 (https://hsk.oray.com/)
- natapp (https://natapp.cn/)
- cpolar (https://www.cpolar.com/)

## 正式环境部署

正式环境需要：

1. 在支付宝开放平台创建正式应用
2. 提交应用审核并签约「当面付」产品
3. 重新生成正式环境密钥
4. 修改 `settings.py` 中的配置：
   - 更换正式 AppID
   - 更新 notify_url 为正式域名
   - 设置 `debug=False`

## 常见问题

### Q: 提示"支付功能未配置，请检查密钥文件"

A: 请确保 `app_private_key.pem` 和 `alipay_public_key.pem` 文件已正确创建，并包含完整的密钥内容。

### Q: 二维码生成失败

A: 检查密钥格式是否正确，确保私钥和公钥匹配，AppID 配置正确。

### Q: 支付成功但积分未到账

A: 检查异步通知地址是否可以外网访问，查看 Django 日志确认是否收到支付宝的通知。

### Q: 签名验证失败

A: 确保使用的是支付宝公钥（不是应用公钥），密钥格式包含完整的头尾标识。

