"""示範用的小檔案：故意留幾個可以被分析出來的問題"""


def average(numbers):
    total = 0
    for n in numbers:
        total += n
    return total / len(numbers)  # 空清單會 ZeroDivisionError


def read_config(path):
    f = open(path)  # 沒有關閉檔案、沒指定 encoding
    return f.read()


if __name__ == "__main__":
    print(average([1, 2, 3]))
