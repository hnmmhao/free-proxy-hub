# ⚡ Global Proxy Hub

> **全自动云端代理节点聚合站 | 零服务器成本 | Cloudflare Pages 全球分发 | 天生防 DDoS**

![GitHub Actions](https://img.shields.io/github/actions/workflow/status/hnmmhao/free-proxy-hub/sync.yml?label=Auto%20Sync&logo=github)
![Cloudflare Pages](https://img.shields.io/badge/Cloudflare-Pages-380d9e?logo=cloudflare)

---

## 📋 项目概述

这是一个**完全自动化**的代理节点聚合工具站：

| 特性 | 说明 |
|------|------|
| 🛡️ **零服务器成本** | GitHub Actions 跑任务，Cloudflare Pages 托管 |
| 🌐 **全球 CDN 分发** | Cloudflare 边缘网络，毫秒级加载 |
| 🔄 **每30分钟自动更新** | GitHub 海外虚拟机定时抓取+测活 |
| 📊 **暗黑大厂风 UI** | Tailwind CSS 4，响应式设计 |
| 📢 **AdSense 就绪** | 页面已预留广告位，可直接投放 |
| 🔍 **实时筛选** | 按国家/协议/IP 免刷新过滤 |

---

## 🏗️ 架构图

```
                     ┌─────────────────────────┐
                     │     5 个公开代理源       │
                     └──────────┬──────────────┘
                                ▼
┌───────────────────────────────────────────────────┐
│           GitHub Actions (每30分钟)                │
│                                                   │
│   build_assets.py                                  │
│   ├── 多源并发抓取原始代理                         │
│   ├── 多线程匿名度检测 (80线程)                    │
│   ├── Google 连通性测活 (generate_204)            │
│   ├── 按速度排序                                  │
│   ├── 输出 JSON → api/*.json                      │
│   └── 生成 HTML → index.html                      │
└──────────────────┬────────────────────────────────┘
                   ▼
┌───────────────────────────────────────────────────┐
│           GitHub 仓库 (自动推送)                   │
│                                                   │
│   hnmmhao/free-proxy-hub                          │
│   ├── index.html          ← 静态首页              │
│   ├── api/proxies.json    ← 全量数据              │
│   ├── api/http.json       ← HTTP 节点             │
│   └── api/socks5.json     ← SOCKS5 节点           │
└──────────────────┬────────────────────────────────┘
                   ▼
┌───────────────────────────────────────────────────┐
│           Cloudflare Pages                         │
│                                                   │
│   ├── 连接 GitHub 仓库                             │
│   ├── 自动部署 (检测到变更即触发)                  │
│   ├── 全球 CDN 加速                               │
│   └── 自带 DDoS 防护                              │
└───────────────────────────────────────────────────┘
```

---

## 🚀 部署步骤

### 第 1 步：理解项目结构

```
free-proxy-hub/
├── .github/
│   └── workflows/
│       └── sync.yml        ← GitHub Actions 定时任务配置
├── build_assets.py         ← 核心引擎（抓取+测活+生成页面）
├── index.html              ← 生成的静态首页（自动生成，无需手动编辑）
├── api/
│   ├── proxies.json        ← 全量代理数据
│   ├── http.json           ← HTTP 代理数据
│   └── socks5.json         ← SOCKS5 代理数据
└── README.md               ← 本文件
```

### 第 2 步：激活 GitHub Actions

1. 打开仓库: https://github.com/hnmmhao/free-proxy-hub
2. 点击 **Actions** 选项卡
3. 左侧点击 **🔄 Proxy Hub Commercial Auto Engine**
4. 点击右侧 **Run workflow** → 绿色 **Run workflow** 按钮
5. 等待 1-2 分钟运行完成
6. 返回仓库首页，确认已自动生成 `index.html` 和 `api/` 文件夹

> ⏱️ 首次运行后，之后每 30 分钟会自动抓取更新

### 第 3 步：部署到 Cloudflare Pages

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com)
2. 左侧导航 → **Workers 和 Pages** → **Pages**
3. 点击 **连接到 Git** → 选择 **GitHub**
4. 授权后找到并选中 `hnmmhao/free-proxy-hub`
5. **配置页面**（关键设置）：

| 字段 | 值 |
|------|-----|
| 项目名称 | 保持默认 |
| 生产分支 | `main` |
| 框架预设 | **无**（None） |
| 构建命令 | **留空** |
| 构建输出目录 | **留空** |

6. 点击 **保存并部署**
7. 部署成功后，Cloudflare 会生成一个 `https://xxxx.pages.dev` 域名
8. **（可选）** 绑定自定义域名：Pages → 项目 → 自定义域 → 添加

> ⚡ 由于 `index.html` 已经是完整的静态页面，Cloudflare 无需任何编译，直接分发

---

## 🌐 数据 API 接口

部署后，你还可以通过 RESTful API 获取数据：

| 接口 | 说明 |
|------|------|
| `GET /api/proxies.json` | 全量代理（按速度排序） |
| `GET /api/http.json` | HTTP 代理 |
| `GET /api/socks5.json` | SOCKS5 代理 |

---

## 📢 Google AdSense 接入

当站点积累一定流量后，在 `build_assets.py` 的 `HTML_TEMPLATE` 中搜索 `AdSense`，将占位注释替换为你的 AdSense 代码：

```html
<!--
  找到这段注释，替换为：
-->
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
<ins class="adsbygoogle" style="display:block"
     data-ad-client="ca-pub-xxxxxxxxxxxxxx"
     data-ad-slot="xxxxxxxxxx"
     data-ad-format="auto"></ins>
<script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
```

---

## ⚙️ 自定义配置

如需调整，编辑 `build_assets.py`：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `PROXY_SOURCES` | 代理数据源 URL 列表 | 5 个公开源 |
| `max_workers` | 测活并发线程数 | 80 |
| `GEO_TARGET` | 地理位置查询 API | `api.ip.sb/geoip` |
| `GOOG_TARGET` | Google 连通性测试地址 | `google.com/generate_204` |

---

## 📄 许可证

本项目仅供学习和研究使用。数据来源于公开代理列表，请遵守当地法律法规。
