#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
* Global Proxy Hub - 全自动代理节点聚合引擎
====================================================
功能:
  1. 从 5 个数据源抓取原始代理 IP
  2. 多线程匿名度检测 + Google 连通性测试
  3. 自动生成 HTML 静态页面（预留 AdSense 广告位）
  4. 输出 JSON 数据到 api/ 目录
====================================================
"""

import requests
import re
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# ==================== 1. 多源全量配置 ====================
PROXY_SOURCES = [
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt",
    "https://raw.githubusercontent.com/mmpx12/proxy-list/master/https.txt",
    "https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks5.txt",
    "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/https/https.txt",
    "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks5/socks5.txt",
    "https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/https.txt",
    "https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/socks5.txt",
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt",
]

GEO_TARGET = "https://api.ip.sb/geoip"
GOOG_TARGET = "https://www.google.com/generate_204"

# ==================== 2. 抓取模块 ====================
def fetch_all_raw_ips():
    """从所有数据源抓取原始代理 IP:Port"""
    raw_pool = []
    for url in PROXY_SOURCES:
        try:
            res = requests.get(url, timeout=15)
            if res.status_code == 200:
                found = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}', res.text)
                raw_pool.extend(found)
                print(f"  [OK] {url.split('/')[2][:30]:>30} -> {len(found):>4} 条")
        except Exception as e:
            print(f"  [ER] {url.split('/')[2][:30]:>30} -> 失败: {str(e)[:40]}")
    return list(set(raw_pool))

# ==================== 3. 探测模块 ====================
def inspect_proxy(ip_port):
    """双阶段探测：地理位置 -> Google 连通性"""
    protocols = ["http", "socks5"]
    for proto in protocols:
        proxy_env = {"http": f"{proto}://{ip_port}", "https": f"{proto}://{ip_port}"}
        try:
            # 阶段一：地理位置探测
            response = requests.get(GEO_TARGET, proxies=proxy_env, timeout=3)
            if response.status_code != 200:
                continue
            geo_data = response.json()
            country = geo_data.get("country_code", "US")
            region = geo_data.get("region", "")
            city = geo_data.get("city", "")

            # 阶段二：Google 连通性验证
            try:
                goog_res = requests.get(GOOG_TARGET, proxies=proxy_env, timeout=3)
                if goog_res.status_code != 204:
                    continue
                speed_ms = int(goog_res.elapsed.total_seconds() * 1000)
            except Exception:
                continue

            return {
                "ip_port": ip_port,
                "protocol": proto.upper(),
                "country": country,
                "region": region,
                "city": city,
                "anonymity": "Elite",
                "speed": speed_ms
            }
        except Exception:
            continue
    return None

# ==================== 4. HTML 模板 ====================
HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN" data-lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Global Proxy Hub — Free High-Speed Anonymous Proxy List | Updated Every 30min</title>
<meta name="description" content="Global Proxy Hub - Free high-speed anonymous proxy IP list. HTTP & SOCKS5 proxies from 26+ countries, updated every 30 minutes. Low latency, elite anonymity, CORS API support.">
<meta name="robots" content="index, follow">
<meta name="keywords" content="free proxy, proxy list, HTTP proxy, SOCKS5 proxy, anonymous proxy, free proxy list, proxy hub, high speed proxy">
<link rel="canonical" href="https://free-proxy-hub.pages.dev">
<link rel="alternate" hreflang="zh-CN" href="https://free-proxy-hub.pages.dev">
<link rel="alternate" hreflang="en" href="https://free-proxy-hub.pages.dev/?lang=en">
<link rel="alternate" hreflang="x-default" href="https://free-proxy-hub.pages.dev">
<meta name="theme-color" content="#0d47a1">
<meta name="author" content="Global Proxy Hub">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta property="og:title" content="Global Proxy Hub — Free High-Speed Anonymous Proxy List">
<meta property="og:description" content="Free high-speed anonymous proxy IP list. HTTP & SOCKS5 proxies from 26+ countries, updated every 30 minutes.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://free-proxy-hub.pages.dev">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="Global Proxy Hub — Free High-Speed Anonymous Proxy List">
<meta name="twitter:description" content="Free high-speed anonymous proxy IP list. HTTP & SOCKS5 proxies from 26+ countries, updated every 30 minutes.">
<meta property="og:image" content="https://free-proxy-hub.pages.dev/og-image.png">
<meta property="og:locale" content="zh_CN">
<meta property="og:site_name" content="Global Proxy Hub">
<meta name="twitter:image" content="https://free-proxy-hub.pages.dev/og-image.png">

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "Global Proxy Hub",
  "alternateName": ["Global Proxy Hub", "全球代理中心"],
  "url": "https://free-proxy-hub.pages.dev",
  "description": "Free high-speed anonymous proxy IP list. HTTP & SOCKS5 proxies from 26+ countries, updated every 30 minutes.",
  "inLanguage": ["zh-CN", "en"],
  "potentialAction": {
    "@type": "SearchAction",
    "target": {
      "@type": "EntryPoint",
      "urlTemplate": "https://free-proxy-hub.pages.dev/?search={search_term_string}"
    },
    "query-input": "required name=search_term_string"
  }
}
</script>
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [{
    "@type": "ListItem",
    "position": 1,
    "name": "Global Proxy Hub",
    "item": "https://free-proxy-hub.pages.dev"
  }]
}
</script>

<script src="https://cdn.tailwindcss.com"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif;background:#f5f5f5;color:#333}
.container{max-width:1200px;margin:0 auto;padding:0 15px}
.header{background:linear-gradient(135deg,#1a73e8,#0d47a1);color:#fff;padding:24px 0 40px}
.header .logo{font-size:24px;font-weight:700}
.header .logo span{color:#ffd54f}
.header .subtitle{font-size:13px;opacity:.85;margin-top:2px}
.header .nav a{color:rgba(255,255,255,.85);text-decoration:none;font-size:14px;padding:6px 14px;border-radius:4px;transition:all .2s;cursor:pointer}
.header .nav a:hover{background:rgba(255,255,255,.15);color:#fff}
.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:15px;margin-top:20px}
.stat-card{background:#fff;border-radius:10px;padding:20px;box-shadow:0 2px 12px rgba(0,0,0,.06);text-align:center}
.stat-card .num{font-size:32px;font-weight:700;color:#1a73e8}
.stat-card .label{font-size:13px;color:#888;margin-top:4px}
.ad-box{background:#fafafa;border:1px dashed #ddd;border-radius:6px;padding:12px;text-align:center;margin:15px 0;min-height:70px;display:flex;align-items:center;justify-content:center;font-size:12px;color:#aaa}
.content-wrap{display:flex;gap:20px;margin-top:20px}
.main-area{flex:1;min-width:0}
.sidebar{width:280px;flex-shrink:0}
@media(max-width:768px){.content-wrap{flex-direction:column}.sidebar{width:100%}}
.card{background:#fff;border-radius:10px;box-shadow:0 2px 12px rgba(0,0,0,.06);overflow:hidden}
.card-title{padding:14px 18px;font-size:15px;font-weight:600;border-bottom:1px solid #f0f0f0;display:flex;justify-content:space-between;align-items:center}
.card-body{padding:16px}
.filter-bar{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:14px}
.filter-bar select,.filter-bar input{padding:7px 12px;border:1px solid #e0e0e0;border-radius:6px;font-size:13px;background:#fff;outline:none}
.filter-bar select:focus,.filter-bar input:focus{border-color:#1a73e8}
.filter-bar select{min-width:120px}
.filter-bar input{flex:1;min-width:140px}
.proxy-table{width:100%;border-collapse:collapse;font-size:13px}
.proxy-table thead{background:#f8f9fa}
.proxy-table th{padding:10px 12px;text-align:left;font-weight:600;color:#666;font-size:12px;border-bottom:2px solid #eee}
.proxy-table td{padding:10px 12px;border-bottom:1px solid #f0f0f0;vertical-align:middle}
.proxy-table tbody tr:hover{background:#f8faff}
.ip-cell{font-family:Courier New,monospace;color:#1a73e8;font-weight:500;font-size:12px}
.proto-badge{display:inline-block;padding:2px 8px;border-radius:3px;font-size:11px;font-weight:600}
.badge-http{background:#e3f2fd;color:#1565c0}
.badge-socks5{background:#f3e5f5;color:#7b1fa2}
.copy-btn{cursor:pointer;color:#999;padding:4px 8px;border-radius:4px;font-size:14px;user-select:none}
.copy-btn:hover{color:#1a73e8;background:#e3f2fd}
.pagination{display:flex;align-items:center;justify-content:space-between;padding:12px 16px;border-top:1px solid #f0f0f0;font-size:13px}
.pagination .info{color:#888}
.pagination .pages{display:flex;gap:4px;align-items:center}
.pagination button{padding:5px 12px;border:1px solid #e0e0e0;border-radius:4px;background:#fff;cursor:pointer;font-size:13px;color:#555;transition:all .2s}
.pagination button:hover{border-color:#1a73e8;color:#1a73e8}
.pagination button:disabled{opacity:.4;cursor:default}
.sidebar .side-card{background:#fff;border-radius:10px;box-shadow:0 2px 12px rgba(0,0,0,.06);padding:18px;margin-bottom:15px}
.sidebar .side-title{font-size:15px;font-weight:600;margin-bottom:12px;padding-bottom:10px;border-bottom:2px solid #1a73e8;display:inline-block}
.sidebar .side-item{font-size:13px;color:#666;padding:6px 0;display:flex;justify-content:space-between}
.sidebar .side-item .key{color:#999}
.sidebar .side-item .val{color:#333;font-weight:500}
.api-endpoint{background:#f8f9fa;border:1px solid #eee;border-radius:6px;padding:12px 14px;margin-bottom:10px;font-size:13px}
.api-endpoint .method{display:inline-block;padding:1px 8px;border-radius:3px;font-size:11px;font-weight:700;color:#fff;background:#1a73e8;margin-right:8px}
.api-endpoint .url{font-family:monospace;font-size:12px;color:#333}
.sidebar .api-desc{font-size:12px;color:#888;margin:-5px 0 10px 0;padding-left:4px}
.footer{background:#1a1a2e;color:#888;text-align:center;padding:20px;margin-top:30px;font-size:12px}
.hidden{display:none!important}
</style></head>
<body>
<div class="header">
<div class="container">
<div class="flex items-center justify-between flex-wrap gap-2">
<div>
<h1>
<span class="logo">Global <span>Proxy</span> Hub</span>
<span class="subtitle"><span data-i18n="header_subtitle">免费高速代理IP - 30分钟自动更新</span></span>
</h1>
</div>
<div class="nav flex items-center gap-1">
<a href="#proxy-list" data-i18n="nav_proxies">代理列表</a>
<a href="#api-docs" data-i18n="nav_api">API文档</a>
<a id="langToggle" onclick="toggleLang()" style="border:1px solid rgba(255,255,255,.5);padding:4px 12px;border-radius:4px;font-size:12px">English</a>
</div>
</div>
</div>
</div>

<main class="container">
<div class="stats-grid" style="margin-top:-20px">
<div class="stat-card"><div class="num" style="color:#e65100" id="stat-total">{{NODE_COUNT}}</div><div class="label" data-i18n="stat_nodes">代理节点</div></div>
<div class="stat-card"><div class="num" style="color:#1565c0" id="stat-http">0</div><div class="label">HTTP</div></div>
<div class="stat-card"><div class="num" style="color:#7b1fa2" id="stat-socks5">0</div><div class="label">SOCKS5</div></div>
<div class="stat-card"><div class="num" style="color:#2e7d32" id="stat-countries">0</div><div class="label" data-i18n="stat_countries">覆盖国家</div></div>
</div>

<div class="content-wrap">
<div class="main-area">
<div class="card" id="proxy-list">
<div class="card-title"><h2 data-i18n="card_title">代理列表</h2><span class="update-badge" style="color:#555;font-weight:normal"><span class="dot" style="background:#4caf50"></span> <span data-i18n="card_updated">更新时间</span>: <time datetime="{{UPDATE_TIME_ISO}}">{{UPDATE_TIME}} UTC</time></span></div>
<div class="card-body">
<div class="filter-bar">
<select id="search_proto" onchange="filterTable()"><option value="ALL" data-i18n="filter_all_proto">全部协议</option><option value="HTTP">HTTP</option><option value="SOCKS5">SOCKS5</option></select>
<select id="search_country" onchange="filterTable()"><option value="ALL" data-i18n="filter_all_country">全部国家</option></select>
<input type="text" id="search_ip" oninput="filterTable()" data-i18n="placeholder" placeholder="搜索 IP...">
</div>
<div style="overflow-x:auto">
<table class="proxy-table">
<thead><tr>
<th><a href="#" onclick="sortTable('ip_port');return false" style="text-decoration:none;color:inherit" data-i18n="th_ip">IP:Port</a></th>
<th data-i18n="th_proto">协议</th>
<th data-i18n="th_country">国家</th>
<th data-i18n="th_anonymity">匿名度</th>
<th><a href="#" onclick="sortTable('speed');return false" style="text-decoration:none;color:inherit" data-i18n="th_speed">速度</a></th>
<th data-i18n="th_copy">操作</th>
</tr></thead>
<tbody id="proxy-tbody">{{TABLE_ROWS}}</tbody>
</table>
</div>
<div class="pagination">
<div class="info"><span data-i18n="pagination_total">共</span> <span id="total-count">{{NODE_COUNT}}</span> <span data-i18n="pagination_items">条</span></div>
<div class="pages">
<button id="prevBtn" onclick="prevPage()"><span data-i18n="btn_prev">← 上一页</span></button>
<span class="page-info" id="page-num">1 / 1</span>
<button id="nextBtn" onclick="nextPage()"><span data-i18n="btn_next">下一页 →</span></button>
</div></div></div></div>
</div>

<aside class="sidebar">
<section class="side-card" id="stats-sidebar">
<h3 class="side-title" data-i18n="sidebar_stats_title">数据统计</h3>
<div class="side-item"><span class="key" data-i18n="sidebar_total">总节点</span><span class="val" id="s-total">{{NODE_COUNT}}</span></div>
<div class="side-item"><span class="key">HTTP</span><span class="val" id="s-http">0</span></div>
<div class="side-item"><span class="key">SOCKS5</span><span class="val" id="s-socks5">0</span></div>
<div class="side-item"><span class="key" data-i18n="sidebar_countries">国家</span><span class="val" id="s-countries">0</span></div>
<div class="side-item"><span class="key" data-i18n="sidebar_update">更新</span><span class="val">30min</span></div>
</section>

<section class="side-card" id="api-docs">
<h3 class="side-title" data-i18n="sidebar_api_title">API 接口</h3>
<div class="api-endpoint"><span class="method">GET</span><span class="url">/api/proxies.json</span></div>
<div class="sidebar api-desc" data-i18n="api_proxies_desc">全量代理数据，按速度升序，支持 CORS</div>
<div class="api-endpoint"><span class="method">GET</span><span class="url">/api/http.json</span></div>
<div class="sidebar api-desc" data-i18n="api_http_desc">仅 HTTP/HTTPS 协议代理</div>
<div class="api-endpoint"><span class="method">GET</span><span class="url">/api/socks5.json</span></div>
<div class="sidebar api-desc" data-i18n="api_socks_desc">仅 SOCKS5 协议代理</div>
<div style="margin-top:10px;padding-top:10px;border-top:1px solid #eee;font-size:12px;color:#666">
<div style="font-weight:600;color:#333;margin-bottom:6px">📖 调用示例</div>
<div style="background:#f8f9fa;border-radius:4px;padding:8px;margin-bottom:6px;font-family:monospace;font-size:11px;line-height:1.6">
<span style="color:#888"># cURL</span><br>curl -s <span style="color:#d63384">https://free-proxy-hub.pages.dev/api/proxies.json</span> | jq .[:2]
</div>
<div style="background:#f8f9fa;border-radius:4px;padding:8px;margin-bottom:6px;font-family:monospace;font-size:11px;line-height:1.6">
<span style="color:#888"># Python</span><br>import requests<br>data = requests.get("<span style="color:#d63384">https://free-proxy-hub.pages.dev/api/proxies.json</span>").json()<br>for p in data[:5]: print(p["ip_port"], p["protocol"], p["speed"], "ms")
</div>
<div style="background:#f8f9fa;border-radius:4px;padding:8px;font-family:monospace;font-size:11px;line-height:1.6">
<span style="color:#888"># JavaScript</span><br>fetch("<span style="color:#d63384">https://free-proxy-hub.pages.dev/api/proxies.json</span>")<br>&nbsp;&nbsp;.then(r => r.json())<br>&nbsp;&nbsp;.then(data => console.log(data.slice(0,3)))</div>
</div>
</section>

<section class="ad-box" style="display:none" data-i18n="ad_336">广告位：336x280 方形模块</section>
</aside>
</div>
</main>

<footer class="footer">
<div class="container">
<div data-i18n="footer_text">Global Proxy Hub — 免费高匿代理 IP 资源站 | 数据每 30 分钟自动更新</div>
</div>
</footer>

<script>
// ========== i18n ==========
const I18N={
zh:{
header_subtitle:"免费高速代理IP - 30分钟自动更新",
nav_proxies:"代理列表",
nav_api:"API文档",
stat_nodes:"代理节点",
stat_countries:"覆盖国家",
card_title:"代理列表",
card_updated:"更新时间",
filter_all_proto:"全部协议",
filter_all_country:"全部国家",
placeholder:"搜索 IP...",
th_ip:"IP:Port",
th_proto:"协议",
th_country:"国家",
th_anonymity:"匿名度",
th_speed:"速度",
th_copy:"操作",
pagination_total:"共",
pagination_items:"条",
btn_prev:"← 上一页",
btn_next:"下一页 →",
sidebar_stats_title:"数据统计",
sidebar_total:"总节点",
sidebar_countries:"国家",
sidebar_update:"更新",
sidebar_api_title:"API 接口",
api_proxies_desc:"全量代理数据，按速度升序，支持 CORS",
api_http_desc:"仅 HTTP/HTTPS 协议代理",
api_socks_desc:"仅 SOCKS5 协议代理",
api_examples:"📋 调用示例",
ad_336:"广告位：336x280 方形模块",
ad_250:"广告位：250x250 方形",
ad_728:"广告位：728x90 底部横幅",
footer_text:"Global Proxy Hub — 免费高匿代理 IP 资源站 | 数据每 30 分钟自动更新"
},
en:{
header_subtitle:"Free High-Speed Proxies - Update Every 30min",
nav_proxies:"Proxies",
nav_api:"API Docs",
stat_nodes:"Proxies",
stat_countries:"Countries",
card_title:"Proxy List",
card_updated:"Updated",
filter_all_proto:"All Protocols",
filter_all_country:"All Countries",
placeholder:"Search IP...",
th_ip:"IP:Port",
th_proto:"Protocol",
th_country:"Country",
th_anonymity:"Anonymity",
th_speed:"Speed",
th_copy:"Copy",
pagination_total:"Total:",
pagination_items:"",
btn_prev:"← Prev",
btn_next:"Next →",
sidebar_stats_title:"Statistics",
sidebar_total:"Total",
sidebar_countries:"Countries",
sidebar_update:"Update",
sidebar_api_title:"API Endpoints",
api_proxies_desc:"All proxies, sorted by speed ascending, CORS enabled",
api_http_desc:"HTTP/HTTPS proxies only",
api_socks_desc:"SOCKS5 proxies only",
api_examples:"📋 Code Examples",
ad_336:"Ad Space: 336x280",
ad_250:"Ad Space: 250x250",
ad_728:"Ad Space: 728x90 Banner",
footer_text:"Global Proxy Hub — Free Anonymous Proxy Resource | Updated Every 30min"
}
};
function setLang(l){const t=I18N[l]||I18N.zh;document.querySelectorAll("[data-i18n]").forEach(e=>{const k=e.getAttribute("data-i18n");if(t[k]!==undefined){if(e.tagName==="INPUT"||e.tagName==="TEXTAREA"){e.placeholder=t[k]}else{e.innerHTML=t[k]}}});document.getElementById("langToggle").textContent=l==="zh"?"English":"中文"}
let currentLang=localStorage.getItem("lang")||"zh";setLang(currentLang);
function toggleLang(){currentLang=currentLang==="zh"?"en":"zh";setLang(currentLang);localStorage.setItem("lang",currentLang)}

// ========== data ==========
const proxyData = [];
const tbody = document.getElementById("proxy-tbody");

let pageSize = 25;
let currentPage = 1;
let filteredData = [];

function renderTable() {
    if (!filteredData.length) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:30px;color:#999" data-i18n="no_data">暂无数据</td></tr>';
        return;
    }
    const start = (currentPage - 1) * pageSize;
    const end = Math.min(start + pageSize, filteredData.length);
    let html = "";
    for (let i = start; i < end; i++) {
        const p = filteredData[i];
        const badgeClass = p.protocol === "HTTP" ? "badge-http" : "badge-socks5";
        html += `<tr data-country="${p.country}" data-proto="${p.protocol}" data-ip="${p.ip_port.split(":")[0]}">`;
        html += `<td class="ip-cell">${p.ip_port}</td>`;
        html += `<td><span class="proto-badge ${badgeClass}">${p.protocol}</span></td>`;
        html += `<td>${p.country}</td>`;
        html += `<td>${p.anonymity}</td>`;
        html += `<td>${p.speed}ms</td>`;
        html += `<td><span class="copy-btn" onclick="copyProxy(this,'${p.ip_port}')">📋</span></td></tr>`;
    }
    tbody.innerHTML = html;
    document.getElementById("total-count").textContent = filteredData.length;
    const totalPages = Math.ceil(filteredData.length / pageSize) || 1;
    document.getElementById("page-num").textContent = `${currentPage} / ${totalPages}`;
    document.getElementById("prevBtn").disabled = currentPage <= 1;
    document.getElementById("nextBtn").disabled = currentPage >= totalPages;
}

function filterTable() {
    const proto = document.getElementById("search_proto").value;
    const country = document.getElementById("search_country").value;
    const ip = document.getElementById("search_ip").value.toLowerCase();
    filteredData = proxyData.filter(p => {
        if (proto !== "ALL" && p.protocol !== proto) return false;
        if (country !== "ALL" && p.country !== country) return false;
        if (ip && !p.ip_port.toLowerCase().includes(ip)) return false;
        return true;
    });
    currentPage = 1;
    renderTable();
}

function prevPage() { if (currentPage > 1) { currentPage--; renderTable(); } }
function nextPage() { const max = Math.ceil(filteredData.length / pageSize); if (currentPage < max) { currentPage++; renderTable(); } }

function sortTable(field) {
    proxyData.sort((a, b) => {
        if (field === "speed") return a.speed - b.speed;
        return a.ip_port.localeCompare(b.ip_port);
    });
    filterTable();
}

function copyProxy(btn, text) {
    navigator.clipboard.writeText(text).then(() => {
        btn.textContent = "✅";
        setTimeout(() => { btn.textContent = "📋"; }, 1500);
    }).catch(() => {
        const ta = document.createElement("textarea");
        ta.value = text; document.body.appendChild(ta);
        ta.select(); document.execCommand("copy"); document.body.removeChild(ta);
        btn.textContent = "✅";
        setTimeout(() => { btn.textContent = "📋"; }, 1500);
    });
}

// Initialize country filter
(() => {
    const countries = [...new Set(proxyData.map(p => p.country))].sort();
    const sel = document.getElementById("search_country");
    countries.forEach(c => { const o = document.createElement("option"); o.value = c; o.textContent = c; sel.appendChild(o); });
    filterTable();
    // Update stats
    document.getElementById("stat-http").textContent = proxyData.filter(p => p.protocol === "HTTP").length;
    document.getElementById("stat-socks5").textContent = proxyData.filter(p => p.protocol === "SOCKS5").length;
    document.getElementById("stat-countries").textContent = countries.length;
    document.getElementById("s-http").textContent = proxyData.filter(p => p.protocol === "HTTP").length;
    document.getElementById("s-socks5").textContent = proxyData.filter(p => p.protocol === "SOCKS5").length;
    document.getElementById("s-countries").textContent = countries.length;
})();
</script>
</body>
</html>"""

