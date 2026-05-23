# Render 部署

本仓库包含 `render.yaml`，可以通过 Render Blueprint 部署：

1. 在 Render Dashboard 选择 **New > Blueprint**。
2. 连接 GitHub 仓库 `yaojingang/GEOFlow`。
3. 选择包含 `render.yaml` 的分支。
4. 填写 Render 提示的密钥：
   - `GEOFLOW_ADMIN_PASSWORD`：后台管理员 `admin` 的初始密码。
5. 创建 Blueprint，等待 `geoflow-web` 部署完成。

默认后台地址：

```text
https://<render-service-host>/geo_admin/login
```

Blueprint 会创建：

- `geoflow-web`：Apache + PHP 的 Web 服务。
- `geoflow-queue`：数据库队列 worker。
- `geoflow-scheduler`：每分钟执行一次 Laravel Scheduler。
- `geoflow-postgres`：PostgreSQL 16 数据库。
