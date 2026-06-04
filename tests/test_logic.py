import unittest

from logic import And, Not, Or, ProofError, TheoremProver, Variable, prove


class LogicTests(unittest.TestCase):
    def test_modus_ponens_proof(self):
        p = Variable("P")
        q = Variable("Q")

        steps = prove([p, p >> q], q)

        self.assertEqual(steps[-1].expression, q)
        self.assertEqual(steps[-1].rule, "Modus Ponens")

    def test_conjunction_introduction(self):
        p = Variable("P")
        q = Variable("Q")

        steps = prove([p, q], And(p, q))

        self.assertEqual(steps[-1].expression, And(p, q))
        self.assertEqual(steps[-1].rule, "Conjunction Introduction")

    def test_conjunction_elimination(self):
        p = Variable("P")
        q = Variable("Q")

        steps = prove([And(p, q)], q)

        self.assertEqual(steps[-1].expression, q)
        self.assertEqual(steps[-1].rule, "Conjunction Elimination")

    def test_de_morgan(self):
        p = Variable("P")
        q = Variable("Q")

        steps = prove([And(Not(p), Not(q))], Not(Or(p, q)))

        self.assertEqual(steps[-1].expression, Not(Or(p, q)))
        self.assertEqual(steps[-1].rule, "De Morgan")

    def test_unprovable_goal_raises(self):
        p = Variable("P")
        q = Variable("Q")

        with self.assertRaises(ProofError):
            TheoremProver([p]).prove(q)


if __name__ == "__main__":
    unittest.main()
