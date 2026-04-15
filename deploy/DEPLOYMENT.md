# 部署说明

本文档给出一套适合试运行和内部部署的 Linux 方案：`gunicorn + systemd + nginx + PostgreSQL/PostGIS`。

## 目录建议

```text
/opt/geo-optimizer
  app/
  deploy/
  .venv/
  .env
  gunicorn.conf.py
  run.py
```

## 1. 准备环境

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nginx postgresql postgis
```

## 2. 部署代码

```bash
sudo mkdir -p /opt/geo-optimizer
sudo chown -R $USER:$USER /opt/geo-optimizer
cp -R . /opt/geo-optimizer
cd /opt/geo-optimizer
bash scripts/bootstrap.sh
cp deploy/env/.env.production.example .env
```

然后编辑 `.env`，填入管理员密码、数据库和模型 API 配置。

## 3. 准备数据库

```bash
sudo -u postgres psql
CREATE DATABASE geo_optimizer;
\c geo_optimizer
CREATE EXTENSION IF NOT EXISTS postgis;
```

## 4. 启动应用

```bash
source .venv/bin/activate
gunicorn -c gunicorn.conf.py run:app
```

确认后可继续配置 `systemd`：

```bash
sudo cp deploy/systemd/geo-optimizer.service /etc/systemd/system/geo-optimizer.service
sudo systemctl daemon-reload
sudo systemctl enable geo-optimizer
sudo systemctl start geo-optimizer
sudo systemctl status geo-optimizer
```

## 5. 配置 Nginx

```bash
sudo cp deploy/nginx/geo-optimizer.conf /etc/nginx/sites-available/geo-optimizer
sudo ln -sf /etc/nginx/sites-available/geo-optimizer /etc/nginx/sites-enabled/geo-optimizer
sudo nginx -t
sudo systemctl reload nginx
```

## 6. 验证

```bash
curl http://127.0.0.1:5000/health
python3 scripts/smoke_check.py
```

## 7. 发布前建议

1. 修改默认管理员账号和密码。
2. 关闭 mock，填入真实 DeepSeek / 豆包配置。
3. 将 `.env` 和日志文件纳入服务器备份策略。
4. 生产环境建议加 HTTPS、WAF、日志轮转和监控告警。
