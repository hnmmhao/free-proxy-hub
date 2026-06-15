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
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚡ GLOBAL PROXY HUB - High Performance Free Proxy Directory</title>
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    <style>
        :root { color-scheme: dark; }
        body { background: #0a0a0f; color: #e2e8f0; font-family: 'Inter', system-ui, -apple-system, sans-serif; }
        .glass-card { background: rgba(15,15,25,0.8); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.06); }
        .glow { box-shadow: 0 0 40px rgba(59,130,246,0.08); }
        .proxy-row:hover { background: rgba(59,130,246,0.08); }
        .badge { padding: 2px 10px; border-radius: 999px; font-size: 0.7rem; font-weight: 600; letter-spacing: 0.3px; }
        .badge-http { background: rgba(59,130,246,0.2); color: #60a5fa; }
        .badge-socks5 { background: rgba(168,85,247,0.2); color: #c084fc; }
        .badge-speed { background: rgba(34,197,94,0.15); color: #4ade80; }
        .ad-container { background: rgba(255,255,255,0.02); border: 1px dashed rgba(255,255,255,0.08); border-radius: 8px; padding: 16px; text-align: center; margin: 20px 0; min-height: 90px; display: flex; align-items: center; justify-content: center; }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
        .animate-pulse-slow { animation: pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        select, input { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 8px 14px; color: #e2e8f0; outline: none; transition: all 0.2s; }
        select:focus, input:focus { border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,0.15); }
    </style>
</head>
<body>
    <div class="max-w-7xl mx-auto px-4 py-6">
        <!-- Header -->
        <header class="text-center mb-8">
            <h1 class="text-4xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-emerald-400 bg-clip-text text-transparent">⚡ Global Proxy Hub</h1>
            <p class="text-gray-500 mt-2 text-sm">Free High-Performance Proxy Directory · Updated Every 30 Minutes</p>
            <div class="flex items-center justify-center gap-2 mt-3 text-xs text-gray-600">
                <span class="inline-block w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                <span>Last Updated: <span id="update-time">{{UPDATE_TIME}}</span> UTC</span>
                <span class="mx-2">·</span>
                <span><a href="#api-docs" class="text-gray-500 hover:text-blue-400 transition-colors text-xs">🔌 API 文档</a></span>
                <span class="mx-2">·</span>
                <span>Nodes: <span id="node-count" class="text-emerald-400 font-mono">{{NODE_COUNT}}</span></span>
            </div>
        </header>

        <!-- Filters -->
        <div class="glass-card rounded-xl p-4 mb-6 glow">
            <div class="flex flex-wrap gap-4 items-center">
                <div class="flex-1 min-w-[160px]">
                    <label class="text-xs text-gray-500 block mb-1">🌍 Country</label>
                    <select id="search_country" onchange="filterTable()" class="w-full text-sm">
                        <option value="ALL">🌐 All Countries</option>
                    </select>
                </div>
                <div class="flex-1 min-w-[140px]">
                    <label class="text-xs text-gray-500 block mb-1">🔌 Protocol</label>
                    <select id="search_proto" onchange="filterTable()" class="w-full text-sm">
                        <option value="ALL">All Protocols</option>
                        <option value="HTTP">HTTP</option>
                        <option value="SOCKS5">SOCKS5</option>
                    </select>
                </div>
                <div class="flex-1 min-w-[160px]">
                    <label class="text-xs text-gray-500 block mb-1">🔍 Search IP</label>
                    <input type="text" id="search_ip" oninput="filterTable()" placeholder="e.g. 123.45..." class="w-full text-sm">
                </div>
                <div class="text-xs text-gray-500">
                    <span id="visible-count">0</span> / <span id="total-count">{{NODE_COUNT}}</span> rows
                </div>
            </div>

        <!-- API Documentation -->
        <div class="glass-card rounded-xl p-6 mt-6 glow" id="api-docs">
            <h2 class="text-xl font-semibold text-white mb-4">🔌 RESTful API 接口文档</h2>
            <p class="text-gray-400 text-sm mb-5">所有接口返回 JSON 格式数据，支持跨域（CORS），可直接在前端或后端调用。</p>
            <div class="grid gap-4 md:grid-cols-3">
                <div class="bg-white/[0.03] rounded-lg p-4 border border-white/5">
                    <div class="flex items-center gap-2 mb-3">
                        <span class="text-xs font-mono bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded">GET</span>
                        <code class="text-xs text-blue-400 font-mono truncate">/api/proxies.json</code>
                    </div>
                    <p class="text-gray-500 text-xs mb-2">全量代理数据，按速度升序排列</p>
                    <button onclick="copyText(window.location.origin + '/api/proxies.json', 'cp1')" id="cp1" class="text-xs text-gray-600 hover:text-white transition-colors">📋 复制 URL</button>
                </div>
                <div class="bg-white/[0.03] rounded-lg p-4 border border-white/5">
                    <div class="flex items-center gap-2 mb-3">
                        <span class="text-xs font-mono bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded">GET</span>
                        <code class="text-xs text-blue-400 font-mono truncate">/api/http.json</code>
                    </div>
                    <p class="text-gray-500 text-xs mb-2">仅 HTTP 协议代理</p>
                    <button onclick="copyText(window.location.origin + '/api/http.json', 'cp2')" id="cp2" class="text-xs text-gray-600 hover:text-white transition-colors">📋 复制 URL</button>
                </div>
                <div class="bg-white/[0.03] rounded-lg p-4 border border-white/5">
                    <div class="flex items-center gap-2 mb-3">
                        <span class="text-xs font-mono bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded">GET</span>
                        <code class="text-xs text-blue-400 font-mono truncate">/api/socks5.json</code>
                    </div>
                    <p class="text-gray-500 text-xs mb-2">仅 SOCKS5 协议代理</p>
                    <button onclick="copyText(window.location.origin + '/api/socks5.json', 'cp3')" id="cp3" class="text-xs text-gray-600 hover:text-white transition-colors">📋 复制 URL</button>
                </div>
            </div>
            <h3 class="text-sm font-semibold text-gray-300 mt-6 mb-3">📖 调用示例</h3>
            <div class="grid gap-3 md:grid-cols-3">
                <div class="bg-black/40 rounded-lg p-3">
                    <div class="text-xs text-gray-500 mb-2">cURL</div>
                    <pre class="text-xs text-gray-300 font-mono leading-relaxed whitespace-pre-wrap">curl -s https://free-proxy-hub.pages.dev/api/proxies.json | jq</pre>
                    <button onclick="copyText('curl -s https://free-proxy-hub.pages.dev/api/proxies.json | jq', 'cp4')" id="cp4" class="text-xs text-gray-600 hover:text-white transition-colors mt-2">📋 复制</button>
                </div>
                <div class="bg-black/40 rounded-lg p-3">
                    <div class="text-xs text-gray-500 mb-2">Python</div>
                    <pre class="text-xs text-gray-300 font-mono leading-relaxed whitespace-pre-wrap">import requests
data = requests.get("https://free-proxy-hub.pages.dev/api/proxies.json").json()
for p in data[:5]: print(p["ip_port"])</pre>
                    <button onclick='copyText("import requests\ndata = requests.get(\"https://free-proxy-hub.pages.dev/api/proxies.json\").json()\nfor p in data[:5]: print(p[\"ip_port\"])", "cp5")' id="cp5" class="text-xs text-gray-600 hover:text-white transition-colors mt-2">📋 复制</button>
                </div>
                <div class="bg-black/40 rounded-lg p-3">
                    <div class="text-xs text-gray-500 mb-2">JavaScript</div>
                    <pre class="text-xs text-gray-300 font-mono leading-relaxed whitespace-pre-wrap">fetch("https://free-proxy-hub.pages.dev/api/proxies.json")
  .then(r => r.json())
  .then(data => console.log(data))</pre>
                    <button onclick='copyText("fetch(\"https://free-proxy-hub.pages.dev/api/proxies.json\").then(r => r.json()).then(data => console.log(data))", "cp6")' id="cp6" class="text-xs text-gray-600 hover:text-white transition-colors mt-2">📋 复制</button>
                </div>
            </div>
        </div>


        <!-- AdSense Slot -->
        <div class="ad-container">
            <p class="text-gray-600 text-xs">📢 Ad Space — Google AdSense Ready</p>
            <!--
                TODO: 将下方注释替换为 Google AdSense 广告代码
                <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
                <ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-xxxxxxxxxxxxxx" data-ad-slot="xxxxxxxxxx" data-ad-format="auto"></ins>
                <script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
            -->
        </div>

        <!-- Proxy Table -->
        <div class="glass-card rounded-xl overflow-hidden glow">
            <div class="overflow-x-auto">
                <table class="w-full text-sm">
                    <thead>
                        <tr class="text-gray-500 text-xs uppercase tracking-wider border-b border-white/5">
                            <th class="text-left py-3 px-4 font-medium">IP:Port</th>
                            <th class="text-left py-3 px-4 font-medium">Protocol</th>
                            <th class="text-left py-3 px-4 font-medium">Country</th>
                            <th class="text-left py-3 px-4 font-medium">Anonymity</th>
                            <th class="text-left py-3 px-4 font-medium">Speed</th>
                            <th class="text-center py-3 px-4 font-medium">Copy</th>
                        </tr>
                    </thead>
                    <tbody id="proxy_table_body">
                        {{TABLE_ROWS}}
                    </tbody>
                </table>

            <!-- Pagination -->
            <div class="flex items-center justify-between px-4 py-3 border-t border-white/5">
                <div class="text-xs text-gray-500">
                    <span id="visible-count">0</span> / <span id="total-count">{{NODE_COUNT}}</span> rows
                </div>
                <div class="flex items-center gap-2">
                    <button onclick="prevPage()" class="px-3 py-1 text-xs rounded bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white transition-colors">‹ Prev</button>
                    <span class="text-xs text-gray-500 px-2" id="page-info">1 / 1</span>
                    <button onclick="nextPage()" class="px-3 py-1 text-xs rounded bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white transition-colors">Next ›</button>
                </div>
            </div>
            </div>
        </div>

        <!-- Bottom AdSense Slot -->
        <div class="ad-container mt-4">
            <p class="text-gray-600 text-xs">📢 Ad Space — Google AdSense Ready (Bottom)</p>
        </div>

        </div>

        <!-- Footer -->
        <footer class="text-center mt-8 pb-8 text-gray-600 text-xs">
            <p>⚡ Global Proxy Hub · Powered by GitHub Actions + Cloudflare Pages</p>
            <p class="mt-1">Data collected from public sources · For educational and research purposes only</p>
        </footer>
    </div>

    <script>
        // 国家列表
        const COUNTRIES = [...new Set(Array.from(document.querySelectorAll('[data-country]')).map(el => el.getAttribute('data-country')))].sort();
        const sel = document.getElementById('search_country');
        COUNTRIES.forEach(c => { const o = document.createElement('option'); o.value = c; o.textContent = c; sel.appendChild(o); });

        function filterTable() {
            const country = document.getElementById('search_country').value.toUpperCase();
            const protocol = document.getElementById('search_proto').value.toUpperCase();
            const ipSearch = document.getElementById('search_ip').value.toLowerCase();
            const rows = document.querySelectorAll('#proxy_table_body tr');
            let visible = 0;

            rows.forEach(row => {
                const c = (row.getAttribute('data-country') || '').toUpperCase();
                const p = (row.getAttribute('data-proto') || '').toUpperCase();
                const ip = (row.getAttribute('data-ip') || '').toLowerCase();

                const cMatch = country === 'ALL' || c.includes(country);
                const pMatch = protocol === 'ALL' || p === protocol;
                const ipMatch = !ipSearch || ip.includes(ipSearch);

                if (cMatch && pMatch && ipMatch) {
                    row.classList.remove('hidden');
                    visible++;
                } else {
                    row.classList.add('hidden');
                }
            });

            document.getElementById('visible-count').textContent = visible;
        }

        function copyIp(ip, btnId) {
            navigator.clipboard.writeText(ip).then(() => {
                const btn = document.getElementById(btnId);
                const orig = btn.innerHTML;
                btn.innerHTML = '✓';
                btn.className = 'text-emerald-400 cursor-pointer text-sm';
                setTimeout(() => { btn.innerHTML = orig; btn.className = 'text-gray-500 hover:text-white cursor-pointer text-sm'; }, 2000);
            });
        }


        function copyText(text, btnId) {
            navigator.clipboard.writeText(text).then(() => {
                const btn = document.getElementById(btnId);
                const orig = btn.innerHTML;
                btn.innerHTML = '✓ Copied';
                setTimeout(() => { btn.innerHTML = orig; }, 2000);
            });
        }


        // ==================== Pagination ====================
        const PAGE_SIZE = 30;
        let currentPage = 1;
        let allRows = [];

        function initPagination() {
            allRows = Array.from(document.querySelectorAll('#proxy_table_body tr'));
            renderPage(1);
            updatePaginationControls();
        }

        function renderPage(page) {
            currentPage = page;
            const start = (page - 1) * PAGE_SIZE;
            const end = start + PAGE_SIZE;

            allRows.forEach((row, i) => {
                if (i >= start && i < end) {
                    row.classList.remove('hidden');
                } else {
                    row.classList.add('hidden');
                }
            });

            document.getElementById('page-info').textContent = 
                page + ' / ' + Math.ceil(allRows.length / PAGE_SIZE);
            document.getElementById('visible-count').textContent = 
                Math.min(end, allRows.length);
        }

        function prevPage() {
            if (currentPage > 1) renderPage(currentPage - 1);
        }

        function nextPage() {
            const total = Math.ceil(allRows.length / PAGE_SIZE);
            if (currentPage < total) renderPage(currentPage + 1);
        }

        function updatePaginationControls() {
            const total = Math.ceil(allRows.length / PAGE_SIZE);
            document.getElementById('total-pages').textContent = total;
        }

        // Override filterTable to work with pagination
        const origFilter = filterTable;
        filterTable = function() {
            origFilter();
            // Re-apply pagination to visible rows
            const visible = allRows.filter(r => !r.classList.contains('hidden'));
            const page = 1;
            visible.forEach((row, i) => {
                if (i >= PAGE_SIZE) row.classList.add('hidden');
            });
            document.getElementById('visible-count').textContent = Math.min(PAGE_SIZE, visible.length);
            document.getElementById('total-count').textContent = allRows.length;
            document.getElementById('total-pages').textContent = Math.ceil(visible.length / PAGE_SIZE) || 1;
            document.getElementById('page-info').textContent = '1 / ' + (Math.ceil(visible.length / PAGE_SIZE) || 1);
            currentPage = 1;
        };

        // 初始统计
        document.getElementById('visible-count').textContent = document.querySelectorAll('#proxy_table_body tr:not(.hidden)').length;
    </script>
</body>
</html>"""

BODY_ROW_TEMPLATE = """<tr class="proxy-row border-b border-white/5 data-row" data-country="{country}" data-proto="{protocol}" data-ip="{ip}">
    <td class="py-2.5 px-4 font-mono text-xs text-gray-300">{ip_port}</td>
    <td class="py-2.5 px-4"><span class="badge {proto_badge}">{protocol}</span></td>
    <td class="py-2.5 px-4 text-xs">{country}</td>
    <td class="py-2.5 px-4 text-xs text-gray-400">{anonymity}</td>
    <td class="py-2.5 px-4"><span class="badge badge-speed">{speed}ms</span></td>
    <td class="py-2.5 px-4 text-center">
        <span id="copy_{idx}" onclick="copyIp('{ip_port}','copy_{idx}')" class="text-gray-500 hover:text-white cursor-pointer text-sm transition-colors" title="Copy">📋</span>
    </td>
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
