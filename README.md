# GEO 大模型优化工具

这是一个面向 GEO 场景的大模型优化系统基础版，已经从单页原型扩展成一个可继续交付的后台项目，覆盖：

- 登录鉴权与后台保护
- 多用户与角色基础能力
- GEO 数据预处理与标签增强
- 豆包、DeepSeek、Gemini 等模型适配层
- 分析结果后处理、推荐摘要与地图视图
- 历史记录持久化
- 多页面后台界面
- JSON / Excel / PDF 导出
- 异步分析任务与状态轮询
- 持久化任务记录与失败重试
- 审计日志
- Docker / PostgreSQL / PostGIS 部署基础

## 当前页面

- `/` 仪表盘：提交分析请求、查看结果和最近记录
- `/history` 历史记录页：浏览分析历史，跳转详情，导出 JSON
- `/history/<id>` 详情页：查看标准化请求与结果详情
- `/settings` 配置页：检查供应商状态和运行时配置
- `/jobs` 任务监控页：查看异步任务状态和重试情况
- `/admin/users` 用户管理页：查看用户和角色
- `/admin/audit` 审计日志页：查看关键操作记录
- `/jobs/<job_id>` 任务详情页：查看任务 payload、错误和重跑入口

## 项目结构

```text
app/
  api.py
  config.py
  db.py
  service.py
  models/
    adapters.py
  persistence/
    models.py
    repository.py
  processing/
    preprocess.py
    postprocess.py
  static/
    app.css
    app.js
  templates/
    base.html
    dashboard.html
    history.html
    analysis_detail.html
    settings.html
run.py
requirements.txt
Dockerfile
gunicorn.conf.py
docker-compose.yml
deploy/
```

## 本地启动

### 一键初始化

```bash
bash scripts/bootstrap.sh
```

### 1. 安装依赖

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

### 2. 配置环境变量

你可以直接复制 `.env.example` 生成 `.env`：

```bash
cp .env.example .env
```

当前应用会在启动时自动读取 `.env`。

### 3. 启动服务

```bash
python run.py
```

### 4. 运行测试

```bash
python3 -m unittest tests/test_app.py
```

### 5. 运行冒烟检查

```bash
python3 scripts/smoke_check.py
```

### Makefile 快捷命令

```bash
make install
make init-env
make dev
make test
make smoke
```

默认登录账号：

- 用户名：`admin`
- 密码：`admin123`

建议你在 `.env` 里尽快修改：

```bash
GEO_ADMIN_USERNAME=your-admin
GEO_ADMIN_PASSWORD=strong-password
GEO_SECRET_KEY=change-me
```

默认地址：

- 工作台: `http://127.0.0.1:5000/`
- 历史页: `http://127.0.0.1:5000/history`
- 配置页: `http://127.0.0.1:5000/settings`

## 试用交付建议

如果你要把这个版本先交给同事试用，推荐按下面的顺序：

1. 执行 `bash scripts/bootstrap.sh`
2. 修改 `.env` 里的管理员账号和密钥
3. 用 `python run.py` 启动
4. 用默认 mock 模式先跑通完整流程
5. 再填入 DeepSeek / 豆包真实 API 做联调

## Docker 启动

### 使用 Docker Compose

```bash
docker compose up --build
```

默认会启动：

- `web`：Flask/Gunicorn 服务
- `db`：PostgreSQL 16 + PostGIS 3.4

停止容器：

```bash
docker compose down
```

## 生产部署

仓库里已经附带了一套基础生产部署模板：

- `[gunicorn.conf.py](/Users/laowang/Documents/New%20project/gunicorn.conf.py)`
- `[deploy/DEPLOYMENT.md](/Users/laowang/Documents/New%20project/deploy/DEPLOYMENT.md)`
- `[deploy/nginx/geo-optimizer.conf](/Users/laowang/Documents/New%20project/deploy/nginx/geo-optimizer.conf)`
- `[deploy/systemd/geo-optimizer.service](/Users/laowang/Documents/New%20project/deploy/systemd/geo-optimizer.service)`
- `[deploy/env/.env.production.example](/Users/laowang/Documents/New%20project/deploy/env/.env.production.example)`

如果你要在 Linux 服务器试运行，直接按 `deploy/DEPLOYMENT.md` 的步骤走即可。

## API

### 查看模型列表

```bash
curl http://127.0.0.1:5000/api/v1/geo/models
```

### 查看供应商状态

```bash
curl http://127.0.0.1:5000/api/v1/geo/providers
```

### 发起 GEO 分析

