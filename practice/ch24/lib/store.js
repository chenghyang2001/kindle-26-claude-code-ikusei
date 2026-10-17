// JSON 檔儲存層：商品、購物車、訂單
import { readFileSync, writeFileSync, renameSync, existsSync } from 'node:fs';
import { randomBytes } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const DATA_DIR = join(dirname(fileURLToPath(import.meta.url)), '..', 'data');
const SEED_FILE = join(DATA_DIR, 'products.json');
const DB_FILE = process.env.DB_FILE || join(DATA_DIR, 'db.json');

/** 帶 HTTP 狀態碼的業務錯誤，server.js 會轉成統一錯誤格式 */
export class AppError extends Error {
  constructor(status, code, message) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

function loadDb() {
  if (existsSync(DB_FILE)) {
    try {
      return JSON.parse(readFileSync(DB_FILE, 'utf-8'));
    } catch (err) {
      // db.json 損毀時不要默默覆蓋，讓啟動失敗以便人工檢查
      throw new Error(`無法解析 ${DB_FILE}：${err.message}`);
    }
  }
  const products = JSON.parse(readFileSync(SEED_FILE, 'utf-8'));
  return { products, carts: {}, orders: [] };
}

let db = loadDb();

// 先寫暫存檔再 rename，避免寫到一半當機留下壞檔
function saveDb() {
  const tmp = `${DB_FILE}.tmp`;
  writeFileSync(tmp, JSON.stringify(db, null, 2), 'utf-8');
  renameSync(tmp, DB_FILE);
}

const findProduct = (id) => db.products.find((p) => p.id === id);

export function listProducts() {
  return db.products;
}

function cartView(cartId) {
  const items = (db.carts[cartId] || []).map(({ productId, qty }) => {
    const p = findProduct(productId);
    return { productId, name: p.name, emoji: p.emoji, price: p.price, qty, subtotal: p.price * qty };
  });
  const total = items.reduce((sum, i) => sum + i.subtotal, 0);
  const count = items.reduce((sum, i) => sum + i.qty, 0);
  return { cartId, items, count, total };
}

export function getCart(cartId) {
  return cartView(cartId);
}

function requireProduct(productId) {
  const p = findProduct(productId);
  if (!p) throw new AppError(404, 'NOT_FOUND', `找不到商品 ${productId}`);
  return p;
}

export function addToCart(cartId, productId, qty) {
  const p = requireProduct(productId);
  const items = db.carts[cartId] || (db.carts[cartId] = []);
  const line = items.find((i) => i.productId === productId);
  const newQty = (line?.qty ?? 0) + qty;
  if (newQty > p.stock) throw new AppError(409, 'OUT_OF_STOCK', `「${p.name}」庫存不足（剩 ${p.stock}）`);
  if (line) line.qty = newQty;
  else items.push({ productId, qty });
  saveDb();
  return cartView(cartId);
}

export function setCartQty(cartId, productId, qty) {
  const p = requireProduct(productId);
  const items = db.carts[cartId] || [];
  const line = items.find((i) => i.productId === productId);
  if (!line) throw new AppError(404, 'NOT_FOUND', '購物車內沒有這項商品');
  if (qty > p.stock) throw new AppError(409, 'OUT_OF_STOCK', `「${p.name}」庫存不足（剩 ${p.stock}）`);
  if (qty === 0) db.carts[cartId] = items.filter((i) => i !== line);
  else line.qty = qty;
  saveDb();
  return cartView(cartId);
}

export function checkout(cartId, customer) {
  const cart = cartView(cartId);
  if (cart.items.length === 0) throw new AppError(409, 'CART_EMPTY', '購物車是空的');
  // 先全部檢查再扣庫存，避免扣到一半才發現缺貨
  for (const item of cart.items) {
    const p = findProduct(item.productId);
    if (item.qty > p.stock) throw new AppError(409, 'OUT_OF_STOCK', `「${p.name}」庫存不足（剩 ${p.stock}）`);
  }
  for (const item of cart.items) findProduct(item.productId).stock -= item.qty;

  const order = {
    id: `ORD-${Date.now().toString(36).toUpperCase()}-${randomBytes(2).toString('hex').toUpperCase()}`,
    createdAt: new Date().toISOString(),
    status: '已成立',
    customer,
    items: cart.items,
    total: cart.total,
  };
  db.orders.push(order);
  delete db.carts[cartId];
  saveDb();
  return order;
}

export function getOrder(orderId) {
  const order = db.orders.find((o) => o.id === orderId);
  if (!order) throw new AppError(404, 'NOT_FOUND', `找不到訂單 ${orderId}`);
  return order;
}

export function findOrdersByPhone(phone) {
  return db.orders.filter((o) => o.customer.phone === phone).reverse();
}
