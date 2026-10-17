#!/bin/bash
# 端對端測試：列商品 → 加入購物車 → 結帳 → 查訂單（另含 3 個錯誤案例）
set -euo pipefail

BASE="${BASE_URL:-http://127.0.0.1:3700}"
CART="e2e_$(date +%s)"
PHONE="0912345678"

# 印出步驟標題、curl 指令與回應（含 HTTP 狀態碼）
call() {
  local title="$1"; shift
  echo "===== ${title} ====="
  echo "\$ curl $*"
  curl -sS -w '\n[HTTP %{http_code}]\n' "$@" || { echo "錯誤：curl 失敗（伺服器是否已啟動？）" >&2; exit 1; }
  echo
}

curl -sf "$BASE/api/health" > /dev/null || { echo "錯誤：$BASE 沒有回應" >&2; exit 1; }

echo "# K26 Ch24 電商網站本機版 E2E 測試"
echo "# 時間：$(date '+%Y-%m-%d %H:%M:%S')　目標：$BASE　cartId：$CART"
echo

call "1. 列出商品" "$BASE/api/products"
call "2a. 加入購物車：咖啡豆 ×2" -X POST -H 'Content-Type: application/json' \
  -d '{"productId":"p001","qty":2}' "$BASE/api/cart/$CART/items"
call "2b. 加入購物車：筆記本 ×1" -X POST -H 'Content-Type: application/json' \
  -d '{"productId":"p005","qty":1}' "$BASE/api/cart/$CART/items"
call "2c. 查看購物車" "$BASE/api/cart/$CART"

# 中文 body 走 stdin（--data-binary @-）：Windows curl.exe 會把命令列參數轉成 cp950 造成亂碼
CHECKOUT=$(printf '{"cartId":"%s","name":"王小明","phone":"%s","address":"台北市信義區市府路1號"}' "$CART" "$PHONE" |
  curl -sS -X POST -H 'Content-Type: application/json' --data-binary @- \
  -w '\n[HTTP %{http_code}]' "$BASE/api/checkout")
echo "===== 3. 結帳 ====="
echo "\$ printf '{...王小明...}' | curl -X POST --data-binary @- $BASE/api/checkout（cartId=$CART, phone=$PHONE）"
echo "$CHECKOUT"
echo

ORDER_ID=$(echo "$CHECKOUT" | grep -o '"id":"ORD-[^"]*"' | head -1 | cut -d'"' -f4)
[ -n "$ORDER_ID" ] || { echo "錯誤：結帳回應中找不到訂單編號" >&2; exit 1; }

call "4a. 依訂單編號查詢：$ORDER_ID" "$BASE/api/orders/$ORDER_ID"
call "4b. 依手機查詢：$PHONE" "$BASE/api/orders?phone=$PHONE"
call "5. 結帳後購物車應為空" "$BASE/api/cart/$CART"

echo "# ---- 錯誤案例 ----"
call "E1. 加入已售完商品（預期 409）" -X POST -H 'Content-Type: application/json' \
  -d '{"productId":"p006","qty":1}' "$BASE/api/cart/$CART/items"
call "E2. 空購物車結帳（預期 409）" -X POST -H 'Content-Type: application/json' \
  -d "{\"cartId\":\"$CART\",\"name\":\"Wang\",\"phone\":\"$PHONE\",\"address\":\"Taipei\"}" "$BASE/api/checkout"
call "E3. 壞掉的 JSON（預期 400）" -X POST -H 'Content-Type: application/json' \
  -d '{bad json' "$BASE/api/cart/$CART/items"
call "E4. 不存在的訂單（預期 404）" "$BASE/api/orders/ORD-NOPE"
call "E5. 非 UTF-8 中文 body（Windows 命令列 -d 中文，預期 400）" -X POST -H 'Content-Type: application/json' \
  -d "{\"cartId\":\"$CART\",\"name\":\"王小明\",\"phone\":\"$PHONE\",\"address\":\"台北\"}" "$BASE/api/checkout"

echo "# E2E 完成：訂單 $ORDER_ID"
