// fb_job_scraper.js — Scrape FB groups for JB restaurant/chef job listings
// RAW DATA IS APPEND-ONLY — never delete fb_jobs_raw.json
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

// Cookies loaded from fb_cookies.json (gitignored — never commit cookies to git)
let COOKIES = [];
const COOKIE_FILE = path.join(__dirname, 'fb_cookies.json');
try {
  const raw = fs.readFileSync(COOKIE_FILE, 'utf-8');
  const data = JSON.parse(raw);
  COOKIES = [
    { name: 'c_user', value: data.c_user, domain: '.facebook.com', path: '/' },
    { name: 'xs', value: data.xs, domain: '.facebook.com', path: '/' },
    { name: 'fr', value: data.fr, domain: '.facebook.com', path: '/' },
    { name: 'presence', value: data.presence, domain: '.facebook.com', path: '/' },
  ];
} catch (e) {
  console.error(`[fb_job_scraper] ❌ Cannot read ${COOKIE_FILE}: ${e.message}`);
  process.exit(1);
}

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
  'chef', 'cook', 'kitchen', 'restaurant', 'restoran', 'kedai makan',
  'tukang masak', 'pembantu dapur', 'pekerja dapur', 'crew dapur',
  'commis', 'demi', 'sous', 'pastry', 'baker', 'bakery', 'culinary',
  'food', 'fb', 'f&b', 'cafe', 'kafe', 'kopitiam', 'makanan', 'dapur',
  'hotel', 'catering', 'kitchen crew', 'line cook', 'head chef',
  'barista', 'service crew', 'waiter', 'waitress', 'captain',
  'masak', 'grill', 'roti', 'cake', 'baking',
  'jawatan kosong', 'kerja kosong', 'vacancy', '招聘', '厨师',
  'burger', 'pizza', 'sushi', 'nasi', 'mee', 'kuih',
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

    // Click expand buttons to reveal hidden text (critical for job posts)
    await page.evaluate(() => {
      const expand = document.createTreeWalker(document.body, NodeFilter.SHOW_ELEMENT);
      let node, clicked = 0;
      while (node = expand.nextNode()) {
        const text = (node.textContent || '').trim();
        if (text === '展开' || text === 'See More' || text === 'See more') {
          try { node.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window })); clicked++; } catch(e) {}
        }
      }
      return clicked;
    });
    await page.waitForTimeout(2000);

    // Scroll to load more posts
    for (let i = 0; i < 12; i++) {
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
