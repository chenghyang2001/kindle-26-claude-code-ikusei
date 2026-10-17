
## 本專案例外

本專案是 Kindle 書籍教學 demo（kindle-drill 快速模式），豁免全域「程式碼三 agent 鐵律」：主 Claude 直接寫檔，不派 code-writer／code-qa／code-reviewer；不需詢問複雜度，也不需詢問是否使用快速模式（已選快速模式）。
所有選擇題一律採用推薦選項、不要停下來問使用者；不可修改全域 `~/.claude/settings.json`，設定一律寫在本專案的 `.claude/settings.local.json`。

## 專案概述

K26 第 24 章練習「純雲端部署的電商網站」的**本機版**：手機優先的迷你電商（商品列表、購物車、結帳、訂單查詢）。
書上做法是 Vercel + Neon；本專案只在本機 `127.0.0.1:3700` 執行，雲端部署步驟只記錄在 `DEPLOY.md`，不實際部署。

## 技術棧

| 層 | 選擇 | 理由 |
| --- | --- | --- |
| 執行環境 | Node.js 24（ESM） | 本機已安裝 |
| 後端 | Node 內建 `node:http`（不用 Express） | 零相依，不需 `npm install` |
| 儲存 | JSON 檔（`data/db.json`，寫入採暫存檔 + rename） | 最簡單、可直接打開檢查 |
| 前端 | 單頁 HTML + 原生 JS + CSS（手機優先、響應式） | 無建置步驟 |
| 測試 | `scripts/e2e.sh`（curl 跑完整流程） | 輸出存 `e2e.txt` |

## 目錄結構

```
server.js            # HTTP 伺服器：路由、靜態檔、錯誤處理
lib/store.js         # JSON 檔儲存層（商品、購物車、訂單）
data/products.json   # 商品種子資料（入版控）
data/db.json         # 執行期資料（購物車/訂單，gitignore）
public/              # 前端：index.html、app.js、style.css
scripts/e2e.sh       # curl 端對端測試
DEPLOY.md            # Vercel + Neon 部署說明（僅文件）
NOTES.md             # 練習紀錄
```

## API 規格

所有 API 回傳 JSON（`Content-Type: application/json; charset=utf-8`）。金額單位：新台幣整數。

| 方法 | 路徑 | 說明 | 成功 |
| --- | --- | --- | --- |
| GET | `/api/health` | 健康檢查 | 200 `{ok:true}` |
| GET | `/api/products` | 商品列表 | 200 `{products:[...]}` |
| GET | `/api/cart/:cartId` | 取得購物車（含小計/總計） | 200 `{cart}` |
| POST | `/api/cart/:cartId/items` | 加入商品 `{productId, qty}`（累加） | 200 `{cart}` |
| PATCH | `/api/cart/:cartId/items/:productId` | 設定數量 `{qty}`，0 = 移除 | 200 `{cart}` |
| POST | `/api/checkout` | 結帳 `{cartId, name, phone, address}`，扣庫存、清空購物車 | 201 `{order}` |
| GET | `/api/orders/:orderId` | 查單筆訂單 | 200 `{order}` |
| GET | `/api/orders?phone=09xx` | 依電話查訂單 | 200 `{orders:[...]}` |

`cartId` 由前端產生（`localStorage`），格式 `^[A-Za-z0-9_-]{6,64}$`。

## 錯誤處理

- 錯誤一律回 `{ "error": { "code": "<代碼>", "message": "<繁中說明>" } }`。
- 狀態碼：400 `BAD_REQUEST`/`VALIDATION_ERROR`、404 `NOT_FOUND`、405 `METHOD_NOT_ALLOWED`、409 `OUT_OF_STOCK`/`CART_EMPTY`、413 `PAYLOAD_TOO_LARGE`、500 `INTERNAL_ERROR`（不洩漏內部細節，細節只寫到 console）。
- 請求 body 上限 10KB；JSON 解析失敗回 400。
- 前端以畫面 toast 顯示錯誤訊息，不只 console。

## 執行方式

```bash
node server.js                 # 預設 127.0.0.1:3700（可用 PORT / HOST 環境變數覆寫）
bash scripts/e2e.sh > e2e.txt  # 伺服器啟動後執行
```
