#!/usr/bin/env node
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const thumbnails = [
  { file: 'myk-art-thumb.jpg', name: 'myk art', replace: 'myk art — 抽象画ポートフォリオ' },
  { file: 'blanc-de-blanc-thumb.jpg', name: 'BLANC DE BLANC', replace: 'BLANC DE BLANC — ダイニングバー ブランドサイト' },
  { file: 'requirebot-thumb.jpg', name: 'RequiBot', replace: 'RequiBot — 要件定義チャット' }
];

let htmlContent = fs.readFileSync(path.join(__dirname, 'index.html'), 'utf-8');

for (const thumb of thumbnails) {
  const imagePath = path.join(__dirname, thumb.file);
  if (!fs.existsSync(imagePath)) {
    console.log(`⚠️  ${thumb.file} not found, skipping...`);
    continue;
  }

  const imageBuffer = fs.readFileSync(imagePath);
  const base64 = imageBuffer.toString('base64');
  const dataUri = `data:image/jpeg;base64,${base64}`;

  // HTML 内で該当のカードを探して、img src を置き換える
  const cardRegex = new RegExp(
    `(<article class="work-card"[^>]*>\\s*<div class="work-thumb">\\s*<div class="work-thumb-inner">\\s*<img src=")([^"]+)("\\s*>\\s*</div>\\s*</div>\\s*<div class="work-overlay">.*?<a[^>]*>[^<]*</a>\\s*</div>\\s*</div>\\s*<div class="work-info">.*?${thumb.replace.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`,
    's'
  );

  if (cardRegex.test(htmlContent)) {
    htmlContent = htmlContent.replace(cardRegex, (match) => {
      return match.replace(/src="[^"]*"/, `src="${dataUri}"`);
    });
    console.log(`✅ Updated ${thumb.name} thumbnail`);
  } else {
    console.log(`⚠️  Could not find ${thumb.name} card, trying simple replacement...`);
    // 別のアプローチで置き換え
    const simpleRegex = new RegExp(
      `(<h3 class="work-title">${thumb.replace.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}</h3>)`,
      's'
    );
    if (simpleRegex.test(htmlContent)) {
      // その h3 の直前の img タグを探す
      const lines = htmlContent.split('\n');
      let updated = false;
      for (let i = 0; i < lines.length; i++) {
        if (lines[i].includes(thumb.replace)) {
          // 上に遡って img src を探す
          for (let j = i - 1; j >= Math.max(0, i - 20); j--) {
            if (lines[j].includes('src="data:image') || lines[j].includes('src="')) {
              lines[j] = lines[j].replace(/src="[^"]*"/, `src="${dataUri}"`);
              updated = true;
              break;
            }
          }
          if (updated) break;
        }
      }
      if (updated) {
        htmlContent = lines.join('\n');
        console.log(`✅ Updated ${thumb.name} thumbnail (simple method)`);
      }
    }
  }
}

fs.writeFileSync(path.join(__dirname, 'index.html'), htmlContent, 'utf-8');
console.log('\n✨ All thumbnails updated in index.html');
