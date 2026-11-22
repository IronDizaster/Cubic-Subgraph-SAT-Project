def generate_k_n(n: int):
  # generates an instance of a K_n graph to test
  with open(f"instances/input-K_{n}.in", "w") as file:
    K = ((n*(n-1)) // 2) # formula for the amount of edges in a complete graph
    file.write(f"{n}\n")
    file.write(f"{K}\n")
    for i in range(1, n+1):
      for j in range(i+1, n+1):
        file.write(f"{i} {j}\n")

generate_k_n(22)