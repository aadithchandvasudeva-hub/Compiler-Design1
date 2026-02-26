temp_count = 1
intermediate_code = []

def new_temp():
    global temp_count
    temp = f"t{temp_count}"
    temp_count += 1
    return temp

def generate_icg(expression):
    tokens = expression.replace("=", " = ").replace("+", " + ").replace("*", " * ").split()

    while "*" in tokens:
        i = tokens.index("*")
        t = new_temp()
        intermediate_code.append(f"{t} = {tokens[i-1]} * {tokens[i+1]}")
        tokens[i-1:i+2] = [t]

    while "+" in tokens:
        i = tokens.index("+")
        t = new_temp()
        intermediate_code.append(f"{t} = {tokens[i-1]} + {tokens[i+1]}")
        tokens[i-1:i+2] = [t]

    intermediate_code.append(f"{tokens[0]} = {tokens[2]}")

# -------- MAIN --------
with open("icg_input.txt", "r") as f:
    expr = f.read().strip()

generate_icg(expr)

with open("icg_output.txt", "w") as f:
    for line in intermediate_code:
        f.write(line + "\n")

print("Intermediate Code Generated Successfully")