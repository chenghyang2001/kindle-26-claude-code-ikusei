# 部署到 Vercel + Neon（僅文件，本練習未實際部署）

本機版用 `node:http` + JSON 檔；上雲時 JSON 檔不能用（Vercel Serverless 檔案系統是唯讀、每次呼叫可能是新的執行個體），
所以資料層要換成 Neon PostgreSQL，API 改寫成 Vercel Functions。

## 1. 架構對照

| 本機版 | 雲端版 |
| --- | --- |
| `server.js`（常駐 HTTP 伺服器） | `api/*.js` Vercel Functions（每個請求冷/熱啟動） |
| `lib/store.js` + `data/db.json` | Neon PostgreSQL（`@neondatabase/serverless`） |
| `public/` 由 server.js 提供 | `public/` 由 Vercel CDN 直接提供 |
| 環境變數 `PORT` / `HOST` | 環境變數 `DATABASE_URL`（Vercel Secrets） |

## 2. 建立 Neon 資料庫

1. 到 <https://console.neon.tech> 建專案（Region 選 `AWS ap-southeast-1` 新加坡，離台灣近）。
2. 複製 **pooled** 連線字串（`...-pooler...`），Serverless 環境要用 pooled 版本避免連線數爆掉。
3. 在 SQL Editor 執行 schema：

```sql
CREATE TABLE products (
  id          TEXT PRIMARY KEY,
  name        TEXT NOT NULL,
  price       INTEGER NOT NULL CHECK (price >= 0),
  stock       INTEGER NOT NULL CHECK (stock >= 0),
  emoji       TEXT,
  description TEXT
);

CREATE TABLE cart_items (
  cart_id    TEXT NOT NULL,
  product_id TEXT NOT NULL REFERENCES products(id),
  qty        INTEGER NOT NULL CHECK (qty BETWEEN 1 AND 99),
  PRIMARY KEY (cart_id, product_id)
);

CREATE TABLE orders (
  id         TEXT PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  status     TEXT NOT NULL DEFAULT '已成立',
  name       TEXT NOT NULL,
  phone      TEXT NOT NULL,
  address    TEXT NOT NULL,
  total      INTEGER NOT NULL
);
CREATE INDEX orders_phone_idx ON orders (phone);

CREATE TABLE order_items (
  order_id   TEXT NOT NULL REFERENCES orders(id),
  product_id TEXT NOT NULL REFERENCES products(id),
  name       TEXT NOT NULL,
  price      INTEGER NOT NULL,
  qty        INTEGER NOT NULL
);
```

1. 種子資料：把 `data/products.json` 轉成 `INSERT INTO products ...` 執行。

## 3. 改寫 API 為 Vercel Functions

```
api/
  products.js                 # GET
  cart/[cartId].js            # GET
  cart/[cartId]/items.js      # POST
  cart/[cartId]/items/[pid].js# PATCH
  checkout.js                 # POST（交易）
  orders/index.js             # GET ?phone=
  orders/[orderId].js         # GET
lib/db.js                     # neon(process.env.DATABASE_URL)
```

重點：

- 所有 SQL 一律參數化（`sql\`SELECT * FROM orders WHERE id = ${id}\`` 是 tagged template，會自動參數化）。
- **結帳必須用交易**，並用條件式扣庫存防超賣：
  `UPDATE products SET stock = stock - $1 WHERE id = $2 AND stock >= $1`，影響列數為 0 就 ROLLBACK 回 409。
- 錯誤格式沿用 `{ error: { code, message } }`，500 不回傳 SQL 細節。

## 4. 部署指令

```bash
npm i @neondatabase/serverless
npm i -g vercel
vercel link                       # 連結 / 建立 Vercel 專案
vercel env add DATABASE_URL       # 貼上 Neon pooled 連線字串（Production + Preview）
vercel                            # 預覽部署
vercel --prod                     # 正式部署
```

## 5. 部署後驗證

```bash
BASE_URL=https://<your-app>.vercel.app bash scripts/e2e.sh > e2e-prod.txt
```

## 6. 部署前 Checklist

- [ ] `DATABASE_URL` 只在 Vercel 環境變數，`.env` 已 gitignore
- [ ] 結帳使用交易 + 條件式扣庫存
- [ ] 手機實機測試（iOS Safari 底部安全區、Android Chrome）
- [ ] Neon 免費方案會自動休眠，第一個請求可能慢 1～2 秒
