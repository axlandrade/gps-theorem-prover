"""A small GPS-style theorem prover for propositional logic.

The module exposes immutable expression objects and a recursive prover that
uses means-ends analysis: to prove a goal, it looks for inference rules that can
make the goal true and recursively proves each rule premise.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence


class ProofError(Exception):
    """Raised when a theorem cannot be proved from the provided axioms."""


@dataclass(frozen=True)
class LogicalExpression:
    """Base class for all logical expressions."""

    def __and__(self, other: LogicalExpression) -> And:
        return And(self, other)

    def __or__(self, other: LogicalExpression) -> Or:
        return Or(self, other)

    def __invert__(self) -> Not:
        return Not(self)

    def implies(self, other: LogicalExpression) -> Implies:
        return Implies(self, other)

    def __rshift__(self, other: LogicalExpression) -> Implies:
        return self.implies(other)

    def variables(self) -> frozenset[Variable]:
        """Return the variables used by this expression."""

        return frozenset()


@dataclass(frozen=True)
class Variable(LogicalExpression):
    """Represents a propositional variable, for example P, Q, or R."""

    name: str

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Variable name cannot be empty.")

    def __repr__(self) -> str:
        return self.name

    def variables(self) -> frozenset[Variable]:
        return frozenset({self})


@dataclass(frozen=True)
class Not(LogicalExpression):
    """Represents negation, for example ¬P."""

    expression: LogicalExpression

    @property
    def sub_expression(self) -> LogicalExpression:
        """Backward-compatible alias used by the first project draft."""

        return self.expression

    def __repr__(self) -> str:
        return f"¬({self.expression!r})"

    def variables(self) -> frozenset[Variable]:
        return self.expression.variables()


@dataclass(frozen=True, repr=False)
class BinaryExpression(LogicalExpression):
    """Base class for binary logical expressions."""

    left: LogicalExpression
    right: LogicalExpression
    symbol: str = "?"

    def __repr__(self) -> str:
        return f"({self.left!r} {self.symbol} {self.right!r})"

    def variables(self) -> frozenset[Variable]:
        return self.left.variables() | self.right.variables()


@dataclass(frozen=True, repr=False)
class And(BinaryExpression):
    """Represents conjunction, for example P ∧ Q."""

    symbol: str = "∧"


@dataclass(frozen=True, repr=False)
class Or(BinaryExpression):
    """Represents disjunction, for example P ∨ Q."""

    symbol: str = "∨"


@dataclass(frozen=True, repr=False)
class Implies(BinaryExpression):
    """Represents implication, for example P -> Q."""

    symbol: str = "->"


@dataclass(frozen=True)
class ProofStep:
    """One step in a generated proof."""

    expression: LogicalExpression
    rule: str
    premises: tuple[LogicalExpression, ...] = ()

    def __repr__(self) -> str:
        if not self.premises:
            return f"{self.expression!r}    [{self.rule}]"
        premises = ", ".join(repr(premise) for premise in self.premises)
        return f"{self.expression!r}    [{self.rule}: {premises}]"


class TheoremProver:
    """GPS-style theorem prover for a compact propositional logic fragment."""

    def __init__(self, axioms: Iterable[LogicalExpression], *, max_depth: int = 12):
        self.max_depth = max_depth
        self.steps: dict[LogicalExpression, ProofStep] = {}
        for axiom in axioms:
            self._record(axiom, "Axiom", ())
        self._saturate_known_facts()

    def prove(self, goal: LogicalExpression) -> list[ProofStep]:
        """Return a step-by-step proof for ``goal`` or raise ``ProofError``."""

        if not self._achieve(goal, depth=0, stack=()):
            raise ProofError(f"Could not prove {goal!r} from the provided axioms.")

        return self._linearize(goal)

    def can_prove(self, goal: LogicalExpression) -> bool:
        """Return whether ``goal`` can be proved from the current axioms."""

        try:
            self.prove(goal)
        except ProofError:
            return False
        return True

    def _achieve(
        self,
        goal: LogicalExpression,
        *,
        depth: int,
        stack: tuple[LogicalExpression, ...],
    ) -> bool:
        if goal in self.steps:
            return True
        if depth >= self.max_depth or goal in stack:
            return False

        next_stack = (*stack, goal)

        for premise in self._known_conjunctions_containing(goal):
            if self._achieve(premise, depth=depth + 1, stack=next_stack):
                self._saturate_known_facts()
                if goal in self.steps:
                    return True

        if isinstance(goal, And):
            if self._achieve(goal.left, depth=depth + 1, stack=next_stack) and (
                self._achieve(goal.right, depth=depth + 1, stack=next_stack)
            ):
                self._record(goal, "Conjunction Introduction", (goal.left, goal.right))
                self._saturate_known_facts()
                return True

        if isinstance(goal, Or):
            if self._achieve(goal.left, depth=depth + 1, stack=next_stack):
                self._record(goal, "Disjunction Introduction", (goal.left,))
                return True
            if self._achieve(goal.right, depth=depth + 1, stack=next_stack):
                self._record(goal, "Disjunction Introduction", (goal.right,))
                return True

        if isinstance(goal, Not) and isinstance(goal.expression, Not):
            inner = goal.expression.expression
            if self._achieve(inner, depth=depth + 1, stack=next_stack):
                self._record(goal, "Double Negation Introduction", (inner,))
                return True

        for implication in self._implications_with_conclusion(goal):
            if self._achieve(implication.left, depth=depth + 1, stack=next_stack):
                self._record(goal, "Modus Ponens", (implication.left, implication))
                self._saturate_known_facts()
                return True

        for de_morgan_source in self._de_morgan_sources_for(goal):
            if self._achieve(de_morgan_source, depth=depth + 1, stack=next_stack):
                self._record(goal, "De Morgan", (de_morgan_source,))
                self._saturate_known_facts()
                return True

        for double_negative in self._double_negative_sources_for(goal):
            if self._achieve(double_negative, depth=depth + 1, stack=next_stack):
                self._record(goal, "Double Negation Elimination", (double_negative,))
                self._saturate_known_facts()
                return True

        return False

    def _saturate_known_facts(self) -> None:
        """Apply rules that do not need search until no new facts appear."""

        changed = True
        while changed:
            changed = False
            known = tuple(self.steps)

            for expression in known:
                if isinstance(expression, And):
                    changed |= self._record(
                        expression.left, "Conjunction Elimination", (expression,)
                    )
                    changed |= self._record(
                        expression.right, "Conjunction Elimination", (expression,)
                    )

                if isinstance(expression, Not) and isinstance(expression.expression, Not):
                    changed |= self._record(
                        expression.expression.expression,
                        "Double Negation Elimination",
                        (expression,),
                    )

                for result in self._de_morgan_results(expression):
                    changed |= self._record(result, "De Morgan", (expression,))

            known = tuple(self.steps)
            implications = [expr for expr in known if isinstance(expr, Implies)]
            for implication in implications:
                if implication.left in self.steps:
                    changed |= self._record(
                        implication.right,
                        "Modus Ponens",
                        (implication.left, implication),
                    )

    def _record(
        self,
        expression: LogicalExpression,
        rule: str,
        premises: Sequence[LogicalExpression],
    ) -> bool:
        if expression in self.steps:
            return False
        self.steps[expression] = ProofStep(expression, rule, tuple(premises))
        return True

    def _linearize(self, goal: LogicalExpression) -> list[ProofStep]:
        ordered: list[ProofStep] = []
        visited: set[LogicalExpression] = set()

        def visit(expression: LogicalExpression) -> None:
            if expression in visited:
                return
            step = self.steps[expression]
            for premise in step.premises:
                visit(premise)
            visited.add(expression)
            ordered.append(step)

        visit(goal)
        return ordered

    def _implications_with_conclusion(
        self, goal: LogicalExpression
    ) -> list[Implies]:
        return [
            expression
            for expression in self.steps
            if isinstance(expression, Implies) and expression.right == goal
        ]

    def _known_conjunctions_containing(
        self, goal: LogicalExpression
    ) -> list[LogicalExpression]:
        return [
            expression
            for expression in self.steps
            if isinstance(expression, And)
            and (expression.left == goal or expression.right == goal)
        ]

    def _double_negative_sources_for(
        self, goal: LogicalExpression
    ) -> list[LogicalExpression]:
        return [Not(Not(goal))]

    def _de_morgan_sources_for(
        self, goal: LogicalExpression
    ) -> list[LogicalExpression]:
        if isinstance(goal, Not) and isinstance(goal.expression, Or):
            return [And(Not(goal.expression.left), Not(goal.expression.right))]
        if isinstance(goal, Not) and isinstance(goal.expression, And):
            return [Or(Not(goal.expression.left), Not(goal.expression.right))]
        if isinstance(goal, And) and self._both_sides_are_negated(goal):
            return [Not(Or(Not(goal.left.expression), Not(goal.right.expression)))]
        if isinstance(goal, Or) and self._both_sides_are_negated(goal):
            return [Not(And(Not(goal.left.expression), Not(goal.right.expression)))]
        return []

    def _de_morgan_results(
        self, expression: LogicalExpression
    ) -> list[LogicalExpression]:
        if isinstance(expression, Not) and isinstance(expression.expression, And):
            return [Or(Not(expression.expression.left), Not(expression.expression.right))]
        if isinstance(expression, Not) and isinstance(expression.expression, Or):
            return [And(Not(expression.expression.left), Not(expression.expression.right))]
        if isinstance(expression, And) and self._both_sides_are_negated(expression):
            return [Not(Or(expression.left.expression, expression.right.expression))]
        if isinstance(expression, Or) and self._both_sides_are_negated(expression):
            return [Not(And(expression.left.expression, expression.right.expression))]
        return []

    @staticmethod
    def _both_sides_are_negated(expression: BinaryExpression) -> bool:
        return isinstance(expression.left, Not) and isinstance(expression.right, Not)


def prove(
    axioms: Iterable[LogicalExpression],
    goal: LogicalExpression,
    *,
    max_depth: int = 12,
) -> list[ProofStep]:
    """Convenience wrapper around ``TheoremProver``."""

    return TheoremProver(axioms, max_depth=max_depth).prove(goal)


def format_proof(steps: Sequence[ProofStep]) -> str:
    """Format proof steps as a numbered text block."""

    return "\n".join(f"{index}. {step!r}" for index, step in enumerate(steps, 1))


def _demo() -> None:
    p = Variable("P")
    q = Variable("Q")
    axioms = [p, p >> q]

    print("Goal:", q)
    print(format_proof(prove(axioms, q)))


if __name__ == "__main__":
    _demo()
