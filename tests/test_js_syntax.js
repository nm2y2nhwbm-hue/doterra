/**
 * Agent 3 負責範圍：全站 JavaScript 靜態語法與腳本編譯自動化檢測 (tests/test_js_syntax.js)
 */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const baseDir = path.join(__dirname, '..');
const checkDirs = [
  path.join(baseDir, 'static'),
  path.join(baseDir, 'components', 'cart')
];

console.log('🧪 [Agent 3] 開始執行全站 JavaScript 靜態語法安全檢測...');

let fileCount = 0;
const errors = [];

checkDirs.forEach(dir => {
  if (!fs.existsSync(dir)) return;
  const files = fs.readdirSync(dir);
  files.forEach(f => {
    if (f.endsWith('.js')) {
      const fullPath = path.join(dir, f);
      try {
        const code = fs.readFileSync(fullPath, 'utf8');
        new vm.Script(code, { filename: f });
        fileCount++;
      } catch (err) {
        errors.push({ file: f, error: err.message });
      }
    }
  });
});

console.log(`   檢測通過 ${fileCount} 個 JavaScript 腳本檔，發現錯誤: ${errors.length}`);
assert.equal(errors.length, 0, `發現 JS 語法錯誤: ${JSON.stringify(errors)}`);
console.log('✅ [Agent 3] 全站所有 JavaScript 語法檢測 100% 通過！');
