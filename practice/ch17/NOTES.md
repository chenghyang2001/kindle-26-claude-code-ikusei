# K26 第 17 章練習筆記：接上自訂模型（LiteLLM proxy）

日期：2026-10-18｜模式：快速 demo 模式（未經 QA／審查）

## 做了什麼

1. `litellm-config.yaml`：LiteLLM proxy 設定範本，`model_list` 共 5 個模型，涵蓋三種來源：
   - Gemini（AI Studio）：`gemini-pro`、`gemini-flash`，金鑰 `os.environ/GEMINI_API_KEY`
   - Vertex AI：`vertex-gemini-pro`、`vertex-claude-sonnet`，用 `VERTEX_PROJECT`／`VERTEX_LOCATION`／`GOOGLE_APPLICATION_CREDENTIALS`
   - Ollama：`ollama-coder`（`ollama_chat/qwen2.5-coder:7b`），位址 `os.environ/OLLAMA_API_BASE`
   - 另設 `drop_params: true` 與 `master_key: os.environ/LITELLM_MASTER_KEY`
2. `run-proxy.md`：安裝（uv／pip／Docker）、proxy 端環境變數表、啟動與健康檢查、
   Claude Code 端的 `ANTHROPIC_BASE_URL` + `ANTHROPIC_AUTH_TOKEN`、四種指定模型的方法。
3. 本筆記。

## 結果

- `uv run --with pyyaml python` 驗證 YAML：語法正確，解析出 5 個模型，
  供應商前綴 `gemini`／`vertex_ai`／`ollama_chat` 三種都有，`master_key` 為環境變數佔位。
- 依指示**未**安裝 LiteLLM、**未**改任何環境變數、**未**實際連線，所以 proxy 能否真的轉送、
  各模型的工具呼叫表現如何，都還沒驗證。

## 和書上做法的差異

> 本次沒有翻閱書本原文，以下是依一般做法推測可能的差異，實際請對照書上內容。

- **全部金鑰用 `os.environ/` 佔位**：書上範例常直接示意填值；這裡刻意不寫任何值，檔案可安全進版控。
- **加了 `drop_params: true`**：Claude Code 會送 thinking、cache_control 等 Anthropic 專屬參數，
  非 Claude 模型可能因此回 400，先丟掉比較穩。
- **Ollama 用 `ollama_chat/` 而非 `ollama/`**：前者走 chat 端點，對工具呼叫支援較好。
- **Vertex AI 多放一個 Claude 模型**：示範同一個 proxy 也能把 Claude 改走 GCP 計費。
- **用 `ANTHROPIC_AUTH_TOKEN` 而非 `ANTHROPIC_API_KEY`**：避免誤扣 API Credits（呼應全域成本規則）。
- **模型指定列了四種方式**（`--model`、`ANTHROPIC_MODEL`、`ANTHROPIC_DEFAULT_*_MODEL`、`/model`）。

## 已知未處理的風險

- 模型版本名稱（如 `gemini-2.5-pro`、`claude-sonnet-4-5`）可能隨時間改名，實際使用前要對照官方清單。
- Vertex 上的 Claude 有區域限制（常見 `us-east5`），與 Gemini 共用 `VERTEX_LOCATION` 可能不適用。
- 本機 7B 模型多半撐不起 Claude Code 的工具呼叫流程，只適合體驗。
