# K26 第 20 章：成本筆記

> 本機實測版本：ccusage 20.0.35。以下第三方模型接法**只寫步驟，本次沒有實際設定、沒有改任何環境變數**。

## 1. ccusage 常用子指令

ccusage 會讀本機 `~/.claude/projects/**/*.jsonl` 的對話紀錄，換算 token 與「等值 API 費用」。
用 Max／Pro 訂閱時，這個金額只是**估算的 API 定價**，不是實際扣款。

| 子指令 | 用途 | 範例 |
| --- | --- | --- |
| `daily`（預設） | 依日期彙總 | `npx -y ccusage@latest daily --since 20261011` |
| `monthly` | 依月份彙總，看長期趨勢 | `npx -y ccusage@latest monthly` |
| `session` | 依 session（對話）彙總，找出最燒錢的對話 | `npx -y ccusage@latest session --order desc` |
| `blocks` | 依 5 小時計費區塊彙總，對應訂閱的用量重置週期 | `npx -y ccusage@latest blocks --active` |
| `weekly` | 依週彙總（新版才有） | `npx -y ccusage@latest weekly` |
| `statusline` | 給 Claude Code 狀態列 hook 用的精簡輸出（Beta） | 設在 `statusLine` 指令 |

常用選項：

- `--since / --until YYYYMMDD`：限定日期範圍
- `--json`：輸出 JSON，方便用 Python／jq 再加工（本練習就是這樣擷取欄位）
- `--breakdown`：拆出每個模型（Opus／Sonnet／Haiku）的費用
- `--offline`：用快取的價格表，不連網
- `--timezone Asia/Taipei`：指定分日時區
- `blocks --active`：只看目前這個 5 小時區塊，含燒完速度預估；`blocks --recent`：最近 3 天

## 2. GLM（智譜）第三方 Base URL 接法

原理：Claude Code 透過 `ANTHROPIC_BASE_URL` 指到相容 Anthropic API 的第三方端點，用該廠商的 key 計費。

步驟：

1. 到智譜開放平台（bigmodel.cn 或國際版 z.ai）註冊，建立 API Key，必要時購買 GLM Coding 方案。
2. **只在當次 shell 設定**（不要用 `setx` 或寫進 `.bashrc`，以免所有 session 都改走 GLM）：

   ```bash
   export ANTHROPIC_BASE_URL="https://open.bigmodel.cn/api/anthropic"   # 國際版：https://api.z.ai/api/anthropic
   export ANTHROPIC_AUTH_TOKEN="<你的 GLM API Key>"
   export ANTHROPIC_MODEL="glm-4.6"            # 依廠商當時提供的模型名稱調整
   claude
   ```

3. 或寫在**專案層** `.claude/settings.local.json` 的 `env` 區段（該檔要加進 `.gitignore`，key 不可 commit）。
4. 進入後用 `/status` 確認 Base URL 與模型已切換。
5. 用完關掉 shell 即恢復原本的訂閱登入。

注意：

- 依全域規則，**不要設全域 `ANTHROPIC_API_KEY`**，否則 `claude -p` 會改扣 API Credits。
- 第三方端點的工具呼叫、快取、圖片支援度可能與官方不同；ccusage 算出的費用是用 Claude 價格表，**對 GLM 不準**。

## 3. Ollama ＋ LiteLLM 本地模型接法

原理：Ollama 在本機跑開源模型；LiteLLM Proxy 把它包成 Anthropic 相容的 `/v1/messages` 端點，再讓 Claude Code 的 `ANTHROPIC_BASE_URL` 指過去。

步驟：

1. 安裝 Ollama：`winget install Ollama.Ollama`
2. 下載模型（挑支援 tool calling 的，例如 `qwen2.5-coder`）：`ollama pull qwen2.5-coder:14b`
3. 確認服務：`ollama list`，預設監聽 `http://localhost:11434`
4. 安裝 LiteLLM：`python -m pip install "litellm[proxy]"`
5. 寫 `litellm.yaml`：

   ```yaml
   model_list:
     - model_name: local-coder
       litellm_params:
         model: ollama_chat/qwen2.5-coder:14b
         api_base: http://localhost:11434
   general_settings:
     master_key: sk-local-only     # 只是本機代理的通行碼
   ```

6. 啟動代理：`litellm --config litellm.yaml --port 4000`
7. 在**當次 shell** 指過去：

   ```bash
   export ANTHROPIC_BASE_URL="http://localhost:4000"
   export ANTHROPIC_AUTH_TOKEN="sk-local-only"
   export ANTHROPIC_MODEL="local-coder"
   claude
   ```

8. 用 `/status` 確認，再丟一個簡單任務測試工具呼叫是否正常。

注意：

- 本地模型免費但能力明顯弱於 Claude，長 context 與多步驟工具呼叫容易出錯；適合離線、隱私敏感或簡單任務。
- 14B 模型建議 16GB 以上記憶體／VRAM。
- 本機已常駐多個 claude 進程時記憶體吃緊，需留意。
