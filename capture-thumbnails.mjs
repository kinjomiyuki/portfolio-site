#!/usr/bin/env node
import puppeteer from 'puppeteer';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const sites = [
  {
    name: 'myk art',
    url: 'https://myk-abstract-art.netlify.app/',
    output: 'myk-art-thumb.jpg'
  },
  {
    name: 'BLANC DE BLANC',
    url: 'https://blanc-de-blanc-okinawa.netlify.app/',
    output: 'blanc-de-blanc-thumb.jpg'
  },
  {
    name: 'RequiBot',
    url: 'https://derectionhelper.netlify.app/',
    output: 'requirebot-thumb.jpg'
  }
];

(async () => {
  let browser;
  try {
    browser = await puppeteer.launch({ 
      headless: 'new',
      channel: 'chrome'
    });

    for (const site of sites) {
      console.log(`📸 Capturing ${site.name} from ${site.url}...`);
      
      const page = await browser.newPage();
      await page.setViewport({ width: 1200, height: 900 });
      await page.goto(site.url, { waitUntil: 'networkidle2' });
      
      // ページ全体のスクリーンショットを取得
      await page.screenshot({
        path: path.join(__dirname, site.output),
        fullPage: false,
        type: 'jpeg',
        quality: 85
      });
      
      console.log(`✅ Saved: ${site.output}`);
      await page.close();
    }

    console.log('\n✨ All thumbnails captured!');
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  } finally {
    if (browser) await browser.close();
  }
})();
