# Module 1: Represenbtation of Logical Expressions

class LogicalExpression:
    """
    Base class for all logical expressions.
    Acts as a commom type maker
    """
    pass


class Variable(LogicalExpression):
    """
    Represents a propositional variable. (e.g., P, Q, R)
    """

    def __init__(self, name):
        """Constructor for the Variable class.
        e.g., p = Variable('P')
        """
        self.name = name

    def __repr__(self):
        """
        Returns the string representation of the variable, which is its own name.
        """
        return self.name


class Not(LogicalExpression):
    """
    Represents the negation of a logical expression (e.g., ¬P)"""

    def __init__(self, sub_expression):
        """Constructor for the Not class.
        e.g., not_p = Not(p)
        """
        self.sub_expression = sub_expression

    def __repr__(self):
        """
        Returns the string representation of the negation, which is '~' followed by the sub-expression.
        """
        return f"¬({self.sub_expression!r})"

    # --- Not class test --- #


class And(LogicalExpression):
    """
    Represents the conjunction of two Logical Expressions (e.g., P ^ Q)
    """


def test():
    p = Variable('P')
    q = Variable('Q')

    print(p)  # Output: P

    not_p = Not(p)
    print(not_p)  # Output: ¬(P)

    # Double negation test
    not_not_p = Not(not_p)
    print(not_not_p)  # Output: ¬(¬(P))


# Run the test
if __name__ == "__main__":
    test()
