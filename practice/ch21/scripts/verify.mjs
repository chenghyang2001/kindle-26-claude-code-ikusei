// 驗證 index.html 結構：必要元素 id 與資源載入，供每個 task 合併前執行
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const requiredIds = ['new-todo-form', 'new-todo-input', 'todo-list', 'todo-count', 'filters', 'clear-completed', 'message'];

let html;
try {
  html = readFileSync(join(root, 'index.html'), 'utf-8');
} catch (err) {
  console.error(`錯誤：無法讀取 index.html（${err.message}）`);
  process.exit(1);
}

const failures = [];
for (const id of requiredIds) {
  if (!new RegExp(`id="${id}"`).test(html)) failures.push(`缺少元素 #${id}`);
}
if (!/<script[^>]+src="app\.js"/.test(html)) failures.push('未載入 app.js');
if (!/<link[^>]+href="style\.css"/.test(html)) failures.push('未載入 style.css');
if (!/<html lang="zh-TW">/.test(html)) failures.push('缺少 lang="zh-TW"');
for (const f of ['all', 'active', 'completed']) {
  if (!html.includes(`data-filter="${f}"`)) failures.push(`缺少篩選按鈕 ${f}`);
}

if (failures.length > 0) {
  console.error('index.html 驗證失敗：\n- ' + failures.join('\n- '));
  process.exit(1);
}
console.log(`index.html 驗證通過（${requiredIds.length} 個必要元素、3 個篩選按鈕）`);
