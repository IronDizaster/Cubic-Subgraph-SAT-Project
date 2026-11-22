import subprocess
from argparse import ArgumentParser
from itertools import combinations
# ... we could make a helper combinations function ourselves using recursion,
#     but this is probably more effective

def initialize_neighbours(n: int) -> dict:
  # Each vertex has no neighbours at initialization
  neighbours = {}
  for i in range(1, n + 1):
    neighbours[i] = set()
  return neighbours

def load_instance(input_file_name) -> dict:
  # returns neighbours dictionary, where key is vertex u, value is set N(u)
  with open(input_file_name, "r") as file:
    N = int(next(file))
    K = int(next(file))
    neighbours = initialize_neighbours(N);
    edge_cnt = 0
    edges = []
    for line in file:
      if not line.strip(): continue # skip empty lines
      edge_cnt += 1
      edge = list(map(int, line.split()))
      if len(edge) != 2:
        raise Exception("ERROR: Invalid input format (some edge in input is not formatted as (x,y))")
      u = edge[0]
      v = edge[1]
      if u == v:
        raise Exception("ERROR: Self - loop provided in input.")
      edges.append((u, v))
      neighbours[u].add(v)
      neighbours[v].add(u)
    if edge_cnt != K:
      raise Exception("ERROR: Input provided more than K edges.")
    return neighbours

def encode(instance):
  edge_to_var = {}
  var_to_edge = {}
  next_f_var = 1
  edges = [(-1, -1)] # first edge is -1,-1 so edges are 1-indexed for clean conversion
  # Initialize look-up dictionaries for conversion between edges and DIMACS CNF vars
  # also initialize Edges
  for u in sorted(instance):
    for v in sorted(instance[u]):
      if u < v:
        edge_to_var[(u,v)] = next_f_var
        var_to_edge[next_f_var] = (u,v)
        next_f_var += 1
        edges.append((u, v))
  cnf = []
  def get_var(u, v) -> int:
    # helper function so that f_u,v = f_v,u
    return edge_to_var[(min(u,v), max(u,v))]
  
  # 1. F must be non-empty
  clause = []
  for i in range(1, len(edges)):
    clause.append(edge_to_var[edges[i]])
  clause.append(0)
  cnf.append(clause)

  # 2. Vertices with fewer than 3 neighbours must have degree 0 in H:
  for u in instance: # for each vertex u...
    if len(instance[u]) >= 3: continue
    for v in instance[u]: # for each neighbour v of vertex u...
      cnf.append([-get_var(u, v), 0])
      # ...ensure u has no incident edges in H

  # 3. Vertices with >= 3 neighbours cannot have degree 1 in H
  for u in instance:
    if len(instance[u]) < 3: continue
    for v in instance[u]:
      clause = [-get_var(u,v)]
      for w in instance[u] - {v}:
        clause.append(get_var(u, w))
      clause.append(0)
      cnf.append(clause)

  # 4. Vertices with >= 3 neighbours cannot have degree 2 in H
  for u in instance:
    if len(instance[u]) < 3: continue
    for v1, v2 in combinations(instance[u], 2):
      if v1 == v2: continue
      clause = [-get_var(u,v1), -get_var(u, v2)]
      for w in instance[u] - {v1, v2}:
        clause.append(get_var(u, w))
      clause.append(0)
      cnf.append(clause)

  # 5. Vertices with >= 4 neighbours cannot have degree >= 4 in H
  for u in instance:
    if len(instance[u]) < 4: continue
    for v1, v2, v3, v4 in combinations(instance[u], 4):
      clause = [-get_var(u, v1), -get_var(u, v2), -get_var(u, v3), -get_var(u, v4), 0]
      cnf.append(clause)

  return cnf, len(edges) - 1, var_to_edge

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        default="instances/input-cubic_graph_exact.in",
        type=str,
        help=(
            "The instance file."
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        default="formula.cnf",
        type=str,
        help=(
            "Output file for the DIMACS format (i.e. the CNF formula)."
        ),
    )
    parser.add_argument(
        "-s",
        "--solver",
        default="glucose-syrup",
        type=str,
        help=(
            "The SAT solver to be used."
        ),
    )
    parser.add_argument(
        "-v",
        "--verb",
        default=1,
        type=int,
        choices=range(0,2),
        help=(
            "Verbosity of the SAT solver used."
        ),
    )
    args = parser.parse_args()

    # get the input instance
    instance = load_instance(args.input)
    encode(instance)
    # interpret the result and print it in a human-readable format

