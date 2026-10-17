# K26 第 25 章練習：用 GRPO 訓練會「先推理再回答」的小模型

用 **Unsloth + TRL GRPOTrainer** 微調 `Qwen2.5-0.5B-Instruct`（或 `Llama-3.2-1B-Instruct`），讓它解 GSM8K 數學題時輸出：

```
<reasoning>
...推理過程...
</reasoning>
<answer>
72
</answer>
```

規格見 [spec.md](spec.md)，練習紀錄見 [NOTES.md](NOTES.md)。

## 檔案

| 檔案 | 用途 |
| --- | --- |
| `train.py` | GRPO 訓練；含 5 個獎勵函式；`--self-test` 可在沒 GPU 的電腦測獎勵函式 |
| `infer.py` | 載入 LoRA 推理；`--compare` 對照基底模型；`--eval N` 算正確率 |
| `spec.md` | Spec Kit 四段規格（constitution／specify／plan／tasks） |

## 在 Google Colab T4 執行

1. **開新筆記本並切到 GPU**
   Colab →「執行階段」→「變更執行階段類型」→ 硬體加速器選 **T4 GPU** → 儲存。

2. **確認 GPU**

   ```python
   !nvidia-smi
   ```

3. **安裝套件**（約 3～5 分鐘；裝完若提示重新啟動就重新啟動）

   ```python
   !pip install -q unsloth vllm
   !pip install -q --upgrade trl datasets
   ```

4. **把程式放上 Colab**（二擇一）

   ```python
   # A. 從 GitHub clone（如果你有推上去）
   !git clone https://github.com/<你的帳號>/k26-ch25-practice.git
   %cd k26-ch25-practice
   ```

   或 B. 左側「檔案」面板直接上傳 `train.py`、`infer.py`。

5. **先自測獎勵函式**（幾秒鐘）

   ```python
   !python train.py --self-test
   ```

6. **快速試跑**（約 5 分鐘，確認整條流程能動）

   ```python
   !python train.py --limit 200 --max-steps 20
   ```

7. **正式訓練**（預設 250 步，T4 約 1 小時）

   ```python
   !python train.py
   # 換 Llama：!python train.py --model unsloth/Llama-3.2-1B-Instruct
   # vLLM 出錯時：!python train.py --no-vllm（會比較慢）
   ```

   觀察 log 中的 `reward` 欄位：前幾十步通常接近 0，之後格式獎勵會先上升，正確性獎勵較晚才上升。

8. **推理與評估**

   ```python
   !python infer.py --compare      # 同一題對照基底模型與 +LoRA
   !python infer.py --eval 50      # GSM8K test 前 50 題正確率
   ```

9. **（可選）下載 LoRA**

   ```python
   !zip -r grpo_lora.zip outputs/grpo_lora
   from google.colab import files; files.download("grpo_lora.zip")
   ```

## 常見問題

| 症狀 | 處理 |
| --- | --- |
| `CUDA out of memory` | 降 `--num-generations 4 --batch-size 4`，或 `--max-completion-length 256` |
| `batch_size 必須能被 num_generations 整除` | 兩個參數設成倍數關係（例如 4/4、8/4） |
| vLLM 安裝或初始化失敗 | 加 `--no-vllm` |
| `bf16` 相關錯誤 | T4 不支援 bf16，程式已固定 `fp16=True`；若換 A100 可自行改成 bf16 |
| reward 一直是 0 | 正常現象，0.5B 模型前 50～100 步常學不到格式；可多跑幾步或換 1B 模型 |

## 本機（無 GPU）能做的事

```bash
python -m py_compile train.py infer.py   # 語法檢查
python train.py --self-test              # 獎勵函式單元測試（不需要 torch）
```
