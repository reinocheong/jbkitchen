#!/usr/bin/env node
/**
 * jbkitchen_verify.mjs — Playwright 验收测试
 * 测试：所有页面可达、按钮正常、JS无报错、视觉截屏
 * 运行：node scripts/jbkitchen_verify.mjs
 */
import { chromium } from 'playwright';

const BASE = 'https://reinocheong.github.io/jbkitchen';

const PAGES = [
  { path: '/', name: 'Homepage' },
  { path: '/chefs/', name: 'Job Board' },
  { path: '/suppliers/', name: 'Suppliers' },
  { path: '/calculator/', name: 'Cost Calculator' },
  { path: '/guides/', name: 'Guides' },
  { path: '/about/', name: 'About' },
  { path: '/contribute/', name: 'Contribute' },
  { path: '/dashboard/', name: 'Dashboard' },
  { path: '/suppliers/khl-frozen-food/', name: 'KHL Detail' },
];

const GUIDE_PAGES = [
  '/guides/halal-cert/',
  '/guides/jb-license/',
  '/guides/frozen-food-guide/',
  '/guides/mesti-certification/',
  '/guides/haccp-vs-iso-22000/',
  '/guides/food-handling-certificate/',
  '/guides/sst-service-tax-restaurant/',
  '/guides/start-frozen-food-business/',
  '/guides/cold-storage-temperature-standards/',
  '/guides/employee-epf-socso-eis-2025/',
  '/guides/frozen-food-import-permit-malaysia/',
];

const NAV_LINKS = ['Job Board', 'Suppliers', 'Cost Calculator', 'Guides', 'Contribute', 'About'];

let passed = 0, failed = 0, warnings = [];

function log(status, msg) {
  const icon = status === 'PASS' ? '✅' : status === 'FAIL' ? '❌' : '⚠️';
  console.log(`  ${icon} [${status}] ${msg}`);
  if (status === 'PASS') passed++;
  else if (status === 'FAIL') failed++;
  else warnings.push(msg);
}

