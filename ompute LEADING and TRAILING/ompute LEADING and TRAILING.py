import collections
from tabulate import tabulate

# Constants for relations
LT = '⋖'  # Yields precedence
GT = '⋗'  # Takes precedence
EQ = '≐'  # Same precedence
DOLLAR = '$'

class OperatorPrecedence:
    def __init__(self, grammar_str):
        self.productions = []
        self.non_terminals = []
        self.terminals = set()
        self.start_symbol = None
        self._parse_grammar(grammar_str)
        
        self.leading = {}
        self.trailing = {}
        self.table = {}

    def _parse_grammar(self, text):
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        for line in lines:
            lhs, rhs_part = line.split('->')
            lhs = lhs.strip()
            if not self.start_symbol: self.start_symbol = lhs
            if lhs not in self.non_terminals: self.non_terminals.append(lhs)
            
            alternatives = rhs_part.split('|')
            for alt in alternatives:
                rhs = alt.strip().split()
                self.productions.append((lhs, rhs))
                for symbol in rhs:
                    if not symbol.isupper():
                        self.terminals.add(symbol)
        self.terminals.add(DOLLAR)

    def validate_operator_grammar(self):
        """Checks for epsilon or adjacent non-terminals."""
        for lhs, rhs in self.productions:
            if not rhs or rhs == ['ε']:
                return False, f"Constraint Error: Epsilon production in {lhs}."
            for i in range(len(rhs) - 1):
                if rhs[i].isupper() and rhs[i+1].isupper():
                    return False, f"Constraint Error: Adjacent non-terminals in {lhs}."
        return True, "Valid Operator Grammar."

    def compute_leading(self):
        leading = {nt: set() for nt in self.non_terminals}
        
        # Base cases
        for lhs, rhs in self.productions:
            # Case 1: A -> a...
            if not rhs[0].isupper():
                leading[lhs].add(rhs[0])
            # Case 2: A -> Ba...
            elif len(rhs) > 1 and not rhs[1].isupper():
                leading[lhs].add(rhs[1])

        # Iterative step
        changed = True
        while changed:
            changed = False
            for lhs, rhs in self.productions:
                if rhs[0].isupper():
                    B = rhs[0]
                    before = len(leading[lhs])
                    leading[lhs].update(leading[B])
                    if len(leading[lhs]) > before: changed = True
        self.leading = leading
        return leading

    def compute_trailing(self):
        trailing = {nt: set() for nt in self.non_terminals}
        
        # Base cases
        for lhs, rhs in self.productions:
            last = rhs[-1]
            # Case 1: A -> ...a
            if not last.isupper():
                trailing[lhs].add(last)
            # Case 2: A -> ...aB
            elif len(rhs) > 1 and not rhs[-2].isupper():
                trailing[lhs].add(rhs[-2])

        # Iterative step
        changed = True
        while changed:
            changed = False
            for lhs, rhs in self.productions:
                last = rhs[-1]
                if last.isupper():
                    B = last
                    before = len(trailing[lhs])
                    trailing[lhs].update(trailing[B])
                    if len(trailing[lhs]) > before: changed = True
        self.trailing = trailing
        return trailing

    def build_table(self):
        terms = sorted(list(self.terminals))
        table = {t1: {t2: "" for t2 in terms} for t1 in terms}

        for lhs, rhs in self.productions:
            for i in range(len(rhs) - 1):
                X, Y = rhs[i], rhs[i+1]
                
                # Rule: a = b
                if not X.isupper() and not Y.isupper():
                    table[X][Y] = EQ
                
                # Rule: a <. LEADING(B)
                if not X.isupper() and Y.isupper():
                    for b in self.leading[Y]:
                        table[X][b] = LT
                
                # Rule: TRAILING(B) .> a
                if X.isupper() and not Y.isupper():
                    for a in self.trailing[X]:
                        table[a][Y] = GT
                
                # Rule: a = b (for X Y Z where Y is NT)
                if i < len(rhs) - 2:
                    Z = rhs[i+2]
                    if not X.isupper() and Y.isupper() and not Z.isupper():
                        table[X][Z] = EQ

        # Handle boundary $
        for b in self.leading[self.start_symbol]:
            table[DOLLAR][b] = LT
        for a in self.trailing[self.start_symbol]:
            table[a][DOLLAR] = GT

        self.table = table
        return table

    def display_results(self):
        print("\n--- LEADING SETS ---")
        for nt, s in self.leading.items(): print(f"{nt}: {s}")
        
        print("\n--- TRAILING SETS ---")
        for nt, s in self.trailing.items(): print(f"{nt}: {s}")
        
        print("\n--- PRECEDENCE TABLE ---")
        headers = sorted(list(self.terminals))
        rows = []
        for t1 in headers:
            row = [t1]
            for t2 in headers:
                row.append(self.table[t1][t2])
            rows.append(row)
        print(tabulate(rows, headers=["T / T"] + headers, tablefmt="fancy_grid"))

# Execution
grammar = """
E -> E + T | T
T -> T * F | F
F -> ( E ) | id
"""

op = OperatorPrecedence(grammar)
is_valid, msg = op.validate_operator_grammar()
print(msg)

if is_valid:
    op.compute_leading()
    op.compute_trailing()
    op.build_table()
    op.display_results()