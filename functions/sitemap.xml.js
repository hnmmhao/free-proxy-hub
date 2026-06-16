export async function onRequest(context) {
  const url = new URL(context.request.url);
  const host = url.hostname;
  const protocol = url.protocol;
  const base = protocol + '//' + host;

  const today = new Date().toISOString().split('T')[0];

  const content = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <url>
    <loc>${base}/</loc>
    <lastmod>${today}</lastmod>
    <changefreq>hourly</changefreq>
    <priority>1.0</priority>
    <xhtml:link rel="alternate" hreflang="zh-CN" href="${base}/"/>
    <xhtml:link rel="alternate" hreflang="en" href="${base}/?lang=en"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="${base}/"/>
  </url>
  <url>
    <loc>${base}/api/proxies.json</loc>
    <lastmod>${today}</lastmod>
    <changefreq>hourly</changefreq>
    <priority>0.6</priority>
  </url>
</urlset>`;

  return new Response(content, {
    headers: {
      'Content-Type': 'application/xml; charset=utf-8',
      'Cache-Control': 'public, max-age=3600'
    }
  });
}
