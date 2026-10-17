# 用 LiteLLM proxy 讓 Claude Code 接上自訂模型

> 本文件只是步驟範本，本練習**沒有**實際安裝 LiteLLM、沒有設定環境變數、也沒有連線。

## 架構

```
Claude Code ──(Anthropic Messages API)──▶ LiteLLM proxy :4000 ──▶ Gemini / Vertex AI / Ollama
              ANTHROPIC_BASE_URL                      litellm-config.yaml
              ANTHROPIC_AUTH_TOKEN = master_key
```

LiteLLM proxy 對外提供與 Anthropic 相容的 `/v1/messages` 端點，Claude Code 以為自己在跟 Anthropic 講話，實際由 proxy 轉送到 `litellm-config.yaml` 裡的模型。

## 1. 安裝 LiteLLM proxy

擇一：

```bash
# 推薦：用 uv 裝成獨立工具（不汙染專案環境）
uv tool install "litellm[proxy]"

# 或 pip
python -m pip install "litellm[proxy]"

# 或 Docker
docker pull ghcr.io/berriai/litellm:main-stable
```

若要用 Ollama，另外安裝並拉模型：

```bash
winget install Ollama.Ollama
ollama pull qwen2.5-coder:7b
```

## 2. 設定 proxy 端需要的環境變數

在**啟動 proxy 的那個終端**設定（只影響該視窗，不要寫進全域設定）：

| 變數 | 用途 | 範例 |
| --- | --- | --- |
| `LITELLM_MASTER_KEY` | proxy 主金鑰，需以 `sk-` 開頭 | `sk-local-xxxx` |
| `GEMINI_API_KEY` | Google AI Studio 金鑰 | （從 aistudio.google.com 取得） |
| `VERTEX_PROJECT` | GCP 專案 ID | `my-gcp-project` |
| `VERTEX_LOCATION` | Vertex 區域 | `us-central1`（Claude 用 `us-east5`） |
| `GOOGLE_APPLICATION_CREDENTIALS` | 服務帳號 JSON 檔路徑 | `$HOME/.gcp/sa.json` |
| `OLLAMA_API_BASE` | Ollama 服務位址 | `http://localhost:11434` |

```bash
# Git Bash 範例（金鑰請自行填入，不要寫進任何檔案）
export LITELLM_MASTER_KEY="sk-local-請自訂"
export GEMINI_API_KEY="..."
export VERTEX_PROJECT="my-gcp-project"
export VERTEX_LOCATION="us-central1"
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.gcp/sa.json"
export OLLAMA_API_BASE="http://localhost:11434"
```

## 3. 啟動 proxy

```bash
litellm --config litellm-config.yaml --port 4000
# Docker 版：
# docker run -p 4000:4000 -v "$PWD/litellm-config.yaml:/app/config.yaml" \
#   -e LITELLM_MASTER_KEY -e GEMINI_API_KEY ... ghcr.io/berriai/litellm:main-stable --config /app/config.yaml
```

檢查是否正常：

```bash
curl http://localhost:4000/health/liveliness
curl http://localhost:4000/v1/models -H "Authorization: Bearer $LITELLM_MASTER_KEY"
```

## 4. 讓 Claude Code 指向 proxy

在**要執行 Claude Code 的終端**設定兩個變數：

```bash
export ANTHROPIC_BASE_URL="http://localhost:4000"
export ANTHROPIC_AUTH_TOKEN="$LITELLM_MASTER_KEY"   # 必須等於 proxy 的 master_key
claude
```

- `ANTHROPIC_BASE_URL`：把 API 請求改送到 proxy（不要加 `/v1`，Claude Code 會自己補）。
- `ANTHROPIC_AUTH_TOKEN`：以 `Authorization: Bearer` 送出，proxy 用它驗證。
- 不要同時設 `ANTHROPIC_API_KEY`，避免混用或誤扣 API Credits。

想只在本專案生效，也可寫進 `.claude/settings.local.json` 的 `env` 區段（該檔不進版控）。

## 5. 指定要用哪個模型

模型名稱就是 `litellm-config.yaml` 裡的 `model_name`。

```bash
# 方法 A：啟動參數
claude --model gemini-pro

# 方法 B：環境變數（主模型）
export ANTHROPIC_MODEL="vertex-claude-sonnet"

# 方法 C：對應 Claude Code 內建的 sonnet / opus / haiku 別名
export ANTHROPIC_DEFAULT_SONNET_MODEL="gemini-pro"
export ANTHROPIC_DEFAULT_OPUS_MODEL="vertex-gemini-pro"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="gemini-flash"   # 背景小任務用的快速模型

# 方法 D：在 Claude Code 對話中切換
/model ollama-coder
```

## 注意事項

- 非 Claude 模型對工具呼叫（tool use）的支援度不一，Claude Code 的編輯、搜尋等功能可能失靈；本機小模型最明顯。
- Prompt caching、extended thinking 等 Anthropic 專屬功能在其他模型上無效（`drop_params: true` 會把它們丟掉）。
- 用完記得關掉 proxy、清掉該終端的環境變數。