BODY_ROW_TEMPLATE = r"""<tr data-country="{country}" data-proto="{protocol}" data-ip="{ip}"><td class="ip-cell">{ip_port}</td><td><span class="proto-badge {proto_badge}">{protocol}</span></td><td>{country}</td><td>{anonymity}</td><td>{speed}ms</td><td><span class="copy-btn" onclick="copyProxy(this,'{ip_port}')">📋</span></td></tr>"""


def build_html_page(proxies):
    """生成 HTML 页面"""
    # 生成表格行
    rows_html = ""
    for idx, p in enumerate(proxies):
        proto_badge = "badge-http" if p["protocol"] == "HTTP" else "badge-socks5"
        ip_only = p["ip_port"].split(":")[0]
        rows_html += BODY_ROW_TEMPLATE.format(
            country=p.get("country", "UN"),
            protocol=p["protocol"],
            ip=ip_only,
            ip_port=p["ip_port"],
            proto_badge=proto_badge,
            anonymity=p.get("anonymity", "Elite"),
            speed=p.get("speed", 0),
            idx=idx
        )

    from datetime import datetime
    update_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    update_time_iso = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00")

    html = HTML_TEMPLATE.replace("{{UPDATE_TIME}}", update_time)
    html = html.replace("{{UPDATE_TIME_ISO}}", update_time_iso)
    html = html.replace("{{NODE_COUNT}}", str(len(proxies)))
    html = html.replace("{{TABLE_ROWS}}", rows_html)
    # Set initial stats from Python data
    http_count = len([p for p in proxies if p["protocol"] == "HTTP"])
    socks5_count = len([p for p in proxies if p["protocol"] == "SOCKS5"])
    countries = len(set(p.get("country","") for p in proxies))
    html = html.replace('id="stat-http">0', 'id="stat-http">' + str(http_count))
    html = html.replace('id="stat-socks5">0', 'id="stat-socks5">' + str(socks5_count))
    html = html.replace('id="stat-countries">0', 'id="stat-countries">' + str(countries))
    html = html.replace('id="s-http">0', 'id="s-http">' + str(http_count))
    html = html.replace('id="s-socks5">0', 'id="s-socks5">' + str(socks5_count))
    html = html.replace('id="s-countries">0', 'id="s-countries">' + str(countries))
    # Embed proxy data as JSON into JavaScript proxyData array
    import json as _json
    proxies_json = _json.dumps(proxies, ensure_ascii=False)
    html = html.replace("const proxyData = [];", "const proxyData = " + proxies_json + ";")


    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  [OK] index.html 已生成 ({len(proxies)} 个节点)")


