# GPS Theorem Prover

[![License: MIT](https://shields.io/badge/License-MIT-e0dd52?style=flat)](https://github.com/axlandrade/gps-theorem-prover/blob/main/LICENSE)
[![LinkedIn](https://img.shields.io/badge/-LinkedIn-blue?style=flat-square&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/axl-andrade-084a7820a/)

A Python theorem prover inspired by the classic General Problem Solver (GPS).

The project has two layers:

- `logic.py`: a GPS-style prover for propositional logic.
- `real_analysis.py`: an educational prover for real-analysis theorem schemas, including limits, continuity, and derivatives of symbolic real expressions.

The goal is to generate readable proof steps, not just a final boolean answer.

## Features

- Immutable symbolic expressions for propositional logic:
  `Variable`, `Not`, `And`, `Or`, and `Implies`.
- Recursive means-ends proof search for inference rules such as:
  Modus Ponens, conjunction introduction/elimination, disjunction introduction,
  double negation, and De Morgan laws.
- Symbolic real expressions:
  constants, identity variables, named functions, sums, differences, products,
  quotients, and integer powers.
- Real-analysis proof generation for:
  limits, continuity at a point, and symbolic derivatives.
- Exact rational arithmetic via Python's `fractions.Fraction`.
- Dependency-free test suite using `unittest`.
- Optional Docker execution for reproducible tests.

## Requirements

- Python 3.12 or newer
- Docker, optional

## Quick Start

Run the propositional logic demo:

```sh
python logic.py
```

Run the real-analysis demo:

```sh
python real_analysis.py
```

Run all tests:

```sh
python -m unittest discover -v
```

Or run the tests in Docker:

```sh
docker build -t gps-theorem-prover .
docker run --rm gps-theorem-prover
```

## Propositional Logic Example

```python
from logic import Variable, format_proof, prove

p = Variable("P")
q = Variable("Q")

proof = prove([p, p >> q], q)
print(format_proof(proof))
```

Output:

```text
1. P    [Axiom]
2. (P -> Q)    [Axiom]
3. Q    [Modus Ponens: P, (P -> Q)]
```

## Real Analysis Examples

### Limit of a Polynomial

```python
from real_analysis import Variable, format_analysis_proof, prove_limit

x = Variable("x")
expression = x**2 + 3 * x + 2

proof = prove_limit(expression, point=1, expected_value=6)
print(format_analysis_proof(proof))
```

This proves:

```text
lim_{x->1} (((x^2) + (3 * x)) + 2) = 6
```

### Continuity

```python
from real_analysis import Variable, format_analysis_proof, prove_continuity

x = Variable("x")
proof = prove_continuity(x**3 - 2 * x + 7, point=3)
print(format_analysis_proof(proof))
```

### Derivative

```python
from real_analysis import Variable, format_analysis_proof, prove_derivative

x = Variable("x")
proof = prove_derivative(x**2 + 3 * x + 2, expected_derivative=2 * x + 3)
print(format_analysis_proof(proof))
```

This proves:

```text
d/dx (((x^2) + (3 * x)) + 2) = ((2 * x) + 3)
```

### Assumptions for Named Functions

Named functions are intentionally uninterpreted. Provide assumptions when the
prover needs facts about them:

```python
from real_analysis import Limit, NamedFunction, prove_limit

f = NamedFunction("f")
assumption = Limit(f, "x", 2, 5)

proof = prove_limit(f + 1, point=2, expected_value=6, assumptions=[assumption])
```

## Project Structure

```text
.
├── logic.py
├── real_analysis.py
├── tests/
│   ├── test_logic.py
│   └── test_real_analysis.py
├── Dockerfile
├── pyproject.toml
└── README.md
```

## Scope

This is an educational symbolic prover. It proves a meaningful fragment of
propositional logic and real-analysis theorem schemas, while keeping the code
small enough to study and extend.

Natural next extensions include trigonometric/exponential functions, epsilon-
delta proof objects, theorem parsing, and a Lean export backend.
