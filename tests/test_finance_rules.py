import math
import unittest

from finance_rules import nonnegative_amount, positive_amount, redeemed_total


class AmountValidationTests(unittest.TestCase):
    def test_accepts_valid_amounts(self):
        self.assertEqual(nonnegative_amount(0), 0.0)
        self.assertEqual(positive_amount("250.50"), 250.5)

    def test_rejects_negative_zero_and_nonfinite_values(self):
        for value in (-1, math.inf, -math.inf, math.nan, "not-a-number"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                nonnegative_amount(value)
        with self.assertRaises(ValueError):
            positive_amount(0)


class PledgeRedemptionTests(unittest.TestCase):
    def test_partial_and_full_redemptions(self):
        self.assertEqual(redeemed_total(1000, 200, 300, "Pledge"), 500.0)
        self.assertEqual(redeemed_total(1000, 500, 500, "Pledge"), 1000.0)

    def test_rejects_overpayment_and_non_pledge_records(self):
        with self.assertRaises(ValueError):
            redeemed_total(1000, 800, 201, "Pledge")
        with self.assertRaises(ValueError):
            redeemed_total(1000, 1000, 1, "Cash")

    def test_rejects_zero_negative_invalid_and_nonfinite_payments(self):
        for value in (0, -1, "invalid", math.inf, math.nan):
            with self.subTest(value=value), self.assertRaises(ValueError):
                redeemed_total(1000, 100, value, "Pledge")


if __name__ == "__main__":
    unittest.main()
