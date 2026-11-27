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
        raise Exception("ERROR: Invalid input format)")
      u = edge[0]
      v = edge[1]
      if u == v:
        raise Exception("ERROR: Self - loop provided in input.")
      edges.append((u, v))
      neighbours[u].add(v)
      neighbours[v].add(u)
    if edge_cnt != K:
      raise Exception("ERROR: Input didn't provide K edges.")
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

# ----borrowed from example solution----
def call_solver(cnf, nr_vars, output_name, solver_name, verbosity):
    # print CNF into formula.cnf in DIMACS format
    with open(output_name, "w") as file:
        file.write("p cnf " + str(nr_vars) + " " + str(len(cnf)) + '\n')
        for clause in cnf:
            file.write(' '.join(str(lit) for lit in clause) + '\n')

    # call the solver and return the output
    return subprocess.run([solver_name, '-model', '-verb=' + str(verbosity) , output_name], stdout=subprocess.PIPE)

def print_result(result, var_to_edge):
    for line in result.stdout.decode('utf-8').split('\n'):
        print(line)  # print the whole output of the SAT solver to stdout, so you can see the raw output for yourself

    # check the returned result
    if (result.returncode == 20): # returncode for SAT is 10, for UNSAT is 20
        return

    # parse the model from the output of the solver
    # the model starts with 'v'
    model = []
    for line in result.stdout.decode('utf-8').split('\n'):
        if line.startswith("v"):    # there might be more lines of the model, each starting with 'v'
            variables = line.split(" ")
            variables.remove("v")
            model.extend(int(v) for v in variables)      
    model.remove(0) # 0 is the end of the model, just ignore it

    # print human readable format
    print()
    print("##################################################################")
    print("#########[ Human readable result of the cubic subgraph ]##########")
    print("##################################################################")
    print()
    edges = []
    for var in model:
      if var < 0: continue # skip negative vars
      edges.append(var_to_edge[var])
    print(f"Found subgraph H(V,F) with {len(edges)} edges:")
    for edge in edges:
       print(edge)

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
        default="./glucose-syrup",
        type=str,
        help=(
            "The SAT solver to be used. If the solver is located in a different directory than this project, provide the absolute path."
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
    cnf, nr_vars, var_to_edge = encode(instance)
    # var_to_edge is needed for printing out human readable format
    result = call_solver(cnf, nr_vars, args.output, args.solver, args.verb)
    # interpret the result and print it in a human-readable format
    print_result(result, var_to_edge)

