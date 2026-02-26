# Phase 5: Code Optimization
# Removes redundant temporary variables

with open("optimizer_input.txt", "r") as f:
    lines = [line.strip() for line in f if line.strip()]

# Store assignments
assignments = {}
for line in lines:
    left, right = line.split(" = ")
    assignments[left] = right

optimized = []

# Find final assignment (usually variable like 'a')
final_var = list(assignments.keys())[-1]
final_expr = assignments[final_var]

# Replace temporary variables in final expression
while final_expr in assignments:
    final_expr = assignments[final_expr]

# Keep only necessary computations
for left, right in assignments.items():
    if left.startswith("t") and left in final_expr:
        optimized.append(f"{left} = {right}")

optimized.append(f"{final_var} = {final_expr}")

# Write optimized code
with open("optimizer_output.txt", "w") as f:
    for line in optimized:
        f.write(line + "\n")