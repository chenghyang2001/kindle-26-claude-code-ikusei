"""用 GRPO 微調小型模型，讓它以 <reasoning>…</reasoning><answer>…</answer> 格式解 GSM8K。

執行環境：Google Colab T4（見 README.md）。
本機沒有 GPU 時可跑 `python train.py --self-test`，只測獎勵函式，不需要 torch／unsloth。

重套件（unsloth / trl / datasets / torch）刻意延後到函式內 import：
獎勵函式是純文字運算，這樣本機才能單獨驗證。
"""
import argparse
import re
import sys

# ---------------------------------------------------------------------------
# 設定區塊：預設值針對 Colab 免費 T4（16GB）調整
# ---------------------------------------------------------------------------
DEFAULT_MODEL = "unsloth/Qwen2.5-0.5B-Instruct"
DEFAULT_OUTPUT_DIR = "outputs/grpo_lora"
SEED = 3407

SYSTEM_PROMPT = """Respond in the following format:
<reasoning>
...
</reasoning>
<answer>
...
</answer>"""

# 獎勵分數集中在這裡，方便實驗時調整權重
CORRECT_SCORE = 2.0
INT_SCORE = 0.5
FORMAT_SCORE = 0.5
TAG_SCORE = 0.125

STRICT_FORMAT_RE = re.compile(
    r"^<reasoning>\n.*?\n</reasoning>\n<answer>\n.*?\n</answer>\n?$", re.DOTALL
)
SOFT_FORMAT_RE = re.compile(
    r"<reasoning>.*?</reasoning>\s*<answer>.*?</answer>", re.DOTALL
)
ANSWER_RE = re.compile(r"<answer>(.*?)</answer>", re.DOTALL)


# ---------------------------------------------------------------------------
# 答案抽取與正規化
# ---------------------------------------------------------------------------
def extract_xml_answer(text: str) -> str:
    """取出 <answer> 內文；沒有閉合標籤時取 <answer> 之後全部（截斷輸出也能部分評分）。"""
    match = ANSWER_RE.search(text)
    if match:
        return match.group(1).strip()
    if "<answer>" in text:
        return text.split("<answer>", 1)[1].strip()
    return ""


def extract_hash_answer(text: str) -> str | None:
    """GSM8K 標準答案放在 '#### ' 之後。"""
    if "####" not in text:
        return None
    return text.split("####", 1)[1].strip()


def normalize_number(text: str) -> str:
    """去掉逗號、貨幣符號、尾端句點，讓 '1,200.' 與 '1200' 視為相同。"""
    cleaned = text.strip().replace(",", "").replace("$", "").rstrip(".")
    try:
        value = float(cleaned)
    except ValueError:
        return cleaned
    # 3.50 與 3.5、12.0 與 12 都要能對上
    return str(int(value)) if value.is_integer() else str(value)


def completion_to_text(completion) -> str:
    """TRL 的 completion 可能是對話格式 [{'role','content'}] 或純字串。"""
    if isinstance(completion, str):
        return completion
    if isinstance(completion, list) and completion:
        first = completion[0]
        if isinstance(first, dict):
            return str(first.get("content") or "")
    return ""


# ---------------------------------------------------------------------------
# 獎勵函式：TRL 簽名為 (prompts, completions, **kwargs) -> list[float]
# 資料集的其他欄位（例如 answer）會以 kwargs 傳入
# ---------------------------------------------------------------------------
def correctness_reward(prompts, completions, answer, **kwargs) -> list[float]:
    """答案正確給 2.0 分——這是真正要優化的目標。"""
    responses = [extract_xml_answer(completion_to_text(c)) for c in completions]
    return [
        CORRECT_SCORE if normalize_number(r) == normalize_number(str(a)) else 0.0
        for r, a in zip(responses, answer)
    ]


