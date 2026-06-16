export async function onRequest(context) {
  const url = new URL(context.request.url);
  const host = url.hostname;
  const protocol = url.protocol;
  const base = protocol + '//' + host;
  
  const content = `User-agent: *
Allow: /

Sitemap: ${base}/sitemap.xml
`;
  
  return new Response(content, {
    headers: {
      'Content-Type': 'text/plain; charset=utf-8',
      'Cache-Control': 'public, max-age=3600'
    }
  });
}
