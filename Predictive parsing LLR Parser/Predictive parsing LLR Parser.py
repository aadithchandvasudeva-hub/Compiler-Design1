import collections
from tabulate import tabulate

# Global Constants
EPSILON = 'ε'
DOLLAR = '$'

class PredictiveParser:
    def __init__(self, grammar_str):
        self.productions = []
        self.non_terminals = []
        self.terminals = set()
        self.start_symbol = None
        self._parse_grammar(grammar_str)
        
        self.first = {}
        self.follow = {}
        self.table = {}

    def _parse_grammar(self, text):
        """Extracts NTs, Terminals, and Productions from raw string."""
        lines = [l.strip() for l in text.split('\n') if l.strip() and not l.startswith('//')]
        for line in lines:
            # Handle different arrow types
            for arrow in ['->', '::=', '→']:
                if arrow in line:
                    lhs, rhs_part = line.split(arrow)
                    break
            
            lhs = lhs.strip()
            if not self.start_symbol: self.start_symbol = lhs
            if lhs not in self.non_terminals: self.non_terminals.append(lhs)
            
            alternatives = rhs_part.split('|')
            for alt in alternatives:
                rhs = alt.strip().split()
                # Handle epsilon keywords
                if not rhs or rhs[0].lower() in ['epsilon', 'eps', 'ε']:
                    rhs = [EPSILON]
                
                self.productions.append({'lhs': lhs, 'rhs': rhs, 'str': f"{lhs} → {' '.join(rhs)}"})
                
                for symbol in rhs:
                    # If it's not a known NT and not epsilon, it's a terminal
                    if not symbol[0].isupper() and symbol != EPSILON:
                        self.terminals.add(symbol)
        self.terminals.add(DOLLAR)

    def _get_first_of_seq(self, seq):
        """Helper to find FIRST of a sequence of symbols (α)."""
        res = set()
        for symbol in seq:
            if symbol == EPSILON:
                res.add(EPSILON)
                return res
            if symbol not in self.non_terminals: # It's a terminal
                res.add(symbol)
                return res
            
            symbol_first = self.first[symbol]
            res.update(symbol_first - {EPSILON})
            if EPSILON not in symbol_first:
                return res
        res.add(EPSILON)
        return res

    def compute_first(self):
        first = {nt: set() for nt in self.non_terminals}
        changed = True
        while changed:
            changed = False
            for prod in self.productions:
                lhs, rhs = prod['lhs'], prod['rhs']
                before = len(first[lhs])
                
                if rhs == [EPSILON]:
                    first[lhs].add(EPSILON)
                else:
                    for symbol in rhs:
                        if symbol not in self.non_terminals: # Terminal
                            first[lhs].add(symbol)
                            break
                        else: # Non-terminal
                            first[lhs].update(first[symbol] - {EPSILON})
                            if EPSILON not in first[symbol]:
                                break
                    else: # All symbols were nullable
                        first[lhs].add(EPSILON)
                
                if len(first[lhs]) > before: changed = True
        self.first = first
        return first

    def compute_follow(self):
        follow = {nt: set() for nt in self.non_terminals}
        follow[self.start_symbol].add(DOLLAR)
        
        changed = True
        while changed:
            changed = False
            for prod in self.productions:
                lhs, rhs = prod['lhs'], prod['rhs']
                for i, B in enumerate(rhs):
                    if B in self.non_terminals:
                        before = len(follow[B])
                        beta = rhs[i+1:]
                        
                        if beta:
                            first_of_beta = self._get_first_of_seq(beta)
                            follow[B].update(first_of_beta - {EPSILON})
                            if EPSILON in first_of_beta:
                                follow[B].update(follow[lhs])
                        else:
                            follow[B].update(follow[lhs])
                            
                        if len(follow[B]) > before: changed = True
        self.follow = follow
        return follow

    def build_table(self):
        table = collections.defaultdict(dict)
        for prod in self.productions:
            lhs, rhs = prod['lhs'], prod['rhs']
            first_of_rhs = self._get_first_of_seq(rhs)
            
            for a in first_of_rhs:
                if a != EPSILON:
                    if a in table[lhs]:
                        print(f"CONFLICT! Multiple entries at M[{lhs}, {a}]")
                    table[lhs][a] = prod['str']
            
            if EPSILON in first_of_rhs:
                for b in self.follow[lhs]:
                    table[lhs][b] = prod['str']
        self.table = table
        return table

    def parse_string(self, input_str):
        tokens = input_str.split() + [DOLLAR]
        stack = [DOLLAR, self.start_symbol]
        idx = 0
        trace = []
        
        while len(stack) > 0:
            top = stack[-1]
            current_token = tokens[idx]
            stack_view = " ".join(stack[::-1])
            input_view = " ".join(tokens[idx:])
            
            if top == current_token:
                if top == DOLLAR:
                    trace.append([stack_view, input_view, "Accepted"])
                    stack.pop()
                else:
                    trace.append([stack_view, input_view, f"Match {top}"])
                    stack.pop()
                    idx += 1
            elif top in self.non_terminals:
                if current_token in self.table[top]:
                    prod_str = self.table[top][current_token]
                    trace.append([stack_view, input_view, f"Apply {prod_str}"])
                    
                    # Extract RHS from string "A → X Y Z"
                    rhs_part = prod_str.split('→')[1].strip().split()
                    stack.pop()
                    if rhs_part != [EPSILON]:
                        for sym in reversed(rhs_part):
                            stack.append(sym)
                else:
                    trace.append([stack_view, input_view, f"Error: No entry for {top}"])
                    break
            else:
                trace.append([stack_view, input_view, f"Error: Unexpected {current_token}"])
                break
                
        print("\n--- Parsing Trace ---")
        print(tabulate(trace, headers=["Stack", "Input", "Action"], tablefmt="fancy_grid"))

# --- Running the Simulation ---
grammar_text = """
E  -> T E'
E' -> + T E' | ε
T  -> F T'
T' -> * F T' | ε
F  -> ( E ) | id
"""

parser = PredictiveParser(grammar_text)
parser.compute_first()
parser.compute_follow()
parser.build_table()

# Display sets
print("--- FIRST Sets ---")
for nt, s in parser.first.items(): print(f"{nt}: {s}")
print("\n--- FOLLOW Sets ---")
for nt, s in parser.follow.items(): print(f"{nt}: {s}")

# Parse a test string
parser.parse_string("id + id * id")