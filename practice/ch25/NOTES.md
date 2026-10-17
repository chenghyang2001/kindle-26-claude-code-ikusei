# NOTES — K26 第 25 章練習紀錄

日期：2026-10-18　模式：kindle-drill 快速 demo 模式（未經 QA／審查 agent）

## 做了什麼

1. 用 Spec Kit 精簡流程寫 `spec.md`：constitution（原則）→ specify（需求、獎勵表、邊界條件）→ plan（技術堆疊、超參數）→ tasks（T1～T12）。
2. 寫 `train.py`：
   - Unsloth `FastLanguageModel` 4-bit 載入 + LoRA（r=16，attention + MLP 七個投影層）
   - GSM8K 轉 chat 格式，標準答案取 `####` 之後
   - 5 個獎勵函式：正確性 2.0、整數 0.5、嚴格格式 0.5、寬鬆格式 0.5、XML 標籤計數 0～0.5
   - TRL `GRPOConfig` + `GRPOTrainer`，參數針對 T4（fp16、paged_adamw_8bit、num_generations=6）
   - `--self-test`：不需 GPU 的獎勵函式測試
3. 寫 `infer.py`：載入 LoRA、greedy 生成、解析 `<answer>`；`--compare` 用 `disable_adapter()` 對照基底模型；`--eval N` 算正確率。
4. 寫 `README.md`：Colab T4 九步驟 + 常見問題。

## 結果

| 檢查 | 結果 |
| --- | --- |
| `python -m py_compile train.py infer.py` | ✅ 通過（本機 Python 3.14.3） |
| `python train.py --self-test` | ✅ 全部通過（9 組斷言，含 `1,200.`／`3.50` 正規化、純字串 completion、缺標籤） |
| 實際 GRPO 訓練 | ⏸ 未執行——本機無 GPU，未安裝 torch／unsloth／trl |
| 推理與正確率 | ⏸ 未執行，需在 Colab 訓練完才有數字 |

## 和書上做法的差異

> 注意：本次沒有逐字對照書中程式碼。下面的「書上做法」是以 Unsloth 官方 Qwen2.5 GRPO 範例 notebook 為基準（本章主題 Claude Code + Unsloth 訓練推理模型，多半沿用這份範例），實際內容請以書為準。

| 項目 | 官方範例／書上常見做法 | 本練習 |
| --- | --- | --- |
| 開發流程 | 直接在 notebook 一格一格寫 | 先用 Spec Kit 寫 spec.md，再拆成 `train.py`／`infer.py` 兩支腳本 |
| 執行方式 | Colab cell 內直接跑 | 命令列腳本 + argparse，所有超參數可覆寫 |
| 基底模型 | Qwen2.5-3B（或 1.5B） | 預設 Qwen2.5-0.5B，T4 更快、更不容易 OOM（代價：學得較慢） |
| `PatchFastRL` | 舊版必須呼叫 | 用 try/except：有就呼叫，新版沒有就略過 |
| 答案比對 | 字串完全相等 | 先正規化（去逗號、`$`、尾端句點、`3.50`→`3.5`）再比 |
| `<answer>` 沒閉合 | 取 `<answer>` 後到 `</answer>` 的 split，沒有閉合時可能出錯或拿到整段 | 有閉合用正規表達式，沒閉合才取後段，沒標籤回空字串 |
| completion 型別 | 假設一定是對話格式 `c[0]["content"]` | 對話格式與純字串都支援 |
| 推理 | 用 vLLM `fast_generate` + `load_lora` | 用 Transformers `generate`（greedy），另加 `--compare` 與 `--eval` |
| 本機驗證 | 沒有 | `--self-test` 不需 GPU 也能測獎勵函式 |
| 精度 | 依 GPU 自動選 bf16／fp16 | T4 固定 fp16（換 A100 需手動改） |

## 已知風險（快速模式未處理）

- 沒有在真實 GPU 上跑過；Unsloth／TRL 版本更新快，`GRPOConfig` 參數名（如 `max_prompt_length`）或 `fast_inference` 行為可能在新版變動。
- `infer.py` 用 `from train import ...` 共用函式，兩支檔案必須放在同一個目錄。
- 0.5B 模型在 250 步內正確率提升有限，主要能看到的是「格式學會了」。
- `gpu_memory_utilization=0.6` 是經驗值，T4 上若 vLLM 仍 OOM 需再調低或加 `--no-vllm`。