def int_reward(completions, **kwargs) -> list[float]:
    """GSM8K 答案都是整數，先鼓勵模型在 <answer> 只放數字。"""
    responses = [extract_xml_answer(completion_to_text(c)) for c in completions]
    return [
        INT_SCORE if re.fullmatch(r"-?\d+", r.replace(",", "")) else 0.0
        for r in responses
    ]


def strict_format_reward(completions, **kwargs) -> list[float]:
    """完全符合含換行的嚴格格式才給分。"""
    texts = [completion_to_text(c) for c in completions]
    return [FORMAT_SCORE if STRICT_FORMAT_RE.match(t) else 0.0 for t in texts]


def soft_format_reward(completions, **kwargs) -> list[float]:
    """寬鬆格式：標籤順序對即可，讓訓練初期也有梯度訊號。"""
    texts = [completion_to_text(c) for c in completions]
    return [FORMAT_SCORE if SOFT_FORMAT_RE.search(t) else 0.0 for t in texts]


def count_xml(text: str) -> float:
    """每個標籤恰好出現一次各加分；</answer> 之後的多餘文字依長度扣分。"""
    score = 0.0
    for tag in ("<reasoning>\n", "\n</reasoning>\n", "\n<answer>\n", "\n</answer>"):
        if text.count(tag) == 1:
            score += TAG_SCORE
    if "\n</answer>" in text:
        trailing = text.split("\n</answer>", 1)[1]
        score -= len(trailing.strip()) * 0.001
    return score


def xml_count_reward(completions, **kwargs) -> list[float]:
    return [count_xml(completion_to_text(c)) for c in completions]


REWARD_FUNCS = [
    xml_count_reward,
    soft_format_reward,
    strict_format_reward,
    int_reward,
    correctness_reward,
]


# ---------------------------------------------------------------------------
# 資料集
# ---------------------------------------------------------------------------
def build_gsm8k_dataset(split: str = "train", limit: int | None = None):
    """把 GSM8K 轉成 chat 格式 prompt + 純數字 answer 欄位。"""
    from datasets import load_dataset

    try:
        raw = load_dataset("openai/gsm8k", "main", split=split)
    except Exception as e:  # datasets 的網路錯誤種類很多，統一包成可讀訊息
        raise RuntimeError(f"下載 GSM8K 失敗（請確認網路）：{e}") from e

    if limit is not None:
        raw = raw.select(range(min(limit, len(raw))))

    def to_chat(example):
        return {
            "prompt": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": example["question"]},
            ],
            "answer": extract_hash_answer(example["answer"]),
        }

    return raw.map(to_chat).filter(lambda ex: ex["answer"] is not None)


# ---------------------------------------------------------------------------
# 模型與訓練
# ---------------------------------------------------------------------------
def load_model(args):
    """Unsloth 4-bit 載入 + 套 LoRA。"""
    try:
        from unsloth import FastLanguageModel
    except ImportError as e:
        raise RuntimeError("找不到 unsloth，請在 Colab 先 `pip install unsloth vllm`") from e

    # 舊版 Unsloth（2025 初）需要先 patch TRL 的 GRPO；新版已內建，找不到就略過
    try:
        from unsloth import PatchFastRL

        PatchFastRL("GRPO", FastLanguageModel)
    except ImportError:
        pass

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=args.model,
        max_seq_length=args.max_seq_length,
        load_in_4bit=True,
        fast_inference=args.use_vllm,
        max_lora_rank=args.lora_rank,
        gpu_memory_utilization=0.6,  # 留記憶體給訓練，T4 設太高 vLLM 會 OOM
    )
    model = FastLanguageModel.get_peft_model(
        model,
        r=args.lora_rank,
        lora_alpha=args.lora_rank,
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
        ],
        use_gradient_checkpointing="unsloth",
        random_state=SEED,
    )
    return model, tokenizer