```bash
curl -X POST http://127.0.0.1:5000/api/v1/geo/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "query": "根据上海浦东新区用户画像推荐周边亲子活动",
    "model": "deepseek",
    "geo_context": {
      "location_name": "上海市浦东新区",
      "coordinates": {
        "lat": 31.2304,
        "lng": 121.4737
      },
      "coordinate_system": "WGS84"
    },
    "user_profile": {
      "preferred_categories": ["亲子", "户外", "周末活动"]
    },
    "context_signals": {
      "weather": "晴",
      "time_of_day": "afternoon",
      "event": "周末"
    }
  }'
```

### 异步发起 GEO 分析

```bash
curl -X POST http://127.0.0.1:5000/api/v1/geo/analyze/async \
  -H "Content-Type: application/json" \
  -d '{
    "query": "推荐深圳南山适合夜跑的公园",
    "model": "deepseek",
    "geo_context": {
      "location_name": "深圳南山区",
      "coordinates": {"lat": 22.5333, "lng": 113.9304},
      "coordinate_system": "WGS84"
    }
  }'
```

### 查询任务状态

```bash
curl "http://127.0.0.1:5000/api/v1/geo/jobs/<job_id>"
```

### 查看用户列表

```bash
curl "http://127.0.0.1:5000/api/v1/admin/users"
```

### 创建用户

```bash
curl -X POST "http://127.0.0.1:5000/api/v1/admin/users" \
  -H "Content-Type: application/json" \
  -d '{"username":"ops","password":"ops123456","role":"analyst"}'
```

### 更新用户角色或状态

```bash
curl -X PATCH "http://127.0.0.1:5000/api/v1/admin/users/2" \
  -H "Content-Type: application/json" \
  -d '{"role":"admin","status":"active"}'
```

### 查看任务列表

```bash
curl "http://127.0.0.1:5000/api/v1/admin/jobs"
```

### 重跑失败任务

```bash
curl -X POST "http://127.0.0.1:5000/api/v1/admin/jobs/<job_id>/retry"
```

### 查看审计日志

```bash
curl "http://127.0.0.1:5000/api/v1/admin/audit"
```

### 按操作者或动作筛选审计日志

```bash
curl "http://127.0.0.1:5000/api/v1/admin/audit?actor=admin&action=analysis.export"
```

### 查看历史列表

```bash
curl "http://127.0.0.1:5000/api/v1/geo/analyses?limit=10"
```

### 查看单条详情

```bash
curl "http://127.0.0.1:5000/api/v1/geo/analyses/1"
```

### 导出 JSON

```bash
curl -OJ "http://127.0.0.1:5000/api/v1/geo/analyses/1/export?format=json"
```

### 导出 Excel

```bash
curl -OJ "http://127.0.0.1:5000/api/v1/geo/analyses/1/export?format=xlsx"
```

### 导出 PDF

```bash
curl -OJ "http://127.0.0.1:5000/api/v1/geo/analyses/1/export?format=pdf"
```

## 模型配置

适配器支持两种模式：

- mock 模式：适合本地无密钥开发
- remote 模式：调用真实 API

### DeepSeek

```bash
DEEPSEEK_USE_MOCK=false
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_API_KEY=your-key
DEEPSEEK_MODEL_NAME=deepseek-chat
```

### 豆包 / 火山方舟

```bash
DOUBAO_USE_MOCK=false
DOUBAO_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
DOUBAO_API_KEY=your-key
DOUBAO_MODEL_NAME=your-endpoint-or-model
```

如果你拿的是完整接口地址，也可以直接设置：

- `DEEPSEEK_API_URL`
- `DOUBAO_API_URL`

它们会覆盖默认的 `BASE_URL + /chat/completions` 拼接逻辑。

参考文档：

- [DeepSeek API Docs](https://api-docs.deepseek.com/guides/multi_round_chat)
- [火山方舟 对话(Chat) API](https://www.volcengine.com/docs/82379/1298454)

## 数据库

默认：

```bash
DATABASE_URL=sqlite:///geo_optimizer.db
```

PostgreSQL / PostGIS：

```bash
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/geo_optimizer
```

应用启动时会自动：

- 初始化表结构
- 在 PostgreSQL 下执行 `CREATE EXTENSION IF NOT EXISTS postgis`
- 为 `analysis_records` 表补充 `geom geometry(Point, 4326)` 列

## 下一步建议

如果继续往正式产品推进，我建议下一轮优先做：

1. 用户删除、强制改密和细粒度权限
2. 真正的消息队列和定时任务调度
3. POI 检索与真实地图服务接入
4. 单元测试与接口测试
5. 更完整的运营报表和监控告警
