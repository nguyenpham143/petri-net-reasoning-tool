# Symbolic and Algebraic Reasoning in Petri Nets (CO2011)

A Python tool for modeling and analyzing **1-safe Petri Nets** using both explicit state space exploration and symbolic/algebraic techniques (Binary Decision Diagrams & Integer Linear Programming). Developed as the Major Assignment for the **Mathematical Modeling (CO2011)** course at Ho Chi Minh City University of Technology (HCMUT - VNU-HCM), Semester 251.

## Overview

This project implements formal verification and optimization techniques for concurrent systems modeled as 1-safe Petri Nets:

- **Task 1 — PNML Parsing & Model Representation (`src/pnml_parser.py`, `src/petri_model.py`):** Parses standard XML-based PNML (Petri Net Markup Language) files and builds graph representations of places, transitions, and flow arcs.
- **Task 2 — Explicit Reachability Analysis (`src/bfs_explicit.py`):** Enumerates all reachable markings from the initial state using Breadth-First Search (BFS).
- **Task 3 — Symbolic Reachability Analysis (`src/bdd_reachability.py`):** Encodes states symbolically using Binary Decision Diagrams (BDD) via `pyeda` and computes the reachable state space through iterative fixed-point image computation.
- **Task 4 — Deadlock Detection (`src/deadlock.py`):** Combines Integer Linear Programming (ILP) formulations via `pulp` with BDD verification to efficiently detect deadlocks (dead markings reachable from initial state).
- **Task 5 — Reachable State Optimization (`src/optimization.py`):** Finds the optimal reachable marking that maximizes a linear objective function $c^T M$.

## Project Structure

```text
.
├── src/
│   ├── pnml_parser.py                  # PNML file reader and XML parser
│   ├── petri_model.py                  # Petri Net data structures & operations
│   ├── common_utils.py                 # Utility helper functions
│   ├── bfs_explicit.py                 # Task 2: Explicit BFS reachability
│   ├── bdd_reachability.py             # Task 3: Symbolic BDD reachability
│   ├── deadlock.py                     # Task 4: ILP + BDD deadlock detection
│   └── optimization.py                 # Task 5: Linear objective optimization
├── tests/
│   ├── test_small.pnml                 # Resource allocation model (contains deadlock)
│   └── test_medium.pnml                # Fork-join workflow model (deadlock-free)
├── specs/
│   └── MM-251-Assignment (v0.0.3).pdf  # Assignment specification document
├── report/
│   └── MM-251-Assignment-Report.pdf    # Technical report & benchmark results
├── .gitignore                          # Git ignore rules (including venv/ and caches)
├── LICENSE                             # MIT License
├── README.md                           # Documentation
├── requirements.txt                    # Python dependencies
└── main.py                             # Main CLI runner
```

## Getting Started

### Prerequisites

- Python 3.10+ (Recommended to run on Linux, macOS, or Windows via WSL for optimal C-extension BDD performance).

### Installation

1. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate    # On Windows: .\venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Usage

Run with default sample model (`tests/test_small.pnml`):
```bash
python3 main.py
```

Run with medium sample model (`tests/test_medium.pnml`):
```bash
python3 main.py --input tests/test_medium.pnml
```

## License

This project is licensed under the [MIT License](LICENSE).
