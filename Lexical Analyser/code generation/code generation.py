target_code = []
register_count = 1

with open("codegen_input.txt", "r") as f:
    lines = f.readlines()

for line in lines:
    left, right = line.strip().split(" = ")

    if "*" in right:
        op1, op2 = right.split(" * ")
        target_code.append(f"MOV R{register_count}, {op1}")
        target_code.append(f"MUL R{register_count}, {op2}")
        target_code.append(f"MOV {left}, R{register_count}")
        register_count += 1

    elif "+" in right:
        op1, op2 = right.split(" + ")
        target_code.append(f"MOV R{register_count}, {op1}")
        target_code.append(f"ADD R{register_count}, {op2}")
        target_code.append(f"MOV {left}, R{register_count}")
        register_count += 1

with open("codegen_output.txt", "w") as f:
    for line in target_code:
        f.write(line + "\n")