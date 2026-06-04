import unittest

from real_analysis import (
    AnalysisProofError,
    Constant,
    Continuity,
    Limit,
    NamedFunction,
    Variable,
    prove_continuity,
    prove_derivative,
    prove_limit,
)


class RealAnalysisTests(unittest.TestCase):
    def test_polynomial_limit(self):
        x = Variable("x")

        steps = prove_limit(x**2 + 3 * x + 2, point=1, expected_value=6)

        self.assertEqual(steps[-1].conclusion.value, 6)
        self.assertEqual(steps[-1].rule, "Sum Limit Theorem")

    def test_named_function_limit_from_assumption(self):
        f = NamedFunction("f")
        assumption = Limit(f, "x", 2, 5)

        steps = prove_limit(f + 1, point=2, expected_value=6, assumptions=[assumption])

        self.assertEqual(steps[0].conclusion, assumption)
        self.assertEqual(steps[-1].conclusion.value, 6)

    def test_quotient_limit_rejects_zero_denominator(self):
        x = Variable("x")

        with self.assertRaises(AnalysisProofError):
            prove_limit(1 / (x - 1), point=1)

    def test_polynomial_continuity(self):
        x = Variable("x")

        steps = prove_continuity(x**3 - 2 * x + 7, point=3)

        self.assertIn("continuous", repr(steps[-1].conclusion))
        self.assertEqual(steps[-1].rule, "Continuity of Sums")

    def test_continuity_uses_assumption_for_named_function(self):
        f = NamedFunction("f")
        x = Variable("x")
        assumption = Continuity(f, "x", 0)

        steps = prove_continuity(f * x, point=0, assumptions=[assumption])

        self.assertEqual(steps[0].conclusion, assumption)
        self.assertEqual(steps[-1].rule, "Continuity of Products")

    def test_polynomial_derivative(self):
        x = Variable("x")

        steps = prove_derivative(x**2 + 3 * x + 2, expected_derivative=2 * x + 3)

        self.assertEqual(steps[-1].conclusion.derivative, 2 * x + 3)
        self.assertEqual(steps[-1].rule, "Sum Derivative Rule")

    def test_named_function_derivative_requires_assumption(self):
        f = NamedFunction("f")

        with self.assertRaises(AnalysisProofError):
            prove_derivative(f)

    def test_constant_derivative(self):
        steps = prove_derivative(Constant(4), expected_derivative=0)

        self.assertEqual(steps[-1].conclusion.derivative, Constant(0))


if __name__ == "__main__":
    unittest.main()
