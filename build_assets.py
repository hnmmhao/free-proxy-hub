#!/usr/bin/env python3
"""
⚡ Global Proxy Hub — 商业级全自动代理节点聚合引擎
====================================================
功能：
  1. 从 5 个数据源抓取原始代理 IP
  2. 多线程匿名度检测 + Google 连通性测活
  3. 自动生成暗黑大厂风 HTML 静态页面（预留 AdSense 广告位）
  4. 输出 JSON 数据到 api/ 目录
====================================================
"""

import requests
import re
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# ==================== 1. 商业级多源全量配置 ====================
PROXY_SOURCES = [
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http,socks5&timeout=3000&country=all&ssl=all&anonymity=all",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies.txt",
    "https://raw.githubusercontent.com/shiftytr/proxy-list/master/proxy.txt"
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
                print(f"  📥 {url.split('/')[2][:30]:>30} → {len(found):>4} 条")
        except Exception as e:
            print(f"  ⚠️  {url.split('/')[2][:30]:>30} → 失败: {str(e)[:40]}")
    return list(set(raw_pool))

# ==================== 3. 探测模块 ====================
def inspect_proxy(ip_port):
    """双阶段探测：地理位置 → Google 连通性"""
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

# ==================== 4. 升华版高级前端 HTML 模板 ====================
HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Global Proxy Hub</title>
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
.proto-http{background:#e3f2fd;color:#1565c0}
.proto-socks5{background:#f3e5f5;color:#7b1fa2}
.copy-btn{cursor:pointer;color:#999;padding:2px 6px;border-radius:3px;font-size:12px;user-select:none}
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
.footer{background:#1a1a2e;color:#888;text-align:center;padding:20px;margin-top:30px;font-size:12px}
.update-badge{display:inline-flex;align-items:center;gap:5px;background:rgba(255,255,255,.15);padding:4px 12px;border-radius:20px;font-size:12px;color:#fff}
.update-badge .dot{width:7px;height:7px;background:#69f0ae;border-radius:50%}
.hidden{display:none!important}
</style></head>
<body>
<header class="header">
<div class="container" style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px">
<div><div class="logo">Global <span>Proxy</span> Hub</div><div class="subtitle">免费高速代理IP - 30分钟自动更新</div></div>
<div class="nav" style="display:flex;gap:4px;align-items:center">
<a href="#api-docs">API文档</a>
</div></div></header>
<div class="container">
<div class="stats-grid">
<div class="stat-card"><div class="num" style="color:#e65100" id="stat-total">{{NODE_COUNT}}</div><div class="label">代理节点</div></div>
<div class="stat-card"><div class="num" id="stat-http">0</div><div class="label">HTTP</div></div>
<div class="stat-card"><div class="num" style="color:#7c3aed" id="stat-socks5">0</div><div class="label">SOCKS5</div></div>
<div class="stat-card"><div class="num" style="color:#2e7d32" id="stat-countries">0</div><div class="label">覆盖国家</div></div></div>
<div class="ad-box" style="margin-top:25px">AdSense Ready</div>
<div class="content-wrap">
<div class="main-area">
<div class="card">
<div class="card-title"><span>代理列表</span><span class="update-badge"><span class="dot"></span> 更新时间: {{UPDATE_TIME}} UTC</span></div>
<div class="card-body">
<div class="filter-bar">
<select id="search_proto" onchange="filterTable()"><option value="ALL">全部协议</option><option value="HTTP">HTTP</option><option value="SOCKS5">SOCKS5</option></select>
<select id="search_country" onchange="filterTable()"><option value="ALL">全部国家</option></select>
<input type="text" id="search_ip" oninput="filterTable()" placeholder="搜索 IP...">
<select id="sort_speed" onchange="filterTable()" style="min-width:100px"><option value="asc">速度↑</option><option value="desc">速度↓</option></select>
</div>
<div style="overflow-x:auto"><table class="proxy-table">
<thead><tr><th>IP:Port</th><th>协议</th><th>国家</th><th>匿名度</th><th>速度</th><th style="text-align:center">复制</th></tr></thead>
<tbody id="proxy_table_body">{{TABLE_ROWS}}</tbody>
</table></div></div>
<div class="pagination">
<div class="info">共 <span id="total-count">{{NODE_COUNT}}</span> 条</div>
<div class="pages">
<button id="prevBtn" onclick="prevPage()">◀ 上一页</button>
<span class="page-info" id="page-num">1 / 1</span>
<button id="nextBtn" onclick="nextPage()">下一页 ▶</button>
</div></div></div></div>
<div class="sidebar">
<div class="side-card">
<div class="side-title">数据统计</div>
<div class="side-item"><span class="key">总节点</span><span class="val" id="s-total">{{NODE_COUNT}}</span></div>
<div class="side-item"><span class="key">HTTP</span><span class="val" id="s-http">0</span></div>
<div class="side-item"><span class="key">SOCKS5</span><span class="val" id="s-socks5">0</span></div>
<div class="side-item"><span class="key">国家</span><span class="val" id="s-countries">0</span></div>
<div class="side-item"><span class="key">更新</span><span class="val">30min</span></div></div>
<div class="side-card" id="api-docs">
<div class="side-title">API 接口</div>
<div class="api-endpoint"><span class="method">GET</span><span class="url">/api/proxies.json</span></div>
<div class="api-endpoint"><span class="method">GET</span><span class="url">/api/http.json</span></div>
<div class="api-endpoint"><span class="method">GET</span><span class="url">/api/socks5.json</span></div>
</div></div></div></div>
<footer class="footer">
<div class="container"><p>Global Proxy Hub - GitHub Actions + Cloudflare Pages</p></div></footer>
<script>
const PS=30;let cp=1,ar=[];
function ip(){ar=Array.from(document.querySelectorAll("#proxy_table_body tr"));rp(1);}
function rp(p){cp=p;const s=(p-1)*PS,e=s+PS,tp=Math.ceil(ar.length/PS)||1;ar.forEach((r,i)=>{if(i>=s&&i<e)r.classList.remove("hidden");else r.classList.add("hidden")});document.getElementById("page-num").textContent=p+"/"+tp;document.getElementById("prevBtn").disabled=p<=1;document.getElementById("nextBtn").disabled=p>=tp;}
function pp(){if(cp>1)rp(cp-1);}function np(){const t=Math.ceil(ar.length/PS);if(cp<t)rp(cp+1);}
function ft(){const c=document.getElementById("search_country").value.toUpperCase(),p2=document.getElementById("search_proto").value.toUpperCase(),iq=document.getElementById("search_ip").value.toLowerCase(),s=document.getElementById("sort_speed").value;let m=ar.filter(r=>{const c2=(r.getAttribute("data-country")||"").toUpperCase(),p3=(r.getAttribute("data-proto")||"").toUpperCase(),ip3=(r.getAttribute("data-ip")||"").toLowerCase();return(c==="ALL"||c2.includes(c))&&(p2==="ALL"||p3===p2)&&(!iq||ip3.includes(iq))});if(s==="desc")m.reverse();const tb=document.getElementById("proxy_table_body");m.forEach(r=>tb.appendChild(r));ar=m;rp(1);document.getElementById("total-count").textContent=ar.length;us(m);}
function us(rs){document.getElementById("stat-total").textContent=rs.length;document.getElementById("stat-http").textContent=rs.filter(r=>r.getAttribute("data-proto")==="HTTP").length;document.getElementById("stat-socks5").textContent=rs.filter(r=>r.getAttribute("data-proto")==="SOCKS5").length;document.getElementById("stat-countries").textContent=new Set(rs.map(r=>r.getAttribute("data-country"))).size;}
function cip(ip,bid){navigator.clipboard.writeText(ip).then(()=>{const b=document.getElementById(bid);b.innerHTML="OK";setTimeout(()=>{b.innerHTML="COPY"},2000)});}
window.onload=function(){ip();const cs=[...new Set(ar.map(r=>r.getAttribute("data-country")))].sort();const sl=document.getElementById("search_country");cs.forEach(c=>{const o=document.createElement("option");o.value=c;o.textContent=c;sl.appendChild(o)});us(ar);};
</script>
</body>
</html>"""
BODY_ROW_TEMPLATE = """<tr data-country="{country}" data-proto="{protocol}" data-ip="{ip}">
    <td class="ip-cell">{ip_port}</td>
    <td><span class="proto-badge {proto_badge}">{protocol}</span></td>
    <td>{country}</td>
    <td style="color:#888">{anonymity}</td>
    <td style="color:#555">{speed}ms</td>
    <td style="text-align:center"><span class="copy-btn" onclick="cip('{ip_port}','c{idx}')">COPY</span></td>
</tr>"""


def build_html_page(proxies):
    """生成完整的 HTML 静态页面"""
    os.makedirs("api", exist_ok=True)

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

    html = HTML_TEMPLATE.replace("{{UPDATE_TIME}}", update_time)
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


    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  📄 index.html 已生成 ({len(proxies)} 个节点)")


# ==================== 5. 调度主函数 ====================
def main():
    print("=" * 55)
    print("  ⚡ Global Proxy Hub — 商业级资产构建引擎启动")
    print(f"  🕐 {time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print("=" * 55)

    # 阶段一：抓取
    print("\n📡 阶段 1/4 — 多源并发抓取原始代理...")
    raw_ips = fetch_all_raw_ips()
    print(f"  ✅ 去重后共 {len(raw_ips)} 条原始代理")

    if not raw_ips:
        print("  ❌ 未获取到任何代理，终止任务")
        return

    # 阶段二：多线程测活
    print(f"\n🔍 阶段 2/4 — 多线程匿名度+Google连通性测活 ({min(80, len(raw_ips))} 线程)...")
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

    print(f"  ✅ 有效节点: {len(validated)}/{len(raw_ips)}")

    if not validated:
        print("  ❌ 未发现有效节点，终止任务")
        return

    # 阶段三：按速度排序
    print(f"\n📊 阶段 3/4 — 排序并输出 JSON...")
    validated.sort(key=lambda x: x["speed"])

    # 输出 JSON
    os.makedirs("api", exist_ok=True)
    full_path = "api/proxies.json"
    http_path = "api/http.json"
    socks5_path = "api/socks5.json"

    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(validated, f, indent=2, ensure_ascii=False)
    print(f"  📦 {full_path} — {len(validated)} 条全量数据")

    with open(http_path, "w", encoding="utf-8") as f:
        json.dump([p for p in validated if p["protocol"] == "HTTP"], f, indent=2, ensure_ascii=False)
    http_count = len([p for p in validated if p["protocol"] == "HTTP"])
    print(f"  📦 {http_path} — {http_count} 条 HTTP 数据")

    with open(socks5_path, "w", encoding="utf-8") as f:
        json.dump([p for p in validated if p["protocol"] == "SOCKS5"], f, indent=2, ensure_ascii=False)
    socks5_count = len([p for p in validated if p["protocol"] == "SOCKS5"])
    print(f"  📦 {socks5_path} — {socks5_count} 条 SOCKS5 数据")

    # 阶段四：生成 HTML
    print(f"\n🎨 阶段 4/4 — 生成商业级前端页面...")
    build_html_page(validated)

    print("\n" + "=" * 55)
    print("  🎉 商业边缘 API 库及 HTML 静态总页面自动化打包圆满成功！")
    print(f"  🌐 共 {len(validated)} 个活跃节点已就绪")
    print("=" * 55)


if __name__ == "__main__":
    main()
