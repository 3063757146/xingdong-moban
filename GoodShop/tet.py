server {
    listen 80;
    listen 443 ssl http2;
    server_name top1.chat www.top1.chat;

    # SSL配置（保持原样）
    ssl_certificate     /www/server/panel/vhost/cert/top1.chat/fullchain.pem;
    ssl_certificate_key /www/server/panel/vhost/cert/top1.chat/privkey.pem;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # 强制HTTPS
    if ($server_port !~ 443) {
        rewrite ^(/.*)$ https://$host$1 permanent;
    }

    # 1. 静态文件直接托管（Django collectstatic 目录）
    location /static/ {
        alias /www/wwwroot/xingdong-moban/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
    location /media/ {
        alias /www/wwwroot/xingdong-moban/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # 2. 后端 API 保留（如不再需要可整段删除）
    # location /api/ {
    #     proxy_pass http://127.0.0.1:3001/api/;
    #     proxy_set_header Host $host;
    #     proxy_set_header X-Real-IP $remote_addr;
    #     proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    #     proxy_set_header X-Forwarded-Proto $scheme;
    # }

    # 3. 其余所有请求转给 Django（gunicorn 8000）
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout   60s;
        proxy_read_timeout   60s;
    }

    # 日志
    access_log /www/wwwlogs/top1.chat.log;
    error_log  /www/wwwlogs/top1.chat.error.log;
}