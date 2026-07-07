# 黄山 AI 搜索优化 GEO 样板

## 项目目标

把“黄山 AI 搜索优化 / GEO 优化 / 豆包搜索优化”做成本地样板业务：当潜在客户在豆包、Kimi、DeepSeek、百度 AI、秘塔等 AI 搜索里询问黄山本地 AI 搜索优化、GEO 优化、企业 AI 获客时，能够逐步识别到 GEOFlow / 王总的服务、案例、诊断报告和内容资产。

第一阶段验收标准：

- 有清晰的本地定位、服务定义和对外落地页文案。
- 有 20 个核心 AI 搜索测试问题词。
- 有 30 天内容发布日历。
- 有可交付给客户的 AI 搜索可见度诊断报告模板。
- 有每周 AI 搜索榜记录表，能持续复盘是否被提及、引用和排名。

## 当前状态

- 状态：进行中
- 最近更新：2026-07-07
- 当前负责人：王总 / Codex

## 关键文件

| 文件 | 用途 | 状态 |
| --- | --- | --- |
| `brief/2026-07-07-original-request.md` | 原始需求与任务判断 | 已生成 |
| `docs/2026-07-07-huangshan-ai-geo-execution-plan.md` | 黄山本地第一名执行方案 | 已生成 |
| `source/2026-07-07-ai-search-question-bank.csv` | 20 个核心 AI 搜索问题词 | 已生成 |
| `source/2026-07-07-30-day-content-calendar.csv` | 30 天内容日历 | 已生成 |
| `source/2026-07-07-brand-entity-profile.md` | 品牌实体统一资料 | 已生成 |
| `docs/2026-07-07-operations-checklist.md` | 每日、每周、客户诊断执行清单 | 已生成 |
| `outputs/2026-07-07-landing-page-copy-v01.md` | 对外落地页文案 | 已生成 |
| `outputs/2026-07-07-client-diagnostic-report-template-v01.md` | 客户诊断报告模板 | 已生成 |
| `outputs/2026-07-07-first-7-days-content-pack-v01.md` | 前 7 天可发布内容包 | 已生成 |
| `logs/2026-07-07-weekly-ai-search-ranking-log.md` | 每周 AI 搜索榜记录表 | 已生成 |
| `logs/2026-07-07-local-landing-page-publish-log.md` | 本地应用落地页接入记录 | 已生成 |
| `logs/2026-07-07-cloudflare-pages-deploy-attempt.md` | Cloudflare Pages 部署尝试记录 | 已生成 |

## 目录说明

| 目录 | 用途 |
| --- | --- |
| `brief/` | 原始需求、聊天摘要、客户背景、任务说明 |
| `source/` | 源代码、源数据、可编辑源文件 |
| `docs/` | 项目过程文档、方案、SOP、分析 |
| `assets/` | 图片、视频、音频、字体、设计素材 |
| `outputs/` | 最终报告、PPT、合同、导出文件、成品 |
| `logs/` | 执行记录、测试记录、会议纪要、问题记录 |
| `archive/` | 旧版本、废弃方案、备份文件 |

## 下一步

- [x] 明确项目目标和验收标准。
- [x] 归档原始需求到 `brief/`。
- [x] 生成第一批执行资产。
- [x] 把落地页文案发布到本地 GEOFlow 应用公开页面。
- [x] 生成 Cloudflare Pages 静态版并推送到 GitHub fork。
- [ ] 配置 Cloudflare Pages 自动部署或提供 `CLOUDFLARE_API_TOKEN` 直传。
- [ ] 按问题词表完成第一轮豆包、Kimi、DeepSeek、百度 AI、秘塔测试。
- [ ] 连续 7 天发布第一批内容，并记录是否被 AI 搜索识别。
- [ ] 把品牌实体资料同步到公众号、抖音、小红书、知乎、视频号等平台。
- [ ] 用诊断报告模板服务前 3 个黄山本地样板客户。

## 重要记录

```text
日期：2026-07-07
记录：创建黄山 AI 搜索优化 GEO 样板项目，并生成第一批定位、内容、测试、诊断资产。
影响：把“我要做到黄山本地 AI 搜索榜第一”的想法拆成可执行项目，不再停留在口号。
下一步：发布落地页，开始第一轮 AI 搜索基线测试和 30 天内容执行。
```

```text
日期：2026-07-07
记录：新增本地公开页面 /huangshan-ai-geo，并加入 llms.txt 与 sitemap.xml。
影响：黄山 AI 搜索优化服务已有可访问的本地落地页入口，可继续部署到公开域名。
下一步：部署上线后提交收录入口，并开始 AI 搜索基线测试。
```

```text
日期：2026-07-07
记录：新增 Cloudflare Pages 静态版 `cf-pages/huangshan-ai-geo.html`、`llms.txt`、`sitemap.xml`，提交并推送到 `dashan1321/GEOFlow` 的 `codex/release-ready` 分支。
影响：代码已到 GitHub fork，但 `geoflow-bp2.pages.dev` 暂未出现新页面；Wrangler 直传因缺少 `CLOUDFLARE_API_TOKEN` 被 Cloudflare 拦截。
下一步：在 Cloudflare Pages 绑定该 fork/分支，或提供 API Token 后用 Wrangler 直接部署。
```
