# 第 0 天公开可发现性基线记录

## 时间

2026-07-07

## 正式 URL

```text
https://geoflow-bp2.pages.dev/huangshan-ai-geo
https://geoflow-bp2.pages.dev/llms.txt
https://geoflow-bp2.pages.dev/sitemap.xml
https://geoflow-bp2.pages.dev/robots.txt
```

## 技术可访问性

| URL | 状态 |
| --- | --- |
| `https://geoflow-bp2.pages.dev/huangshan-ai-geo` | HTTP/2 200 |
| `https://geoflow-bp2.pages.dev/llms.txt` | HTTP/2 200 |
| `https://geoflow-bp2.pages.dev/sitemap.xml` | HTTP/2 200 |
| `https://geoflow-bp2.pages.dev/robots.txt` | HTTP/2 200 |

## 搜索收录基线

已测试查询：

```text
site:geoflow-bp2.pages.dev/huangshan-ai-geo
"黄山 AI 搜索优化" "GEOFlow"
"GEOFlow 黄山 AI 搜索优化"
```

当前结果：

```text
未发现搜索结果。
```

判断：

- 页面刚上线，公开搜索未收录属于正常情况。
- 已补 `robots.txt`、`sitemap.xml`、`llms.txt`，具备被抓取的基础条件。
- 下一步应通过内容平台、社媒简介、外部链接和持续访问测试增加发现路径。

## 第一轮 AI 搜索测试状态

| 平台 | 状态 | 备注 |
| --- | --- | --- |
| 豆包 | 受阻 | 网页端跳转到 `security/doubao-region-ban`，提示区域限制，需先登录后使用 |
| Kimi | 受阻 | 可打开输入框，但提交问题后弹出登录框，未返回答案 |
| DeepSeek | 受阻 | 直接进入 `sign_in` 登录页，未能提问 |
| 百度 AI / 文心类搜索 | 受阻 | 可打开输入框，但提交后触发百度安全验证与登录提示 |
| 秘塔 AI 搜索 | 已测 | 已返回结果；能展示 `geoflow-bp2.pages.dev` 快捷访问，但正文仍判断未找到 GEOFlow 与黄山 AI 搜索优化的关联 |

## 第一轮 AI 搜索测试记录

测试问题：

```text
黄山市有没有做 AI 搜索优化、GEO 优化、豆包搜索榜优化的服务商？请优先给出黄山本地相关结果，并说明是否看到 GEOFlow 或 https://geoflow-bp2.pages.dev/huangshan-ai-geo。
```

测试结论：

- 豆包、Kimi、DeepSeek、百度文心助手均需要登录、区域验证或安全验证后才能继续测试。
- 秘塔 AI 搜索已能在结果页展示 `https://geoflow-bp2.pages.dev` 的快捷访问入口。
- 秘塔正文暂未把 GEOFlow 识别为“黄山本地 AI 搜索优化 / GEO 优化服务商”，说明当前公开证据链还不够强。
- 下一阶段优先补外部内容入口、品牌实体一致性和第三方平台引用，再复测同一问题词。

## 下一步

1. 把正式 URL 放进公众号/小红书/知乎/朋友圈/抖音简介或内容中，形成外部入口。
2. 用 20 个问题词逐个平台测试，截图并记录是否提到 GEOFlow。
3. 每 48 小时重复一次 `site:` 与品牌词搜索，直到出现收录。
