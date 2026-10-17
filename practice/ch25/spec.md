# spec.md — 用 GRPO 訓練小型推理模型解 GSM8K

> Spec Kit 精簡流程：constitution → specify → plan → tasks 四段合一檔。
> 練習來源：K26 第 25 章（Claude Code ＋ Unsloth 訓練推理模型）。

---

## 1. Constitution（專案憲章）

不可違反的原則：

1. **本機只寫程式不訓練**：開發機沒有 GPU，本機只做 `python -m py_compile` 語法檢查，不安裝 torch／unsloth／trl。真正的訓練在 Google Colab（T4 16GB）執行。
2. **免費硬體可跑**：所有預設參數必須能在 Colab 免費 T4 上跑完（4-bit 量化 + LoRA，batch 小、序列短）。
3. **格式先於正確**：模型輸出必須是 `<reasoning>…</reasoning><answer>…</answer>`；獎勵函式要能分辨「格式對」與「答案對」，兩者分開給分。
4. **獎勵函式是純函式**：只吃文字、回傳 `list[float]`，不碰 GPU，可在本機單獨測試。
5. **可重現**：固定 `seed`，所有超參數集中在一個設定區塊，可用命令列覆寫。
6. **不硬編碼路徑與機密**：輸出路徑用相對路徑／參數；Hugging Face token 只從環境變數讀。

---

## 2. Specify（需求規格）

### 目標

用 **GRPO**（Group Relative Policy Optimization，不需要 value model 的 RL 演算法）微調小型指令模型，讓它在回答 GSM8K 小學數學應用題時：

- 先在 `<reasoning>` 內寫出推理過程
- 再在 `<answer>` 內只寫最終數字

### 使用者故事

- 身為學習者，我想在 Colab 上一鍵跑 `train.py`，約 30～60 分鐘看到獎勵曲線上升。
- 身為學習者，我想用 `infer.py` 載入訓練好的 LoRA，輸入一題數學題，看到格式化的推理輸出。
- 身為學習者，我想比較「有 LoRA / 沒 LoRA」的輸出差異。

### 輸入 / 輸出

| 項目 | 內容 |
| --- | --- |
| 訓練資料 | `openai/gsm8k`（config `main`，split `train`，7,473 題） |
| 標準答案 | GSM8K `answer` 欄位 `####` 之後的數字 |
| 基底模型 | 預設 `unsloth/Qwen2.5-0.5B-Instruct`；可換 `unsloth/Llama-3.2-1B-Instruct` |
| 訓練產出 | `outputs/grpo_lora/`（LoRA adapter + tokenizer） |
| 推理輸出 | `<reasoning>…</reasoning>\n<answer>…</answer>` 文字，並解析出答案 |

### 獎勵函式（共 5 個，加總為總獎勵）

| 名稱 | 條件 | 分數 |
| --- | --- | --- |
| `correctness_reward` | `<answer>` 內容（正規化後）== 標準答案 | 2.0 |
| `int_reward` | `<answer>` 內容是整數 | 0.5 |
| `strict_format_reward` | 完整符合 `^<reasoning>\n…\n</reasoning>\n<answer>\n…\n</answer>\n?$` | 0.5 |
| `soft_format_reward` | 寬鬆符合 `<reasoning>…</reasoning>\s*<answer>…</answer>` | 0.5 |
| `xml_count_reward` | 每個標籤恰好出現一次各 +0.125；`</answer>` 後多餘文字扣分 | 0～0.5 |

### 邊界條件

- 模型沒有輸出 `<answer>` → 抽取結果為空字串，正確性 0 分。
- 答案帶逗號、`$`、尾端句點（如 `1,200.`）→ 正規化後再比對。
- 答案是小數（如 `3.50` vs `3.5`）→ 能轉成數字時用數值比對。
- `completions` 可能是對話格式（list of dict）或純文字 → 兩者都要處理。
- 輸出超過 `max_completion_length` 被截斷 → 自然拿不到格式分。

---

## 3. Plan（技術計畫）

### 技術堆疊

| 元件 | 選擇 | 理由 |
| --- | --- | --- |
| 模型載入 | `unsloth.FastLanguageModel` | 4-bit 量化 + 加速，T4 可跑 |
| 微調方法 | LoRA（r=16，全 attention + MLP 投影層） | 只訓練約 1% 參數 |
| RL 演算法 | `trl.GRPOTrainer` + `GRPOConfig` | 官方實作，支援自訂多個 reward func |
| 生成加速 | vLLM（`fast_inference=True`，可關） | GRPO 每步要生成多個 completion，生成是瓶頸 |
| 資料 | `datasets.load_dataset("openai/gsm8k", "main")` | 標準數學推理資料集 |

### 檔案結構

```
k26-ch25-practice/
├── spec.md      本檔
├── train.py     GRPO 訓練（含 5 個獎勵函式、--self-test 本機自測）
├── infer.py     載入 LoRA 推理（可對照基底模型）
├── README.md    Colab T4 執行步驟
└── NOTES.md     練習紀錄與和書上做法的差異
```

### 資料流

```
GSM8K question ──► system prompt + user 訊息（chat 格式）
                         │
                         ▼
          GRPOTrainer：每題生成 num_generations 個回答
                         │
                         ▼
          5 個 reward func 打分 → 組內相對優勢（GRPO）
                         │
                         ▼
                  更新 LoRA 權重 → outputs/grpo_lora/
```

### 預設超參數（T4）

| 參數 | 值 |
| --- | --- |
| `max_seq_length` | 1024 |
| `lora_rank` | 16 |
| `learning_rate` | 5e-6 |
| `per_device_train_batch_size` | 6（須能被 `num_generations` 整除） |
| `num_generations` | 6 |
| `max_prompt_length` / `max_completion_length` | 256 / 512 |
| `max_steps` | 250 |
| `optim` | `paged_adamw_8bit` |

---

## 4. Tasks（任務清單）

- [x] T1 寫 spec.md（本檔）
- [x] T2 `train.py`：設定區塊 + argparse
- [x] T3 `train.py`：GSM8K 載入與 chat 格式轉換、答案抽取
- [x] T4 `train.py`：5 個獎勵函式（純函式）
- [x] T5 `train.py`：Unsloth 載入模型 + LoRA
- [x] T6 `train.py`：GRPOConfig + GRPOTrainer + 儲存 LoRA
- [x] T7 `train.py --self-test`：不需 GPU 的獎勵函式自測
- [x] T8 `infer.py`：載入 LoRA、生成、解析答案、可選對照基底模型
- [x] T9 `README.md`：Colab T4 步驟
- [x] T10 本機 `python -m py_compile` 語法檢查
- [x] T11 `NOTES.md` 紀錄
- [ ] T12（Colab）實際訓練並記錄獎勵曲線 — 本機無 GPU，留待 Colab
