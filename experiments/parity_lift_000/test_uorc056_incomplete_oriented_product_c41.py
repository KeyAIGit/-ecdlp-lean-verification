import unittest

from uorc056_incomplete_oriented_product_c41 import (
    SECP_N,
    antisymmetric_monomials,
    first_symmetric_degree_over_pairs,
    first_total_degree_over_rows,
    symmetric_monomials,
    total_monomials,
)


class IncompleteOrientedProductC41Tests(unittest.TestCase):
    def test_monomial_split(self) -> None:
        for degree in range(32):
            self.assertEqual(
                symmetric_monomials(degree) + antisymmetric_monomials(degree),
                total_monomials(degree),
            )

    def test_small_interpolation_thresholds(self) -> None:
        expected = {
            30: 7,
            78: 12,
            66: 11,
            126: 15,
            138: 16,
        }
        for rows, degree in expected.items():
            self.assertEqual(first_total_degree_over_rows(rows), degree)
            self.assertLessEqual(total_monomials(degree - 1), rows)
            self.assertLess(rows, total_monomials(degree))

    def test_secp_dimension_frontier(self) -> None:
        rows = SECP_N - 1
        pairs = rows // 2
        expected = 481231938336009023090067544955250113852
        self.assertEqual(first_total_degree_over_rows(rows), expected)
        self.assertEqual(first_symmetric_degree_over_pairs(pairs), expected)
        self.assertEqual(expected.bit_length(), 129)
        self.assertEqual(pairs.bit_length(), 255)


if __name__ == '__main__':
    unittest.main()