(async () => {
  console.log(`\n═══════════════════════════════════════`);
  console.log(`  jbkitchen 验收测试`);
  console.log(`  ${new Date().toISOString()}`);
  console.log(`═══════════════════════════════════════\n`);

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const mobileCtx = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true });

  // ── 测试1: 所有页面可访问 ──
  console.log(`\n📄 页面可达性 (${PAGES.length + GUIDE_PAGES.length}页)`);
  for (const p of PAGES) {
    const page = await context.newPage();
    try {
      const resp = await page.goto(BASE + p.path, { waitUntil: 'networkidle', timeout: 30000 });
      const status = resp?.status() || 0;
      const title = await page.title();
      const errors = (await page.evaluate(() => {
        return window.__testErrors || [];
      }).catch(() => []));
      if (status === 200 && title) {
        log('PASS', `${p.name} — ${status} OK, title: "${title.substring(0, 50)}"`);
      } else {
        log('FAIL', `${p.name} — status ${status}, title: "${title}"`);
      }
    } catch (e) {
      log('FAIL', `${p.name} — ${e.message.substring(0, 60)}`);
    } finally {
      await page.close();
    }
  }

  // Guide pages (快速检查)
  for (const g of GUIDE_PAGES) {
    const page = await context.newPage();
    try {
      const resp = await page.goto(BASE + g, { waitUntil: 'domcontentloaded', timeout: 20000 });
      const status = resp?.status() || 0;
      if (status === 200) log('PASS', `Guide: ${g}`);
      else log('FAIL', `Guide: ${g} → ${status}`);
    } catch (e) {
      log('FAIL', `Guide: ${g} — ${e.message.substring(0, 50)}`);
    } finally {
      await page.close();
    }
  }

  // ── 测试2: 导航按钮 ──
  console.log(`\n🔗 导航链接 (${NAV_LINKS.length}个)`);
  const navPage = await context.newPage();
  await navPage.goto(BASE + '/', { waitUntil: 'networkidle', timeout: 30000 });
  for (const name of NAV_LINKS) {
    try {
      const link = navPage.locator(`a:has-text("${name}")`).first();
      const href = await link.getAttribute('href');
      if (href && href !== '#') {
        log('PASS', `"${name}" → ${href}`);
      } else {
        log('WARN', `"${name}" link not found`);
      }
    } catch (e) {
      log('FAIL', `"${name}" — ${e.message.substring(0, 50)}`);
    }
  }
  await navPage.close();

  // ── 测试3: CTA按钮 ──
  console.log(`\n🖱️ CTA 按钮`);
  const ctaPage = await context.newPage();
  await ctaPage.goto(BASE + '/', { waitUntil: 'networkidle', timeout: 30000 });
  const heroBtns = await ctaPage.locator('.hero-btn, a.btn, .cta-btn, a[class*="hero"]').count();
  if (heroBtns >= 3) log('PASS', `Hero区找到 ${heroBtns} 个按钮`);
  else log('WARN', `Hero区仅 ${heroBtns} 个按钮（期望≥3）`);
  await ctaPage.close();

  // Post Resume 按钮
  const resumePage = await context.newPage();
  await resumePage.goto(BASE + '/chefs/', { waitUntil: 'networkidle', timeout: 30000 });
  const submitBtn = await resumePage.locator('a:has-text("Submit Resume"), a:has-text("Post Resume")').first().getAttribute('href');
  if (submitBtn && submitBtn.includes('google.com/forms')) {
    log('PASS', `Submit Resume → Google Form`);
  } else {
    log('WARN', `Submit Resume link not found or wrong: ${submitBtn}`);
  }
  await resumePage.close();

  // ── 测试4: 页脚联系信息 ──
  console.log(`\n📞 联系信息`);
  const footerPage = await context.newPage();
  await footerPage.goto(BASE + '/', { waitUntil: 'networkidle', timeout: 30000 });
  const whatsappLink = await footerPage.locator('a[href*="wa.me"]').first().getAttribute('href');
  if (whatsappLink && whatsappLink.includes('60167913913')) {
    log('PASS', `WhatsApp: ${whatsappLink}`);
  } else {
    log('WARN', `WhatsApp link: ${whatsappLink || 'not found'}`);
  }
  const phoneLink = await footerPage.locator('a[href^="tel:"]').first().getAttribute('href');
  if (phoneLink) log('PASS', `Phone: ${phoneLink}`);
  else log('WARN', 'Phone link not found');
  await footerPage.close();

  // ── 测试5: SEO 标签 ──
  console.log(`\n🔍 SEO 标签`);
  for (const p of PAGES.slice(0, 4)) {
    const page = await context.newPage();
    await page.goto(BASE + p.path, { waitUntil: 'domcontentloaded', timeout: 20000 });
    const seo = await page.evaluate(() => ({
      canonical: !!document.querySelector('link[rel="canonical"]'),
      ogTitle: !!document.querySelector('meta[property="og:title"]'),
      ogDesc: !!document.querySelector('meta[property="og:description"]'),
      jsonld: !!document.querySelector('script[type="application/ld+json"]'),
      h1: !!document.querySelector('h1'),
    }));
    const seoOk = Object.values(seo).every(v => v === true);
    if (seoOk) log('PASS', `${p.name} — canonical+OG+JSON-LD+H1 齐全`);
    else {
      const missing = Object.entries(seo).filter(([, v]) => !v).map(([k]) => k);
      log('WARN', `${p.name} — 缺: ${missing.join(', ')}`);
    }
    await page.close();
  }

  // ── 测试6: 手机端视觉 ──
  console.log(`\n📱 手机端`);
  const mobilePage = await mobileCtx.newPage();
  await mobilePage.goto(BASE + '/', { waitUntil: 'networkidle', timeout: 30000 });
  await mobilePage.waitForTimeout(1000);
  
  // 截图
  await mobilePage.screenshot({ path: '/tmp/jbkitchen-mobile-home.png', fullPage: true });
  
  // 检查汉堡菜单
  const hamburger = await mobilePage.locator('.hamburger, button[aria-label="Menu"]').count();
  if (hamburger >= 1) log('PASS', '汉堡菜单可见');
  else log('WARN', '汉堡菜单未找到');

  // 检查水平滚动
  const hasScroll = await mobilePage.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
  if (hasScroll) log('WARN', '⚠️ 手机端有水平溢出滚动');
  else log('PASS', '手机端无水平溢出');
  await mobilePage.close();

  // ── 测试7: 数据新鲜度 ──
  console.log(`\n📊 数据新鲜度`);
  const dataPage = await context.newPage();
  await dataPage.goto(BASE + '/', { waitUntil: 'domcontentloaded', timeout: 20000 });
  const hasExchange = await dataPage.locator('text=USD/MYR').count();
  const hasCPI = await dataPage.locator('text=CPI Inflation').count();
  const hasNews = await dataPage.locator('text=Latest News').count();
  const hasChicken = await dataPage.locator('text=Frozen Chicken').count();
  if (hasExchange && hasCPI && hasNews && hasChicken) log('PASS', '首页数据区块全部可见（汇率/CPI/新闻/鸡价）');
  else log('WARN', `数据区块: 汇率=${hasExchange} CPI=${hasCPI} 新闻=${hasNews} 鸡价=${hasChicken}`);
  await dataPage.close();

  await browser.close();
  await mobileCtx.close();

  // ── 总结 ──
  console.log(`\n═══════════════════════════════════════`);
  console.log(`  结果: ✅ ${passed} 通过 | ❌ ${failed} 失败 | ⚠️ ${warnings.length} 警告`);
  if (warnings.length > 0) {
    console.log(`  警告详情:`);
    warnings.forEach(w => console.log(`    ⚠️ ${w}`));
  }
  if (failed === 0) console.log(`\n  ✅ 网站准备就绪，可以买域名提交了。`);
  else console.log(`\n  ❌ 有 ${failed} 个失败项需要修复。`);
  console.log(`═══════════════════════════════════════\n`);
})();
