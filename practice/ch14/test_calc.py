"""calc.py 的測試（用 unittest，免安裝 pytest）"""
import unittest

from calc import average, last_n, median


class TestCalc(unittest.TestCase):
    def test_average_normal(self):
        self.assertEqual(average([1, 2, 3, 4]), 2.5)

    def test_average_empty(self):
        # 規格：空串列回傳 0.0，不應拋出 ZeroDivisionError
        self.assertEqual(average([]), 0.0)

    def test_last_n(self):
        self.assertEqual(last_n([1, 2, 3, 4, 5], 2), [4, 5])

    def test_last_n_zero(self):
        self.assertEqual(last_n([1, 2, 3], 0), [])

    def test_last_n_larger_than_length(self):
        self.assertEqual(last_n([1, 2, 3], 10), [1, 2, 3])

    def test_median_odd(self):
        self.assertEqual(median([1, 3, 2]), 2)

    def test_median_even(self):
        self.assertEqual(median([1, 2, 3, 4]), 2.5)

    def test_median_empty(self):
        self.assertEqual(median([]), 0.0)

    def test_median_unsorted_not_mutated(self):
        data = [5, 1, 4, 2, 3]
        self.assertEqual(median(data), 3)
        self.assertEqual(data, [5, 1, 4, 2, 3])


if __name__ == "__main__":
    unittest.main()
