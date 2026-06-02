// fb_job_scraper.js — Scrape FB groups for JB restaurant/chef job listings
// RAW DATA IS APPEND-ONLY — never delete fb_jobs_raw.json
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const COOKIES = [
  { name: 'c_user', value: '100000390330536', domain: '.facebook.com', path: '/' },
  { name: 'xs', value: '22%3ABP076DDNtD7PnQ%3A2%3A1773550824%3A-1%3A-1%3A%3AAcw-mSgGoEFZAI_4rPrQWnZdsDrepQ1MED6H7hony9w', domain: '.facebook.com', path: '/' },
  { name: 'fr', value: '11lkkMhtF2En5XJeD.AWeKxawEKCkeI_s_RFZZDjCg3hFSAcCmvKx2epfkf63Jt-qXC_U.BqAmQE..AAA.0.0.BqAmQE.AWcmtemPt2EE7myVwQ5QLmlSAr0', domain: '.facebook.com', path: '/' },
  { name: 'presence', value: 'C%7B%22t3%22%3A%5B%5D%2C%22utc3%22%3A1778541574416%2C%22v%22%3A1%7D', domain: '.facebook.com', path: '/' },
];

const GROUPS = [
  { id: '1876719386899909', name: 'Chef-Tukang Masak Restoran JB' },
  { id: '1160503301973340', name: 'Jawatan Kosong Restoran JB' },
  { id: '1605936663645487', name: 'Kerja Kosong Hotel JB' },
  { id: '226649657954297', name: 'JAWATAN KOSONG JOHOR BHARU' },
  { id: '1736634896581390', name: 'Jobs Johor Bahru JJB' },
  { id: '322574771134969', name: 'Job Vacancies Johor' },
  { id: '352849686871274', name: 'Job Vacancy Johor Bahru' },
  { id: '299562313742588', name: 'JB Johor Part Full Time Jobs' },
];

const RAW_FILE = '/home/user/jbkitchen/data/fb_jobs_raw.json';
const LOG_DIR = '/home/user/jbkitchen/.logs';

const FOOD_KW = [
  'chef', 'cook', 'kitchen', 'restaurant', 'tukang masak', 'pembantu dapur',
  'commis', 'demi', 'sous', 'pastry', 'baker', 'bakery', 'culinary',
  'food', 'fb', 'f&b', 'cafe', 'kafe', 'kopitiam', 'makanan', 'dapur',
  'hotel', 'catering', 'kitchen crew', 'line cook', 'head chef',
  'barista', 'service crew', 'waiter', 'waitress', 'captain',
  'masak', 'grill', 'roti', 'kek', 'cake',
];

function log(msg) {
  const ts = new Date().toISOString();
  fs.mkdirSync(LOG_DIR, { recursive: true });
  fs.appendFileSync(path.join(LOG_DIR, 'fb_job_scraper.log'), `[${ts}] ${msg}\n`);
  console.log(`[${ts}] ${msg}`);
}

/** Load existing raw posts for dedup by link */
function loadExisting() {
  try {
    if (fs.existsSync(RAW_FILE)) {
      return JSON.parse(fs.readFileSync(RAW_FILE, 'utf-8'));
    }
  } catch (e) {
    log(`读取现有数据失败: ${e.message}`);
  }
  return [];
}

async function scrapeGroup(group) {
  log(`[${group.name}] 开始`);
  let browser = null;
  let posts = [];

  try {
    browser = await chromium.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
    });
    const context = await browser.newContext({
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
      locale: 'ms-MY',
      viewport: { width: 1280, height: 720 },
    });
    await context.addCookies(COOKIES);
    const page = await context.newPage();

    await page.goto(`https://www.facebook.com/groups/${group.id}`, {
      waitUntil: 'domcontentloaded',
      timeout: 25000,
    });
    await page.waitForTimeout(4000);

    for (let i = 0; i < 6; i++) {
      await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
      await page.waitForTimeout(1500);
    }

    posts = await page.evaluate((gid) => {
      const articles = document.querySelectorAll('[role="article"]');
      const results = [];
      for (const article of articles) {
        const text = (article.textContent || '').trim();
        if (text.length < 50) continue;

        let postLink = '';
        for (const link of article.querySelectorAll('a')) {
          const href = link.href || '';
          const pm = href.match(/\/(posts|permalink)\/(\d{6,})/);
          if (pm) { postLink = `https://www.facebook.com/groups/${gid}/posts/${pm[2]}`; break; }
        }
        if (!postLink) {
          for (const link of article.querySelectorAll('a')) {
            const pm = (link.href || '').match(/\/posts\/(\d+)/);
            if (pm) { postLink = `https://www.facebook.com/groups/${gid}/posts/${pm[1]}`; break; }
          }
        }

        results.push({ text: text.substring(0, 3000), link: postLink });
      }
      return results;
    }, group.id);

    log(`[${group.name}] ${posts.length} 条`);
    await page.close();
    await context.close();
  } catch (e) {
    log(`[${group.name}] 错误: ${e.message.substring(0, 100)}`);
  } finally {
    if (browser) await browser.close();
  }

  return posts.map(p => ({
    group_id: group.id,
    group_name: group.name,
    text: p.text,
    link: p.link,
    scraped_at: new Date().toISOString(),
  }));
}

(async () => {
  log('FB Job Scraper 启动');
  fs.mkdirSync(path.dirname(RAW_FILE), { recursive: true });

  // Load existing data for dedup (append-only: NEVER delete raw data)
  const existing = loadExisting();
  const seenLinks = new Set(existing.map(p => p.link).filter(Boolean));
  log(`现有数据: ${existing.length} 条`);

  let newPosts = [];
  for (const group of GROUPS) {
    const posts = await scrapeGroup(group);
    const relevant = posts.filter(p =>
      FOOD_KW.some(kw => p.text.toLowerCase().includes(kw))
    );

    // Dedup vs existing
    const fresh = relevant.filter(p => !seenLinks.has(p.link));
    newPosts.push(...fresh);

    // Add new links to seen set for subsequent groups
    fresh.forEach(p => { if (p.link) seenLinks.add(p.link); });
    log(`  → 相关: ${relevant.length}/${posts.length}, 新增: ${fresh.length}`);
  }

  // APPEND to existing data (NEVER delete raw data)
  const allPosts = existing.concat(newPosts);
  fs.writeFileSync(RAW_FILE, JSON.stringify(allPosts, null, 2));

  // Also write a timestamped snapshot for history
  const dateStr = new Date().toISOString().slice(0, 10);
  const snapshotFile = RAW_FILE.replace('.json', `_${dateStr}.json`);
  if (!fs.existsSync(snapshotFile)) {
    fs.writeFileSync(snapshotFile, JSON.stringify(allPosts, null, 2));
    log(`快照: ${snapshotFile}`);
  }

  log(`\n完成: 现有 ${existing.length} + 新增 ${newPosts.length} = ${allPosts.length} 条`);
  console.log(`输出: ${RAW_FILE} (${allPosts.length} 条)`);
})();
