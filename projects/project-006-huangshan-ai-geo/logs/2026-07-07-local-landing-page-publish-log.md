# 本地应用落地页接入记录

## 时间

2026-07-07

## 本次动作

将“黄山 AI 搜索优化 / GEO 优化服务”落地页接入当前 Flask / GEOFlow 应用。

## 新增/修改位置

| 文件 | 动作 |
| --- | --- |
| `app/api.py` | 新增 `/huangshan-ai-geo`、`/huangshan-ai-search-optimization`、`/huangshan-geo` 公开路由，并加入 `llms.txt` 与 `sitemap.xml` |
| `app/templates/huangshan_ai_geo.html` | 新增黄山 AI 搜索优化服务页 |
| `app/static/app.css` | 新增黄山服务页样式 |
| `tests/test_app.py` | 增加公开页面、`llms.txt`、`sitemap.xml` 测试断言 |

## 本地访问地址

```text
http://127.0.0.1:5050/huangshan-ai-geo
```

## 验证记录

```text
python3 -m unittest tests.test_app.GeoAppTestCase.test_auth_required tests.test_app.GeoAppTestCase.test_public_geo_assets

结果：2 tests OK
```

```text
curl -I http://127.0.0.1:5050/huangshan-ai-geo

结果：HTTP/1.1 200 OK
```

## 下一步

- 部署到公开域名。
- 打开公开页面后检查手机和桌面显示。
- 将公开 URL 加入 AI 搜索问题词测试表。
- 开始豆包、Kimi、DeepSeek、百度 AI、秘塔第一轮基线测试。
