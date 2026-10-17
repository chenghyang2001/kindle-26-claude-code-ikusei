"""簡易統計計算模組（K26 第 14 章練習：故意埋了 bug）"""
import argparse


def average(numbers):
    """回傳數字串列的平均值。"""
    if not numbers:
        return 0.0
    return sum(numbers) / len(numbers)


def median(numbers):
    """回傳數字串列的中位數；空串列回傳 0.0，不修改傳入的串列。"""
    if not numbers:
        return 0.0
    ordered = sorted(numbers)  # 用 sorted 產生新串列，避免改動呼叫端資料
    mid = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2


def last_n(numbers, n):
    """回傳串列最後 n 個元素。"""
    if n <= 0:
        return []
    return numbers[-n:]


def main(argv=None):
    """命令列入口：avg 算平均、last 取最後 n 個。"""
    parser = argparse.ArgumentParser(description="簡易統計計算工具")
    sub = parser.add_subparsers(dest="command", required=True, help="子命令")

    avg_parser = sub.add_parser("avg", help="計算數字的平均值")
    avg_parser.add_argument("numbers", nargs="+", type=float, help="要計算的數字")

    last_parser = sub.add_parser("last", help="取最後 n 個數字（先 n，再數字）")
    last_parser.add_argument("n", type=int, help="要取的個數")
    last_parser.add_argument("numbers", nargs="+", type=float, help="數字串列")

    args = parser.parse_args(argv)
    if args.command == "avg":
        print(average(args.numbers))
    else:
        print(last_n(args.numbers, args.n))


if __name__ == "__main__":
    main()
