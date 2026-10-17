"""載入 train.py 產生的 LoRA，對數學題做推理並解析 <answer>。

用法（Colab）：
    python infer.py --question "Natalia sold clips to 48 of her friends ..."
    python infer.py --eval 20          # 用 GSM8K test 前 20 題算正確率
    python infer.py --compare          # 同一題對照「基底模型」與「+LoRA」
"""
import argparse
import sys
from pathlib import Path

from train import (
    DEFAULT_OUTPUT_DIR,
    SYSTEM_PROMPT,
    build_gsm8k_dataset,
    extract_xml_answer,
    normalize_number,
)

DEFAULT_QUESTION = (
    "Natalia sold clips to 48 of her friends in April, and then she sold half "
    "as many clips in May. How many clips did Natalia sell altogether in April and May?"
)


def load_lora_model(lora_dir: str, max_seq_length: int):
    """Unsloth 可直接從 adapter 目錄載入（會依 adapter_config 自動抓基底模型）。"""
    if not Path(lora_dir).is_dir():
        raise FileNotFoundError(f"找不到 LoRA 目錄：{lora_dir}（請先跑 train.py）")
    try:
        from unsloth import FastLanguageModel
    except ImportError as e:
        raise RuntimeError("找不到 unsloth，請在 Colab 先 `pip install unsloth`") from e

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=lora_dir,
        max_seq_length=max_seq_length,
        load_in_4bit=True,
    )
    FastLanguageModel.for_inference(model)
    return model, tokenizer


def generate(model, tokenizer, question: str, max_new_tokens: int) -> str:
    import torch

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    input_ids = tokenizer.apply_chat_template(
        messages, add_generation_prompt=True, return_tensors="pt"
    ).to(model.device)
    with torch.no_grad():
        output = model.generate(
            input_ids=input_ids,
            max_new_tokens=max_new_tokens,
            do_sample=False,  # 評估用 greedy，結果才可重現
            pad_token_id=tokenizer.eos_token_id,
        )
    return tokenizer.decode(output[0][input_ids.shape[1]:], skip_special_tokens=True)


def run_single(model, tokenizer, args):
    text = generate(model, tokenizer, args.question, args.max_new_tokens)
    print("=== +LoRA 輸出 ===")
    print(text)
    print(f"\n解析答案：{extract_xml_answer(text) or '（無 <answer>）'}")

    if args.compare:
        # disable_adapter() 暫時關掉 LoRA，等同基底模型
        with model.disable_adapter():
            base_text = generate(model, tokenizer, args.question, args.max_new_tokens)
        print("\n=== 基底模型輸出 ===")
        print(base_text)
        print(f"\n解析答案：{extract_xml_answer(base_text) or '（無 <answer>）'}")


def run_eval(model, tokenizer, args):
    dataset = build_gsm8k_dataset("test", limit=args.eval)
    correct = formatted = 0
    for i, ex in enumerate(dataset, 1):
        question = ex["prompt"][-1]["content"]
        text = generate(model, tokenizer, question, args.max_new_tokens)
        pred = extract_xml_answer(text)
        formatted += int("<answer>" in text and "</answer>" in text)
        is_correct = normalize_number(pred) == normalize_number(ex["answer"])
        correct += int(is_correct)
        print(f"[{i}/{len(dataset)}] 預測={pred!r} 標準={ex['answer']} {'✓' if is_correct else '✗'}")
    total = len(dataset)
    print(f"\n正確率 {correct}/{total} = {correct / total:.1%}；格式完整 {formatted}/{total}")


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="載入 GRPO LoRA 推理 GSM8K")
    p.add_argument("--lora-dir", default=DEFAULT_OUTPUT_DIR)
    p.add_argument("--question", default=DEFAULT_QUESTION)
    p.add_argument("--max-seq-length", type=int, default=1024)
    p.add_argument("--max-new-tokens", type=int, default=512)
    p.add_argument("--compare", action="store_true", help="同時輸出基底模型結果")
    p.add_argument("--eval", type=int, default=0, help="用 GSM8K test 前 N 題評估")
    return p.parse_args(argv)


def main():
    args = parse_args()
    try:
        model, tokenizer = load_lora_model(args.lora_dir, args.max_seq_length)
        if args.eval > 0:
            run_eval(model, tokenizer, args)
        else:
            run_single(model, tokenizer, args)
    except (FileNotFoundError, RuntimeError) as e:
        print(f"錯誤：{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
