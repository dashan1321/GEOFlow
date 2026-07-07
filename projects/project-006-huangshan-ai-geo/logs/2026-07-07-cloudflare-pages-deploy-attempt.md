# Cloudflare Pages 部署与验证记录

## 时间

2026-07-07

## 本次目标

把“黄山 AI 搜索优化 / GEO 优化服务”落地页发布到公开 Cloudflare Pages 静态站。

## 已完成

- 新增 `cf-pages/huangshan-ai-geo.html`
- 新增 `cf-pages/llms.txt`
- 新增 `cf-pages/sitemap.xml`
- 更新 `cf-pages/index.html`，加入黄山 AI 搜索优化入口
- 更新 `cf-pages/styles.css`，加入黄山落地页样式
- 本地静态服务器验证：

```text
http://127.0.0.1:8065/huangshan-ai-geo.html -> 200 OK
http://127.0.0.1:8065/llms.txt -> 200 OK
```

- 提交：

```text
0f325da Add Huangshan AI GEO landing page
```

- 推送：

```text
fork codex/release-ready -> dashan1321/GEOFlow:codex/release-ready
```

## 遇到的阻塞

### 1. 不能推送到原始远端

```text
remote: Permission to yaojingang/GEOFlow.git denied to dashan1321.
fatal: unable to access 'https://github.com/yaojingang/GEOFlow.git/': The requested URL returned error: 403
```

处理：新增 `fork` 远端，推送到 `dashan1321/GEOFlow` 成功。

### 2. Wrangler 直传缺 Cloudflare API Token

```text
ERROR In a non-interactive environment, it's necessary to set a CLOUDFLARE_API_TOKEN environment variable for wrangler to work.
```

处理：未绕过密钥；改走 GitHub fork 推送路线。

### 3. 公开 URL 暂未更新

检查：

```text
https://geoflow-bp2.pages.dev/huangshan-ai-geo.html -> 404
https://geoflow-bp2.pages.dev/llms.txt -> 404
```

判断：当前 Cloudflare Pages 项目未绑定 `dashan1321/GEOFlow` 的 `codex/release-ready` 分支，或未触发该分支构建。

### 4. 浏览器接管部署卡在账号认证

用户要求 Codex 自行操作后，已打开 Cloudflare Pages 的 GitHub provider 部署入口：

```text
https://dash.cloudflare.com/?to=/:account/pages/new/provider/github
```

实际跳转到 Cloudflare 登录页，选择“使用 GitHub 继续”后进入 GitHub 登录页：

```text
https://github.com/login?...Cloudflare OAuth...
```

当前页面要求输入 GitHub 账号密码或使用 passkey。Codex 无法绕过账号认证，也不能替用户输入未知密码或验证码。

下一步：用户在 Chrome 中完成 GitHub 登录 / passkey / 2FA 后，Codex 可以继续接管 Cloudflare Pages 配置与部署。

## 下一步选项

### 已执行：Wrangler OAuth 直传部署

用户完成 GitHub 设备验证后，Codex 使用浏览器完成 Cloudflare 登录，并通过 Wrangler OAuth 授权：

```text
npx wrangler login
```

随后执行预览分支部署：

```text
npx wrangler pages deploy cf-pages --project-name geoflow
```

输出：

```text
Deployment complete! Take a peek over at https://b1b38520.geoflow-bp2.pages.dev
Deployment alias URL: https://codex-release-ready.geoflow-bp2.pages.dev
```

该分支预览会自动带 `x-robots-tag: noindex`，因此继续执行生产分支部署：

```text
npx wrangler pages deploy cf-pages --project-name geoflow --branch main
```

输出：

```text
Deployment complete! Take a peek over at https://f024fdf9.geoflow-bp2.pages.dev
```

## 正式 URL 验证

```text
https://geoflow-bp2.pages.dev/huangshan-ai-geo -> HTTP/2 200
https://geoflow-bp2.pages.dev/llms.txt -> HTTP/2 200
https://geoflow-bp2.pages.dev/sitemap.xml -> HTTP/2 200
```

页面正文已确认包含：

```text
黄山 AI 搜索优化 / GEO 优化服务
GEOFlow 黄山 AI 搜索优化
豆包、Kimi、DeepSeek、百度 AI、秘塔
```

## 下一步

- 使用正式 URL 做豆包、Kimi、DeepSeek、百度 AI、秘塔第一轮基线测试。
- 把正式 URL 放入公众号、朋友圈、小红书、抖音、知乎简介或内容入口。
- 后续如果要让 GitHub push 自动部署，需要在 Cloudflare Pages 里完成 GitHub App 仓库授权。

## 备选方案 A：提供 Cloudflare API Token

在当前 shell 设置：

```text
CLOUDFLARE_API_TOKEN=...
```

然后执行：

```text
npx wrangler pages deploy cf-pages --project-name geoflow
```

## 备选方案 B：Cloudflare Pages 绑定 GitHub fork

在 Cloudflare Pages 项目 `geoflow` 里配置：

```text
Repository: dashan1321/GEOFlow
Branch: codex/release-ready
Build command: 留空
Build output directory: cf-pages
```

然后触发部署。
