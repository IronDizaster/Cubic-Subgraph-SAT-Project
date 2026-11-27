# Cubic Subgraph SAT Project
This is a solution to a homework project for Propositional and Predicate Logic (NAIL062) at Charles University. The provided Python code encodes, solves, and decodes the Cubic Subgraph problem via reduction to SAT (i.e. a propositional logic formula).

This repository does not include a precompiled Glucose binary. To run the script, you need **Python 3** and a compiled binary of **[Glucose 4.2.1](https://github.com/audemard/glucose/releases/tag/4.2.1)**

# Documentation
## Problem description
The Cubic Subgraph problem states:
Let us have an input of an $n$-node undirected graph $G(V,E)$. Is there a (non-empty) subset $F$ of the edges of $G$ such that every node in the graph $H(V,F)$ has either degree 3 or degree 0?

**Note:** The degree of a node, $v$, is the number of edges in the graph with $v$ as an end-point. We also assume that $G$ doesn't contains self-loops or multiplied edges.

An example of a valid input format is:

```
8
12
1 2
3 1
7 1
2 8
2 4
3 4
7 8
7 5
3 5
5 6
4 6
6 8
```
**Line 1:** A non-negative integer $n$ specifying the number of vertices $\vert{}V\vert{}$ in graph $G$. Vertices are 1-indexed ($V = \lbrace 1, 2, \dots, n \rbrace$).

**Line 2:** A non-negative integer $k$ specifying the number of edges $\vert{}E\vert{}$ in graph $G$.

**Next $k$ lines:** Each line contains two space-separated integers `u v` ($1 \le u, v \le n$, $u \neq v$) representing an undirected edge $\lbrace u, v \rbrace \in E$. Blank/whitespace-only lines are ignored, and the file must contain exactly $k$ edges.

For the provided example input, the output would be:
```
Found subgraph H(V,F) with 12 edges:
(1, 2)
(1, 3)
(1, 7)
(2, 4)
(2, 8)
(3, 4)
(3, 5)
(4, 6)
(5, 6)
(5, 7)
(6, 8)
(7, 8)
```
listing the edges of the found cubic subgraph.
If no cubic subgraph is found, only ```UNSATISFIABLE``` is outputted.

## Encoding
To represent the edge subset $F \subseteq E$, we introduce one propositional variable $f_{u,v}$ for each undirected edge $\lbrace u, v \rbrace \in E$ (indexed with $u < v$, where $f_{v,u}$ denotes the same variable as $f_{u,v}$):

$$f_{u,v} = 1 \iff \lbrace u, v \rbrace \in F$$

For each vertex $u \in V$, let $N(u) = \lbrace v \in V \mid \lbrace u, v \rbrace \in E \rbrace$ denote the set of its neighbour vertices in $G$.

To express the Cubic Subgraph conditions in Conjunctive Normal Form (CNF), we combine the following constraints:

1. The edge subset $F$ is non-empty ($F \neq \emptyset$):

$$\bigvee_{\substack{\lbrace u, v \rbrace \in E \\\\ u < v}} f_{u,v}$$

2. Vertices with fewer than $3$ neighbours in $G$ must have degree $0$ in $H$:

$$\bigwedge_{\substack{u \in V \\\\ |N(u)| < 3}} \bigwedge_{v \in N(u)} \neg f_{u,v}$$

3. Vertices with $|N(u)| \ge 3$ cannot have degree $1$ in $H$:

$$\bigwedge_{\substack{u \in V \\\\ |N(u)| \ge 3}} \bigwedge_{v \in N(u)} \left( \neg f_{u,v} \lor \bigvee_{w \in N(u) \setminus \lbrace v \rbrace} f_{u,w} \right)$$

4. Vertices with $|N(u)| \ge 3$ cannot have degree $2$ in $H$:

$$\bigwedge_{\substack{u \in V \\\\ |N(u)| \ge 3}} \bigwedge_{\substack{\lbrace v_1, v_2 \rbrace \subseteq N(u) \\\\ v_1 \neq v_2}} \left( \neg f_{u,v_1} \lor \neg f_{u,v_2} \lor \bigvee_{w \in N(u) \setminus \lbrace v_1, v_2 \rbrace} f_{u,w} \right)$$

5. Vertices with $|N(u)| \geq 4$ cannot have degree greater than or equal to 4 in $H$:

$$\bigwedge_{\substack{u \in V \\\\ |N(u)| \ge 4}} \bigwedge_{\substack{S \subseteq N(u) \\\\ |S| = 4}} \left( \bigvee_{v \in S} \neg f_{u,v} \right)$$

**Note:**

We could encode constraints 2–5 directly, but this would yield a formula that is not in CNF:

**2–5. All vertices $u \in V$ have degree $3$ or $0$ in $H(V, F)$:**

$$\bigwedge_{u \in V} \left( \bigwedge_{v \in N(u)} \neg f_{u,v} \lor \bigvee_{\substack{S \subseteq N(u) \\\\ |S| = 3}} \left( \bigwedge_{v \in S} f_{u,v} \land \bigwedge_{w \in N(u) \setminus S} \neg f_{u,w} \right) \right)$$

which is why we opted for the indirect encoding approach of forbidding degrees of 1, 2, and greater than or equal to 4.

## User documentation

### Prerequisites & Solver Setup

1. Ensure **Python 3** is installed.
2. Download and build **[Glucose 4.2.1](https://github.com/audemard/glucose/releases/tag/4.2.1)** on a UNIX-based environment (Linux, macOS, or WSL on Windows):

```bash
cmake .
make
```

4. Either copy the compiled `glucose-syrup` binary into the root directory of this repository, or pass its path explicitly via the `-s` flag.

### Running the Script

Basic usage:
```bash
python3 cubic_subgraph.py [-h] [-i INPUT] [-o OUTPUT] [-s SOLVER] [-v {0,1}]
```

Command-line options:

- `-h`, `--help` : Show the help message and exit.
- `-i INPUT`, `--input INPUT` : Path to the input graph instance file. Default: `"instances/input-cubic_graph_exact.in"`.
- `-o OUTPUT`, `--output OUTPUT` : Path where the generated DIMACS CNF formula will be written. Default: `"formula.cnf"`.
- `-s SOLVER`, `--solver SOLVER` : Path to the SAT solver to be used. Default: `"./glucose-syrup"`. If the binary is located outside the project root, provide its relative or absolute path (e.g., `-s ~/glucose-4.2.1/glucose-syrup`).
- `-v {0,1}`, `--verb {0,1}` : Verbosity level passed to Glucose (`0` = minimal output, `1` = full solver statistics). Default: `1`.

### Example Execution & Output

```bash
python3 cubic_subgraph.py -i instances/input-cubic_graph_subset.in -s ./glucose-syrup -v 0
```
### Example Instances

- `instances/input-cubic_graph_exact_sat.in`: A cube graph ($n = 8, k = 12$), which is itself a cubic graph.
- `instances/input-cubic_graph_subset_sat.in`: The same cube graph but with two extra vertices attached ($n = 10, k = 14$).
- `instances/input-K_22_sat.in`: The complete graph $K_{22}$ ($n = 22, k = 231$), a dense satisfiable instance containing multiple cubic subgraphs. Takes ~9.8 seconds to execute. Generates a ~3MB file containing 136753 clauses.
- `instances/input-c4_unsat.in`: Graph $C_4$ ($n = 4, k = 4) containing no $3$-regular subgraph (`UNSAT`).
---

## Experiments
Tests were ran on AMD Ryzen 7 8845HS w/ Radeon 780M Graphics (3.8 GHz) with 14 GB RAM on Fedora inside WSL (Windows 11)

