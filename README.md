# GPS Theorem Prover

[![License: MIT](https://shields.io/badge/License-MIT-e0dd52?style=flat)](https://github.com/axlandrade/gps-theorem-prover/blob/main/LICENSE)
[![LinkedIn](https://img.shields.io/badge/-LinkedIn-blue?style=flat-square&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/axl-andrade-084a7820a/)

A Python implementation of the classic General Problem Solver (GPS) algorithm, tailored to prove theorems in propositional logic. This is an educational project inspired by Newell & Simon's original work and the book "Artificial Intelligence: A Modern Approach".

## About The Project

The General Problem Solver (GPS) is one of the most iconic programs in the history of Artificial Intelligence. Developed in 1959 by Herbert A. Simon, J. C. Shaw, and Allen Newell, it was the first program to separate its problem-solving strategy from its knowledge of specific problems.

This project aims to replicate the core logic of GPS, **Means-Ends Analysis**, to solve problems in a symbolic domain: proving formal logic theorems. Instead of navigating a physical world, our GPS will navigate a world of logical expressions, using rules of inference as its operators to reach a goal theorem from a set of given axioms.

This is a hands-on exercise to explore the foundations of symbolic AI and automated reasoning.

## Features

-   **Object-Oriented Logic:** Clean and extensible representation of logical expressions (`Variables`, `Not`, `And`, `Or`, `Implies`).
-   **GPS Engine:** A core solver that implements the recursive Means-Ends Analysis algorithm.
-   **Symbolic Operators:** Logical rules of inference (e.g., Modus Ponens, De Morgan's Laws) are treated as operators to reduce differences between states.
-   **Proof Generation:** The final output is a step-by-step plan that constitutes a formal proof of the target theorem.

## Getting Started

This project is configured to run inside a fully containerized development environment using VS Code and Docker.

### Prerequisites

-   [Docker](https://www.docker.com/get-started)
-   [Visual Studio Code](https://code.visualstudio.com/)
-   [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) for VS Code.

### Installation

1.  Clone the repository:
    ```sh
     git clone [https://github.com/axlandrade/gps-theorem-prover](https://github.com/axlandrade/gps-theorem-prover)
    ```
2.  Change into the project directory:
    ```sh
    cd gps-theorem-prover
    ```
3.  Open the folder in VS Code.
4.  VS Code will automatically detect the `.devcontainer` configuration and prompt you to **"Reopen in Container"**. Click it.

That's it! The dev container will build, and all dependencies and VS Code extensions specified in `devcontainer.json` will be automatically installed and configured for you.

## Usage

The core of the project is the ability to represent complex logical expressions in an intuitive way.

For example, to create the expression `(¬P ∧ Q)`:

```python
from logic import Variable, Not, And

# 1. Define the propositional variables
p = Variable('P')
q = Variable('Q')

# 2. Build the complex expression
not_p = Not(p)
expression = And(not_p, q)

# 3. The object representation is easy to print and debug
print(expression)
# Expected output: (¬(P) ∧ Q)