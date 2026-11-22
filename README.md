# Cubic Subgraph SAT Project
This is a solution to a homework project for Propositional and Predicate Logic (NAIL062) at Charles University. The provided Python code encodes, solves, and decodes the Cubic Subgraph problem via reduction to SAT (i.e. a propositional logic formula).

This repository does not include a precompiled Glucose binary. To run the script, you need **Python 3** and a compiled binary of **[Glucose 4.2.1](https://github.com/audemard/glucose/releases/tag/4.2.1)**

# Documentation
## Problem description
The Cubic Subgraph problem states:
Let us have an input of an $n$-node undirected graph $G(V,E)$. Is there a (non-empty) subset $F$ of the edges of $G$ such that every node in the graph $H(V,F)$ has either degree 3 or degree 0?

**Note:** The degree of a node, $v$, is the number of edges in the graph with $v$ as an end-point.

An example of a valid input format is:

```
...to be decided...
...but most likely something along the lines of...:
4 # n = |V|
6 # k = |E|
1 2
1 3
1 4
2 3
2 4
3 4
```
