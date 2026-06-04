"""Educational real-analysis prover for limits of real-valued functions.

This module proves a useful fragment of real analysis: limit, continuity, and
derivative theorems for expressions built from constants, the identity function,
named functions with supplied assumptions, sums, differences, products,
quotients, and integer powers.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Sequence


class AnalysisProofError(Exception):
    """Raised when an analysis theorem cannot be proved by this prover."""


def to_fraction(value: int | float | str | Fraction) -> Fraction:
    """Convert supported numeric inputs to an exact rational value."""

    if isinstance(value, Fraction):
        return value
    if isinstance(value, float):
        return Fraction(value).limit_denominator()
    return Fraction(value)


def format_number(value: Fraction) -> str:
    """Format a rational number compactly for proof output."""

    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def as_expression(value: RealExpression | int | float | str | Fraction) -> RealExpression:
    """Coerce Python numeric values into real expressions."""

    if isinstance(value, RealExpression):
        return value
    return Constant(value)


@dataclass(frozen=True)
class RealExpression:
    """Base class for symbolic real expressions."""

    def __add__(self, other: RealExpression | int | float | str | Fraction) -> Add:
        return Add(self, as_expression(other))

    def __radd__(self, other: RealExpression | int | float | str | Fraction) -> Add:
        return Add(as_expression(other), self)

    def __sub__(self, other: RealExpression | int | float | str | Fraction) -> Subtract:
        return Subtract(self, as_expression(other))

    def __rsub__(self, other: RealExpression | int | float | str | Fraction) -> Subtract:
        return Subtract(as_expression(other), self)

    def __mul__(self, other: RealExpression | int | float | str | Fraction) -> Multiply:
        return Multiply(self, as_expression(other))

    def __rmul__(self, other: RealExpression | int | float | str | Fraction) -> Multiply:
        return Multiply(as_expression(other), self)

    def __truediv__(
        self, other: RealExpression | int | float | str | Fraction
    ) -> Divide:
        return Divide(self, as_expression(other))

    def __rtruediv__(
        self, other: RealExpression | int | float | str | Fraction
    ) -> Divide:
        return Divide(as_expression(other), self)

    def __pow__(self, exponent: int) -> Power:
        if not isinstance(exponent, int):
            raise TypeError("Only integer powers are supported.")
        return Power(self, exponent)


@dataclass(frozen=True)
class Constant(RealExpression):
    """A constant real expression."""

    value: Fraction | int | float | str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", to_fraction(self.value))

    def __repr__(self) -> str:
        return format_number(self.value)


@dataclass(frozen=True)
class Variable(RealExpression):
    """The identity expression for a real variable."""

    name: str = "x"

    def __repr__(self) -> str:
        return self.name


@dataclass(frozen=True)
class NamedFunction(RealExpression):
    """An uninterpreted real function whose limit may be provided as a premise."""

    name: str
    variable: str = "x"

    def __repr__(self) -> str:
        return f"{self.name}({self.variable})"


@dataclass(frozen=True, repr=False)
class BinaryRealExpression(RealExpression):
    """Base class for binary real expressions."""

    left: RealExpression
    right: RealExpression
    symbol: str = "?"

    def __repr__(self) -> str:
        return f"({self.left!r} {self.symbol} {self.right!r})"


@dataclass(frozen=True, repr=False)
class Add(BinaryRealExpression):
    """A sum of two real expressions."""

    symbol: str = "+"


@dataclass(frozen=True, repr=False)
class Subtract(BinaryRealExpression):
    """A difference of two real expressions."""

    symbol: str = "-"


@dataclass(frozen=True, repr=False)
class Multiply(BinaryRealExpression):
    """A product of two real expressions."""

    symbol: str = "*"


@dataclass(frozen=True, repr=False)
class Divide(BinaryRealExpression):
    """A quotient of two real expressions."""

    symbol: str = "/"


@dataclass(frozen=True)
class Power(RealExpression):
    """A non-negative integer power of a real expression."""

    base: RealExpression
    exponent: int

    def __post_init__(self) -> None:
        if self.exponent < 0:
            raise ValueError("Negative powers are represented with division.")

    def __repr__(self) -> str:
        return f"({self.base!r}^{self.exponent})"


def simplify(expression: RealExpression) -> RealExpression:
    """Simplify symbolic real expressions enough for readable proofs."""

    if isinstance(expression, (Constant, Variable, NamedFunction)):
        return expression

    if isinstance(expression, Add):
        left = simplify(expression.left)
        right = simplify(expression.right)
        if isinstance(left, Constant) and left.value == 0:
            return right
        if isinstance(right, Constant) and right.value == 0:
            return left
        if isinstance(left, Constant) and isinstance(right, Constant):
            return Constant(left.value + right.value)
        return Add(left, right)

    if isinstance(expression, Subtract):
        left = simplify(expression.left)
        right = simplify(expression.right)
        if isinstance(right, Constant) and right.value == 0:
            return left
        if isinstance(left, Constant) and isinstance(right, Constant):
            return Constant(left.value - right.value)
        return Subtract(left, right)

    if isinstance(expression, Multiply):
        left = simplify(expression.left)
        right = simplify(expression.right)
        if isinstance(left, Constant) and left.value == 0:
            return Constant(0)
        if isinstance(right, Constant) and right.value == 0:
            return Constant(0)
        if isinstance(left, Constant) and left.value == 1:
            return right
        if isinstance(right, Constant) and right.value == 1:
            return left
        if isinstance(left, Constant) and isinstance(right, Constant):
            return Constant(left.value * right.value)
        return Multiply(left, right)

    if isinstance(expression, Divide):
        left = simplify(expression.left)
        right = simplify(expression.right)
        if isinstance(left, Constant) and left.value == 0:
            return Constant(0)
        if isinstance(right, Constant) and right.value == 1:
            return left
        if isinstance(left, Constant) and isinstance(right, Constant):
            if right.value == 0:
                return Divide(left, right)
            return Constant(left.value / right.value)
        return Divide(left, right)

    if isinstance(expression, Power):
        base = simplify(expression.base)
        if expression.exponent == 0:
            return Constant(1)
        if expression.exponent == 1:
            return base
        if isinstance(base, Constant):
            return Constant(base.value**expression.exponent)
        return Power(base, expression.exponent)

    return expression


@dataclass(frozen=True)
class Limit:
    """A theorem statement: lim_{variable -> point} expression = value."""

    expression: RealExpression
    variable: str
    point: Fraction | int | float | str
    value: Fraction | int | float | str

    def __post_init__(self) -> None:
        object.__setattr__(self, "point", to_fraction(self.point))
        object.__setattr__(self, "value", to_fraction(self.value))

    def key_without_value(self) -> tuple[RealExpression, str, Fraction]:
        return (self.expression, self.variable, self.point)

    def __repr__(self) -> str:
        point = format_number(self.point)
        value = format_number(self.value)
        return f"lim_{{{self.variable}->{point}}} {self.expression!r} = {value}"


@dataclass(frozen=True)
class Continuity:
    """A theorem statement: an expression is continuous at a point."""

    expression: RealExpression
    variable: str
    point: Fraction | int | float | str

    def __post_init__(self) -> None:
        object.__setattr__(self, "point", to_fraction(self.point))

    def key(self) -> tuple[RealExpression, str, Fraction]:
        return (self.expression, self.variable, self.point)

    def __repr__(self) -> str:
        point = format_number(self.point)
        return f"{self.expression!r} is continuous at {self.variable} = {point}"


@dataclass(frozen=True)
class Derivative:
    """A theorem statement: d/dvariable expression = derivative."""

    expression: RealExpression
    variable: str
    derivative: RealExpression

    def __post_init__(self) -> None:
        object.__setattr__(self, "derivative", simplify(self.derivative))

    def key_without_derivative(self) -> tuple[RealExpression, str]:
        return (self.expression, self.variable)

    def __repr__(self) -> str:
        return f"d/d{self.variable} {self.expression!r} = {self.derivative!r}"


AnalysisStatement = Limit | Continuity | Derivative


@dataclass(frozen=True)
class AnalysisProofStep:
    """One step in a real-analysis proof."""

    conclusion: AnalysisStatement
    rule: str
    premises: tuple[AnalysisStatement, ...] = ()

    def __repr__(self) -> str:
        if not self.premises:
            return f"{self.conclusion!r}    [{self.rule}]"
        premises = ", ".join(repr(premise) for premise in self.premises)
        return f"{self.conclusion!r}    [{self.rule}: {premises}]"


class RealAnalysisProver:
    """Proves real-analysis statements by recursively applying theorem schemas."""

    def __init__(self, assumptions: Sequence[AnalysisStatement] | None = None):
        self.steps: dict[AnalysisStatement, AnalysisProofStep] = {}
        self.limit_assumptions_by_key: dict[
            tuple[RealExpression, str, Fraction], Limit
        ] = {}
        self.continuity_assumptions_by_key: dict[
            tuple[RealExpression, str, Fraction], Continuity
        ] = {}
        self.derivative_assumptions_by_key: dict[
            tuple[RealExpression, str], Derivative
        ] = {}

        for assumption in assumptions or ():
            if isinstance(assumption, Limit):
                self.limit_assumptions_by_key[assumption.key_without_value()] = assumption
            elif isinstance(assumption, Continuity):
                self.continuity_assumptions_by_key[assumption.key()] = assumption
            elif isinstance(assumption, Derivative):
                self.derivative_assumptions_by_key[
                    assumption.key_without_derivative()
                ] = assumption
            self._record(assumption, "Assumption", ())

    def prove_limit(
        self,
        expression: RealExpression,
        *,
        variable: str = "x",
        point: int | float | str | Fraction = 0,
        expected_value: int | float | str | Fraction | None = None,
    ) -> list[AnalysisProofStep]:
        """Prove the limit of an expression at a point.

        When ``expected_value`` is supplied, the prover checks that the derived
        value matches it.
        """

        theorem = self._prove(expression, variable, to_fraction(point), stack=())
        if expected_value is not None and theorem.value != to_fraction(expected_value):
            raise AnalysisProofError(
                f"Derived {theorem!r}, not the expected value {expected_value!r}."
            )
        return self._linearize(theorem)

    def prove_theorem(self, theorem: Limit) -> list[AnalysisProofStep]:
        """Prove an explicitly stated limit theorem."""

        return self.prove_limit(
            theorem.expression,
            variable=theorem.variable,
            point=theorem.point,
            expected_value=theorem.value,
        )

    def prove_continuity(
        self,
        expression: RealExpression,
        *,
        variable: str = "x",
        point: int | float | str | Fraction = 0,
    ) -> list[AnalysisProofStep]:
        """Prove that an expression is continuous at a point."""

        theorem = self._prove_continuity(expression, variable, to_fraction(point), ())
        return self._linearize(theorem)

    def prove_derivative(
        self,
        expression: RealExpression,
        *,
        variable: str = "x",
        expected_derivative: RealExpression | int | float | str | Fraction | None = None,
    ) -> list[AnalysisProofStep]:
        """Prove a symbolic derivative theorem."""

        theorem = self._prove_derivative(expression, variable, ())
        if expected_derivative is not None:
            expected = simplify(as_expression(expected_derivative))
            if theorem.derivative != expected:
                raise AnalysisProofError(
                    f"Derived {theorem!r}, not the expected derivative {expected!r}."
                )
        return self._linearize(theorem)

    def _prove(
        self,
        expression: RealExpression,
        variable: str,
        point: Fraction,
        stack: tuple[tuple[RealExpression, str, Fraction], ...],
    ) -> Limit:
        key = (expression, variable, point)
        if key in stack:
            raise AnalysisProofError(f"Cyclic proof search while proving {expression!r}.")

        assumption = self.limit_assumptions_by_key.get(key)
        if assumption is not None:
            return assumption

        if isinstance(expression, Constant):
            return self._record_and_return(
                Limit(expression, variable, point, expression.value),
                "Constant Limit Law",
                (),
            )

        if isinstance(expression, Variable):
            if expression.name != variable:
                assumption = self.limit_assumptions_by_key.get(key)
                if assumption is not None:
                    return assumption
                raise AnalysisProofError(
                    f"No assumption was provided for variable {expression.name!r} "
                    f"as {variable} approaches {format_number(point)}."
                )
            return self._record_and_return(
                Limit(expression, variable, point, point),
                "Identity Limit Law",
                (),
            )

        if isinstance(expression, NamedFunction):
            raise AnalysisProofError(
                f"No limit assumption was provided for {expression!r} as "
                f"{variable} approaches {format_number(point)}."
            )

        next_stack = (*stack, key)

        if isinstance(expression, Add):
            left = self._prove(expression.left, variable, point, next_stack)
            right = self._prove(expression.right, variable, point, next_stack)
            return self._record_and_return(
                Limit(expression, variable, point, left.value + right.value),
                "Sum Limit Theorem",
                (left, right),
            )

        if isinstance(expression, Subtract):
            left = self._prove(expression.left, variable, point, next_stack)
            right = self._prove(expression.right, variable, point, next_stack)
            return self._record_and_return(
                Limit(expression, variable, point, left.value - right.value),
                "Difference Limit Theorem",
                (left, right),
            )

        if isinstance(expression, Multiply):
            left = self._prove(expression.left, variable, point, next_stack)
            right = self._prove(expression.right, variable, point, next_stack)
            return self._record_and_return(
                Limit(expression, variable, point, left.value * right.value),
                "Product Limit Theorem",
                (left, right),
            )

        if isinstance(expression, Divide):
            left = self._prove(expression.left, variable, point, next_stack)
            right = self._prove(expression.right, variable, point, next_stack)
            if right.value == 0:
                raise AnalysisProofError(
                    f"Cannot apply the quotient theorem because {right!r}."
                )
            return self._record_and_return(
                Limit(expression, variable, point, left.value / right.value),
                "Quotient Limit Theorem",
                (left, right),
            )

        if isinstance(expression, Power):
            base = self._prove(expression.base, variable, point, next_stack)
            return self._record_and_return(
                Limit(expression, variable, point, base.value**expression.exponent),
                "Power Limit Theorem",
                (base,),
            )

        raise AnalysisProofError(f"Unsupported real expression: {expression!r}.")

    def _prove_continuity(
        self,
        expression: RealExpression,
        variable: str,
        point: Fraction,
        stack: tuple[tuple[RealExpression, str, Fraction], ...],
    ) -> Continuity:
        key = (expression, variable, point)
        if key in stack:
            raise AnalysisProofError(
                f"Cyclic proof search while proving continuity of {expression!r}."
            )

        assumption = self.continuity_assumptions_by_key.get(key)
        if assumption is not None:
            return assumption

        if isinstance(expression, Constant):
            return self._record_statement(
                Continuity(expression, variable, point),
                "Constant Function Continuity",
                (),
            )

        if isinstance(expression, Variable):
            if expression.name != variable:
                raise AnalysisProofError(
                    f"No continuity assumption was provided for {expression!r}."
                )
            return self._record_statement(
                Continuity(expression, variable, point),
                "Identity Function Continuity",
                (),
            )

        if isinstance(expression, NamedFunction):
            raise AnalysisProofError(
                f"No continuity assumption was provided for {expression!r} at "
                f"{variable} = {format_number(point)}."
            )

        next_stack = (*stack, key)

        if isinstance(expression, (Add, Subtract, Multiply)):
            left = self._prove_continuity(expression.left, variable, point, next_stack)
            right = self._prove_continuity(expression.right, variable, point, next_stack)
            rule = {
                Add: "Continuity of Sums",
                Subtract: "Continuity of Differences",
                Multiply: "Continuity of Products",
            }[type(expression)]
            return self._record_statement(
                Continuity(expression, variable, point),
                rule,
                (left, right),
            )

        if isinstance(expression, Divide):
            left = self._prove_continuity(expression.left, variable, point, next_stack)
            right = self._prove_continuity(expression.right, variable, point, next_stack)
            denominator_limit = self._prove(expression.right, variable, point, next_stack)
            if denominator_limit.value == 0:
                raise AnalysisProofError(
                    "Cannot prove quotient continuity because the denominator "
                    f"has limit 0: {denominator_limit!r}."
                )
            return self._record_statement(
                Continuity(expression, variable, point),
                "Continuity of Quotients",
                (left, right, denominator_limit),
            )

        if isinstance(expression, Power):
            base = self._prove_continuity(expression.base, variable, point, next_stack)
            return self._record_statement(
                Continuity(expression, variable, point),
                "Continuity of Integer Powers",
                (base,),
            )

        raise AnalysisProofError(
            f"Unsupported real expression for continuity: {expression!r}."
        )

    def _prove_derivative(
        self,
        expression: RealExpression,
        variable: str,
        stack: tuple[tuple[RealExpression, str], ...],
    ) -> Derivative:
        key = (expression, variable)
        if key in stack:
            raise AnalysisProofError(
                f"Cyclic proof search while proving derivative of {expression!r}."
            )

        assumption = self.derivative_assumptions_by_key.get(key)
        if assumption is not None:
            return assumption

        if isinstance(expression, Constant):
            return self._record_statement(
                Derivative(expression, variable, Constant(0)),
                "Constant Derivative Rule",
                (),
            )

        if isinstance(expression, Variable):
            derivative = Constant(1 if expression.name == variable else 0)
            return self._record_statement(
                Derivative(expression, variable, derivative),
                "Identity Derivative Rule",
                (),
            )

        if isinstance(expression, NamedFunction):
            raise AnalysisProofError(
                f"No derivative assumption was provided for {expression!r}."
            )

        next_stack = (*stack, key)

        if isinstance(expression, Add):
            left = self._prove_derivative(expression.left, variable, next_stack)
            right = self._prove_derivative(expression.right, variable, next_stack)
            return self._record_statement(
                Derivative(
                    expression,
                    variable,
                    simplify(left.derivative + right.derivative),
                ),
                "Sum Derivative Rule",
                (left, right),
            )

        if isinstance(expression, Subtract):
            left = self._prove_derivative(expression.left, variable, next_stack)
            right = self._prove_derivative(expression.right, variable, next_stack)
            return self._record_statement(
                Derivative(
                    expression,
                    variable,
                    simplify(left.derivative - right.derivative),
                ),
                "Difference Derivative Rule",
                (left, right),
            )

        if isinstance(expression, Multiply):
            left = self._prove_derivative(expression.left, variable, next_stack)
            right = self._prove_derivative(expression.right, variable, next_stack)
            derivative = simplify(
                left.derivative * expression.right + expression.left * right.derivative
            )
            return self._record_statement(
                Derivative(expression, variable, derivative),
                "Product Derivative Rule",
                (left, right),
            )

        if isinstance(expression, Divide):
            left = self._prove_derivative(expression.left, variable, next_stack)
            right = self._prove_derivative(expression.right, variable, next_stack)
            derivative = simplify(
                (left.derivative * expression.right - expression.left * right.derivative)
                / (expression.right**2)
            )
            return self._record_statement(
                Derivative(expression, variable, derivative),
                "Quotient Derivative Rule",
                (left, right),
            )

        if isinstance(expression, Power):
            base = self._prove_derivative(expression.base, variable, next_stack)
            coefficient = Constant(expression.exponent)
            derivative = simplify(
                coefficient * (expression.base ** (expression.exponent - 1))
                * base.derivative
            )
            return self._record_statement(
                Derivative(expression, variable, derivative),
                "Power Derivative Rule",
                (base,),
            )

        raise AnalysisProofError(
            f"Unsupported real expression for derivatives: {expression!r}."
        )

    def _record_and_return(
        self,
        theorem: Limit,
        rule: str,
        premises: Sequence[Limit],
    ) -> Limit:
        self._record(theorem, rule, premises)
        return theorem

    def _record(
        self,
        theorem: AnalysisStatement,
        rule: str,
        premises: Sequence[AnalysisStatement],
    ) -> None:
        if theorem not in self.steps:
            self.steps[theorem] = AnalysisProofStep(theorem, rule, tuple(premises))

    def _record_statement(
        self,
        theorem: Continuity | Derivative,
        rule: str,
        premises: Sequence[AnalysisStatement],
    ) -> Continuity | Derivative:
        self._record(theorem, rule, premises)
        return theorem

    def _linearize(self, theorem: AnalysisStatement) -> list[AnalysisProofStep]:
        ordered: list[AnalysisProofStep] = []
        visited: set[AnalysisStatement] = set()

        def visit(current: AnalysisStatement) -> None:
            if current in visited:
                return
            step = self.steps[current]
            for premise in step.premises:
                visit(premise)
            visited.add(current)
            ordered.append(step)

        visit(theorem)
        return ordered


def prove_limit(
    expression: RealExpression,
    *,
    variable: str = "x",
    point: int | float | str | Fraction = 0,
    expected_value: int | float | str | Fraction | None = None,
    assumptions: Sequence[Limit] | None = None,
) -> list[AnalysisProofStep]:
    """Convenience wrapper around ``RealAnalysisProver``."""

    return RealAnalysisProver(assumptions).prove_limit(
        expression,
        variable=variable,
        point=point,
        expected_value=expected_value,
    )


def prove_continuity(
    expression: RealExpression,
    *,
    variable: str = "x",
    point: int | float | str | Fraction = 0,
    assumptions: Sequence[AnalysisStatement] | None = None,
) -> list[AnalysisProofStep]:
    """Convenience wrapper for continuity proofs."""

    return RealAnalysisProver(assumptions).prove_continuity(
        expression,
        variable=variable,
        point=point,
    )


def prove_derivative(
    expression: RealExpression,
    *,
    variable: str = "x",
    expected_derivative: RealExpression | int | float | str | Fraction | None = None,
    assumptions: Sequence[AnalysisStatement] | None = None,
) -> list[AnalysisProofStep]:
    """Convenience wrapper for derivative proofs."""

    return RealAnalysisProver(assumptions).prove_derivative(
        expression,
        variable=variable,
        expected_derivative=expected_derivative,
    )


def format_analysis_proof(steps: Sequence[AnalysisProofStep]) -> str:
    """Format analysis proof steps as a numbered text block."""

    return "\n".join(f"{index}. {step!r}" for index, step in enumerate(steps, 1))


def _demo() -> None:
    x = Variable("x")
    expression = x**2 + 3 * x + 2

    print("Limit theorem")
    print(format_analysis_proof(prove_limit(expression, point=1, expected_value=6)))
    print()
    print("Derivative theorem")
    print(format_analysis_proof(prove_derivative(expression)))


if __name__ == "__main__":
    _demo()