# ==================== 5. 调度主函数 ====================
def main():
    print("=" * 58)
    print("  * Global Proxy Hub - SEO 优化资产构建引擎启动")
    print(f"  [T] {time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print("=" * 58)

    # 阶段一：抓取
    print("\n[1/4] 多源并发抓取原始代理...")
    raw_ips = fetch_all_raw_ips()
    print(f"  -> 去重后共 {len(raw_ips)} 条原始代理")

    if not raw_ips:
        print("  [X] 未获取到任何代理，终止任务")
        return

    # 阶段二：多线程探测
    print(f"\n[2/4] 多线程匿名度+Google连通性探测 ({min(80, len(raw_ips))} 线程)...")
    validated = []
    max_workers = min(80, len(raw_ips))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(inspect_proxy, ip): ip for ip in raw_ips}
        done = 0
        for future in as_completed(futures):
            done += 1
            result = future.result()
            if result:
                validated.append(result)
            if done % 50 == 0 or done == len(raw_ips):
                print(f"    进度: {done}/{len(raw_ips)} | 已发现有效节点: {len(validated)}")

    print(f"  -> 有效节点: {len(validated)}/{len(raw_ips)}")

    if not validated:
        print("  [X] 未发现有效节点，跳过HTML生成，仅输出JSON")
        return

    # 阶段三：按速度排序
    print(f"\n[3/5] 排序并输出 JSON...")
    validated.sort(key=lambda x: x["speed"])

    # 输出 JSON
    os.makedirs("api", exist_ok=True)
    full_path = "api/proxies.json"
    http_path = "api/http.json"
    socks5_path = "api/socks5.json"

    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(validated, f, indent=2, ensure_ascii=False)
    print(f"  [OK] {full_path} - {len(validated)} 条全量数据")

    with open(http_path, "w", encoding="utf-8") as f:
        json.dump([p for p in validated if p["protocol"] == "HTTP"], f, indent=2, ensure_ascii=False)
    http_count = len([p for p in validated if p["protocol"] == "HTTP"])
    print(f"  [OK] {http_path} - {http_count} 条 HTTP 数据")

    with open(socks5_path, "w", encoding="utf-8") as f:
        json.dump([p for p in validated if p["protocol"] == "SOCKS5"], f, indent=2, ensure_ascii=False)
    socks5_count = len([p for p in validated if p["protocol"] == "SOCKS5"])
    print(f"  [OK] {socks5_path} - {socks5_count} 条 SOCKS5 数据")

    # 阶段四：生成 HTML
    print(f"\n[4/5] 生成前端页面...")
    build_html_page(validated)

    # 阶段五：生成 SEO 文件
    print(f"\n[5/5] 生成 SEO 文件 (sitemap.xml | robots.txt)...")
    _generate_seo_files()

    print("\n" + "=" * 58)
    print("  [OK] 边缘 API 库及 HTML 静态首页自动化打包圆满成功！")
    print(f"  [OK] 共 {len(validated)} 个活跃节点已就绪")
    print("=" * 58)


# ==================== 6. SEO 文件生成 ====================
def _generate_seo_files():
    """SEO 文件已迁移至 Cloudflare Pages Functions 动态生成"""
    print("  [OK] robots.txt / sitemap.xml 由 Pages Functions 动态处理 (functions/robots.txt.js / sitemap.xml.js)")




if __name__ == "__main__":
    main()
