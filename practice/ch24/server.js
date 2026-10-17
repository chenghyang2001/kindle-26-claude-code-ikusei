// 手機版電商網站本機版：node:http 伺服器（API + 靜態檔）
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join, normalize, extname, sep } from 'node:path';
import * as store from './lib/store.js';

const { AppError } = store;
const HOST = process.env.HOST || '127.0.0.1';
const PORT = Number(process.env.PORT || 3700);
const PUBLIC_DIR = join(dirname(fileURLToPath(import.meta.url)), 'public');
const MAX_BODY = 10 * 1024;
const CART_ID_RE = /^[A-Za-z0-9_-]{6,64}$/;
const PHONE_RE = /^09\d{8}$/;
const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
};

function sendJson(res, status, payload) {
  res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' });
  res.end(JSON.stringify(payload));
}

function readJsonBody(req) {
  return new Promise((resolve, reject) => {
    let size = 0;
    const chunks = [];
    req.on('data', (chunk) => {
      size += chunk.length;
      if (size > MAX_BODY) {
        reject(new AppError(413, 'PAYLOAD_TOO_LARGE', '請求內容過大'));
        req.destroy();
        return;
      }
      chunks.push(chunk);
    });
    req.on('end', () => {
      let text;
      try {
        // fatal: true → 非 UTF-8（例如 Windows curl 送出的 cp950）直接拒絕，避免亂碼寫進訂單
        text = new TextDecoder('utf-8', { fatal: true }).decode(Buffer.concat(chunks));
      } catch {
        return reject(new AppError(400, 'BAD_REQUEST', '請求內容必須是 UTF-8 編碼'));
      }
      if (!text) return resolve({});
      try {
        const body = JSON.parse(text);
        if (body === null || typeof body !== 'object' || Array.isArray(body)) {
          return reject(new AppError(400, 'BAD_REQUEST', '請求內容必須是 JSON 物件'));
        }
        resolve(body);
      } catch {
        reject(new AppError(400, 'BAD_REQUEST', 'JSON 格式錯誤'));
      }
    });
    req.on('error', reject);
  });
}

function requireCartId(cartId) {
  if (!CART_ID_RE.test(cartId)) throw new AppError(400, 'VALIDATION_ERROR', 'cartId 格式錯誤');
}

function requireQty(qty, { allowZero }) {
  const min = allowZero ? 0 : 1;
  if (!Number.isInteger(qty) || qty < min || qty > 99) {
    throw new AppError(400, 'VALIDATION_ERROR', `數量必須是 ${min}～99 的整數`);
  }
}

function validateCustomer({ name, phone, address }) {
  const clean = (v) => (typeof v === 'string' ? v.trim() : '');
  const customer = { name: clean(name), phone: clean(phone), address: clean(address) };
  if (!customer.name || customer.name.length > 30) throw new AppError(400, 'VALIDATION_ERROR', '請填寫姓名（30 字內）');
  if (!PHONE_RE.test(customer.phone)) throw new AppError(400, 'VALIDATION_ERROR', '手機號碼格式錯誤（09 開頭共 10 碼）');
  if (!customer.address || customer.address.length > 100) throw new AppError(400, 'VALIDATION_ERROR', '請填寫地址（100 字內）');
  return customer;
}

