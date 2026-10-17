# K26 第 24 章練習筆記：純雲端部署的電商網站（本機版）

日期：2026-10-18　模式：kindle-drill 快速 demo 模式（未經 QA／code review）

## 做了什麼

1. **CLAUDE.md**：保留原有「本專案例外」，追加技術棧、目錄結構、API 規格、錯誤處理規範。
2. **後端**（零相依，不需 `npm install`）
   - `server.js`：`node:http` 伺服器，路由表、JSON body 解析（10KB 上限、非 UTF-8 拒收）、靜態檔（防 `../` 路徑穿越）、統一錯誤格式。
   - `lib/store.js`：JSON 檔儲存，寫入用「暫存檔 + rename」避免壞檔；結帳先檢查全部庫存再扣，避免扣一半。
3. **前端**（`public/`）：手機優先單頁，底部分頁列（商品／購物車／訂單），2→3→4 欄響應式格線，支援深色模式；
   購物車 id 存 `localStorage`；所有內容用 `textContent` 渲染防 XSS；錯誤以 toast 顯示。
4. **E2E**：`scripts/e2e.sh` 用 curl 跑「列商品 → 加入購物車 → 結帳 → 查訂單」＋ 5 個錯誤案例，輸出存 `e2e.txt`。
5. **DEPLOY.md**：Vercel + Neon 的部署步驟、schema、交易防超賣寫法（未實際部署）。

## 結果

- 伺服器在 `127.0.0.1:3700` 背景啟動，E2E 全數符合預期：8 個成功請求（200/201）＋ 5 個錯誤案例（409/409/400/404/400）。
- 結帳後：訂單成立（總計 NT$1,020）、購物車清空、咖啡豆庫存 20 → 18。
- 驗證完已關閉伺服器，3700 埠已釋放。

## 過程中踩到的坑

| 問題 | 原因 | 處理 |
| --- | --- | --- |
| 訂單裡中文姓名／地址變亂碼 | Windows 的 `curl.exe` 會把命令列參數轉成 cp950 再送出 | e2e 改用 `printf ... \| curl --data-binary @-` 走 stdin；伺服器加 `TextDecoder(fatal)`，非 UTF-8 一律回 400（E5 驗證） |
| 重啟後測到舊版伺服器 | Git Bash 把 `taskkill //PID` 的參數轉壞，舊程序沒被關掉，新伺服器綁埠失敗 | 改用 `MSYS_NO_PATHCONV=1 taskkill /PID <pid> /F`，並先確認埠已釋放再啟動 |
| heredoc 寫前端 JS 失敗 | Git Bash heredoc 解析長 JS 出錯 | 改用編輯器工具直接寫檔 |

## 和書上做法的差異

| 項目 | 書上（純雲端） | 本練習（本機版） |
| --- | --- | --- |
| 部署 | Vercel 正式部署，取得公開網址 | 只在 `127.0.0.1:3700` 跑，部署寫在 DEPLOY.md |
| 資料庫 | Neon PostgreSQL | JSON 檔（`data/db.json`） |
| 後端 | Next.js / Vercel Functions | `node:http` 單一伺服器，零相依 |
| 前端 | Next.js + Tailwind 元件 | 原生 HTML/CSS/JS，無建置步驟 |
| 環境變數 | `DATABASE_URL` 放 Vercel Secrets | 不需要（只有可選的 `PORT`/`HOST`） |
| 併發安全 | DB 交易 + 條件式 UPDATE | 單程序同步寫檔，單人 demo 足夠；多實例會出問題 |
| 驗證 | 雲端網址實測 | curl 腳本 `e2e.txt` |

## 已知未處理的風險（快速模式）

- 沒有會員／登入，訂單用手機號碼即可查詢（任何人知道手機就能看到姓名地址）。
- 沒有付款流程，結帳＝直接成立訂單。
- JSON 檔不支援多程序同時寫入；購物車不會過期清除。
- 沒有自動化單元測試，只有一支 curl E2E 腳本；前端未做瀏覽器截圖驗收。
