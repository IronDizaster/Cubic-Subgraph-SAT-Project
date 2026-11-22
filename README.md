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

## Encoding
To represent the edge subset $F \subseteq E$, we introduce one propositional variable $f_{u,v}$ for each undirected edge $\lbrace u, v \rbrace \in E$ (indexed with $u < v$, where $f_{v,u}$ denotes the same variable as $f_{u,v}$):

$$f_{u,v} = 1 \iff \lbrace u, v \rbrace \in F$$

For each vertex $u \in V$, let $N(u) = \lbrace v \in V \mid \lbrace u, v \rbrace \in E \rbrace$ denote the set of its neighbour vertices in $G$.

To express the Cubic Subgraph conditions directly in Conjunctive Normal Form (CNF), we combine the following constraints:

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

