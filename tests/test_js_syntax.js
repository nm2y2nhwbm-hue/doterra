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
  path.join(baseDir, 'components'),
  path.join(baseDir, 'tests')
];

console.log('🧪 [Agent 3] 開始執行全站 JavaScript 靜態語法安全檢測...');

let fileCount = 0;
const errors = [];

function scanDirectory(dir) {
  if (!fs.existsSync(dir)) return;
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      scanDirectory(fullPath);
    } else if (entry.isFile() && entry.name.endsWith('.js')) {
      try {
        const code = fs.readFileSync(fullPath, 'utf8');
        new vm.Script(code, { filename: entry.name });
        fileCount++;
      } catch (err) {
        errors.push({ file: path.relative(baseDir, fullPath), error: err.message });
      }
    }
  }
}

checkDirs.forEach(dir => scanDirectory(dir));


console.log(`   檢測通過 ${fileCount} 個 JavaScript 腳本檔，發現錯誤: ${errors.length}`);
assert.equal(errors.length, 0, `發現 JS 語法錯誤: ${JSON.stringify(errors)}`);
console.log('✅ [Agent 3] 全站所有 JavaScript 語法檢測 100% 通過！');