// 路由表：[方法, 路徑正規式, 處理函式]
const routes = [
  ['GET', /^\/api\/health$/, () => [200, { ok: true }]],
  ['GET', /^\/api\/products$/, () => [200, { products: store.listProducts() }]],
  ['GET', /^\/api\/cart\/([^/]+)$/, (_req, [cartId]) => {
    requireCartId(cartId);
    return [200, { cart: store.getCart(cartId) }];
  }],
  ['POST', /^\/api\/cart\/([^/]+)\/items$/, async (req, [cartId]) => {
    requireCartId(cartId);
    const { productId, qty = 1 } = await readJsonBody(req);
    if (typeof productId !== 'string') throw new AppError(400, 'VALIDATION_ERROR', '缺少 productId');
    requireQty(qty, { allowZero: false });
    return [200, { cart: store.addToCart(cartId, productId, qty) }];
  }],
  ['PATCH', /^\/api\/cart\/([^/]+)\/items\/([^/]+)$/, async (req, [cartId, productId]) => {
    requireCartId(cartId);
    const { qty } = await readJsonBody(req);
    requireQty(qty, { allowZero: true });
    return [200, { cart: store.setCartQty(cartId, productId, qty) }];
  }],
  ['POST', /^\/api\/checkout$/, async (req) => {
    const body = await readJsonBody(req);
    requireCartId(String(body.cartId ?? ''));
    const customer = validateCustomer(body);
    return [201, { order: store.checkout(body.cartId, customer) }];
  }],
  ['GET', /^\/api\/orders\/([^/]+)$/, (_req, [orderId]) => [200, { order: store.getOrder(orderId) }]],
  ['GET', /^\/api\/orders$/, (_req, _p, url) => {
    const phone = url.searchParams.get('phone') ?? '';
    if (!PHONE_RE.test(phone)) throw new AppError(400, 'VALIDATION_ERROR', '請提供正確的手機號碼');
    return [200, { orders: store.findOrdersByPhone(phone) }];
  }],
];

async function handleApi(req, res, url) {
  const matched = routes.filter(([, re]) => re.test(url.pathname));
  if (matched.length === 0) throw new AppError(404, 'NOT_FOUND', '找不到這個 API');
  const route = matched.find(([method]) => method === req.method);
  if (!route) throw new AppError(405, 'METHOD_NOT_ALLOWED', `不支援 ${req.method}`);
  const params = url.pathname.match(route[1]).slice(1).map(decodeURIComponent);
  const [status, payload] = await route[2](req, params, url);
  sendJson(res, status, payload);
}

async function serveStatic(req, res, url) {
  if (req.method !== 'GET' && req.method !== 'HEAD') throw new AppError(405, 'METHOD_NOT_ALLOWED', `不支援 ${req.method}`);
  const rel = url.pathname === '/' ? 'index.html' : decodeURIComponent(url.pathname).replace(/^\/+/, '');
  const filePath = normalize(join(PUBLIC_DIR, rel));
  // 防止 ../ 路徑穿越讀到 public/ 以外的檔案
  if (!filePath.startsWith(PUBLIC_DIR + sep)) throw new AppError(404, 'NOT_FOUND', '找不到檔案');
  try {
    const content = await readFile(filePath);
    res.writeHead(200, { 'Content-Type': MIME[extname(filePath)] || 'application/octet-stream' });
    res.end(req.method === 'HEAD' ? undefined : content);
  } catch (err) {
    if (err.code === 'ENOENT' || err.code === 'EISDIR') throw new AppError(404, 'NOT_FOUND', '找不到檔案');
    throw err;
  }
}

const server = createServer(async (req, res) => {
  const started = Date.now();
  try {
    const url = new URL(req.url, `http://${req.headers.host || HOST}`);
    if (url.pathname.startsWith('/api/')) await handleApi(req, res, url);
    else await serveStatic(req, res, url);
  } catch (err) {
    if (err instanceof AppError) {
      sendJson(res, err.status, { error: { code: err.code, message: err.message } });
    } else {
      console.error('[未預期錯誤]', req.method, req.url, err);
      sendJson(res, 500, { error: { code: 'INTERNAL_ERROR', message: '伺服器發生錯誤，請稍後再試' } });
    }
  } finally {
    console.log(`${req.method} ${req.url} -> ${res.statusCode} (${Date.now() - started}ms)`);
  }
});

server.on('error', (err) => {
  console.error(`伺服器啟動失敗：${err.message}`);
  process.exit(1);
});

server.listen(PORT, HOST, () => console.log(`電商網站已啟動：http://${HOST}:${PORT}`));

const shutdown = () => server.close(() => process.exit(0));
process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);