def build_trainer(model, tokenizer, dataset, args):
    from trl import GRPOConfig, GRPOTrainer

    if args.batch_size % args.num_generations != 0:
        raise ValueError(
            f"batch_size({args.batch_size}) 必須能被 num_generations({args.num_generations}) 整除"
        )

    config = GRPOConfig(
        output_dir="outputs",
        learning_rate=args.learning_rate,
        adam_beta1=0.9,
        adam_beta2=0.99,
        weight_decay=0.1,
        warmup_ratio=0.1,
        lr_scheduler_type="cosine",
        optim="paged_adamw_8bit",
        logging_steps=1,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=1,
        num_generations=args.num_generations,
        max_prompt_length=args.max_prompt_length,
        max_completion_length=args.max_completion_length,
        max_steps=args.max_steps,
        save_steps=args.max_steps,
        max_grad_norm=0.1,
        use_vllm=args.use_vllm,
        report_to="none",
        seed=SEED,
        fp16=True,  # T4 不支援 bf16
        bf16=False,
    )
    return GRPOTrainer(
        model=model,
        processing_class=tokenizer,
        reward_funcs=REWARD_FUNCS,
        args=config,
        train_dataset=dataset,
    )


def train(args):
    dataset = build_gsm8k_dataset("train", limit=args.limit)
    print(f"訓練資料：{len(dataset)} 題")
    model, tokenizer = load_model(args)
    trainer = build_trainer(model, tokenizer, dataset, args)
    trainer.train()
    model.save_pretrained(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    print(f"LoRA 已儲存到 {args.output_dir}")


# ---------------------------------------------------------------------------
# 本機自測（不需 GPU）
# ---------------------------------------------------------------------------
def self_test():
    good = "<reasoning>\n3 + 4 = 7\n</reasoning>\n<answer>\n7\n</answer>\n"
    loose = "<reasoning>3+4=7</reasoning> <answer>7</answer>"
    wrong = "<reasoning>\nguess\n</reasoning>\n<answer>\n8\n</answer>"
    bare = "The answer is 7."
    comps = [[{"role": "assistant", "content": t}] for t in (good, loose, wrong, bare)]
    answers = ["7"] * 4

    assert correctness_reward(None, comps, answers) == [2.0, 2.0, 0.0, 0.0]
    assert strict_format_reward(comps) == [0.5, 0.0, 0.5, 0.0]
    assert soft_format_reward(comps) == [0.5, 0.5, 0.5, 0.0]
    assert int_reward(comps) == [0.5, 0.5, 0.5, 0.0]
    assert xml_count_reward(comps)[0] == 0.5 and xml_count_reward(comps)[3] == 0.0
    # 邊界：正規化、純字串 completion、缺 <answer>
    assert normalize_number("1,200.") == "1200" and normalize_number("3.50") == "3.5"
    assert correctness_reward(None, ["<answer>$1,200</answer>"], ["1200"]) == [2.0]
    assert extract_xml_answer("no tags") == ""
    assert extract_hash_answer("blah\n#### 42") == "42"
    print("self-test 全部通過")


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="GRPO 訓練 GSM8K 推理格式")
    p.add_argument("--self-test", action="store_true", help="只測獎勵函式（不需 GPU）")
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    p.add_argument("--max-seq-length", type=int, default=1024)
    p.add_argument("--lora-rank", type=int, default=16)
    p.add_argument("--learning-rate", type=float, default=5e-6)
    p.add_argument("--batch-size", type=int, default=6)
    p.add_argument("--num-generations", type=int, default=6)
    p.add_argument("--max-prompt-length", type=int, default=256)
    p.add_argument("--max-completion-length", type=int, default=512)
    p.add_argument("--max-steps", type=int, default=250)
    p.add_argument("--limit", type=int, default=None, help="只取前 N 題（快速試跑）")
    p.add_argument("--no-vllm", dest="use_vllm", action="store_false", help="關閉 vLLM 生成加速")
    return p.parse_args(argv)


def main():
    args = parse_args()
    try:
        if args.self_test:
            self_test()
        else:
            train(args)
    except (RuntimeError, ValueError, AssertionError) as e:
        print(f"錯誤：{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
