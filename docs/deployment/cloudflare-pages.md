# Cloudflare Pages 部署

GEOFlow 的完整后台是 Laravel/PHP 应用，需要 PHP 运行时、PostgreSQL、队列和常驻任务。Cloudflare Pages 不能直接运行这套后台，本目录提供的是可免费托管的静态入口页。

## Cloudflare Pages 设置

- Repository: `dashan1321/GEOFlow`
- Branch: `main`
- Build command: 留空
- Build output directory: `cloudflare-pages`

部署后会得到一个 `*.pages.dev` 免费域名。
