const { chromium } = require('playwright');

async function main() {
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  const defaultContext = browser.contexts()[0];
  const page = await defaultContext.newPage();
  
  const queries = [
    'Kerja Kosong Johor Bahru',
    'Restaurant Hotel Jobs Malaysia',
    'Jawatan Kosong Restoran Johor',
    'kitchen crew Johor Bahru job',
    'chef job Johor Bahru group',
  ];
  
  const results = [];
  for (const q of queries) {
    try {
      await page.goto(`https://www.facebook.com/search/groups?q=${encodeURIComponent(q)}`, { waitUntil: 'domcontentloaded', timeout: 15000 });
      await page.waitForTimeout(3000);
      
      const groups = await page.evaluate(() => {
        const items = [];
        const links = new Set();
        
        document.querySelectorAll('a[href*="/groups/"]').forEach(a => {
          const href = a.href;
          if (href && href.match(/facebook\.com\/groups\/[^/?]+/)) {
            const groupMatch = href.match(/facebook\.com\/groups\/([^/?]+)/);
            if (groupMatch && !links.has(groupMatch[1])) {
              links.add(groupMatch[1]);
              const parent = a.closest('[role="article"]') || a.parentElement;
              const text = (parent ? parent.textContent : a.textContent) || '';
              const memberCount = text.match(/([\d,.KkMmbB]+\s*members?)/i);
              const name = a.textContent.trim() || groupMatch[1];
              items.push({
                name: name.substring(0, 80),
                id: groupMatch[1],
                members: memberCount ? memberCount[1] : '?',
                snippet: text.replace(/\s+/g, ' ').trim().substring(0, 200)
              });
            }
          }
        });
        return items;
      });
      
      results.push({ query: q, groups });
      console.log(`[${q}] Found ${groups.length} groups`);
    } catch(e) {
      results.push({ query: q, error: e.message.substring(0, 100) });
      console.log(`[${q}] Error: ${e.message.substring(0, 100)}`);
    }
  }
  
  await page.close();
  console.log('\n=== FINAL RESULTS ===');
  console.log(JSON.stringify(results, null, 2));
  await browser.close();
}

main().catch(e => console.error('FATAL:', e.message));
