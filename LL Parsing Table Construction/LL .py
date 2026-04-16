import collections

# Constants
EPSILON = 'ε'
DOLLAR = '$'

class LL1Parser:
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
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        for line in lines:
            lhs, rhs_part = line.split('->')
            lhs = lhs.strip()
            if not self.start_symbol: self.start_symbol = lhs
            if lhs not in self.non_terminals: self.non_terminals.append(lhs)
            
            alternatives = rhs_part.split('|')
            for alt in alternatives:
                rhs = alt.strip().split()
                if not rhs or rhs == ['eps'] or rhs == [EPSILON]:
                    rhs = [EPSILON]
                self.productions.append((lhs, rhs))
                for symbol in rhs:
                    if not symbol.isupper() and symbol != EPSILON:
                        self.terminals.add(symbol)
        self.terminals.add(DOLLAR)

    def compute_first(self):
        first = {nt: set() for nt in self.non_terminals}
        
        changed = True
        while changed:
            changed = False
            for lhs, rhs in self.productions:
                before = len(first[lhs])
                
                # Rule: if X -> epsilon, add epsilon to FIRST(X)
                if rhs == [EPSILON]:
                    first[lhs].add(EPSILON)
                else:
                    for symbol in rhs:
                        if symbol not in self.non_terminals: # Terminal
                            first[lhs].add(symbol)
                            break
                        else: # Non-terminal
                            first_of_symbol = first[symbol]
                            first[lhs].update(first_of_symbol - {EPSILON})
                            if EPSILON not in first_of_symbol:
                                break
                    else: # If all symbols in RHS are nullable
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
            for lhs, rhs in self.productions:
                for i, symbol in enumerate(rhs):
                    if symbol in self.non_terminals:
                        before = len(follow[symbol])
                        
                        # Look at what follows this non-terminal (beta)
                        beta = rhs[i+1:]
                        if beta:
                            first_of_beta = self._get_first_of_sequence(beta)
                            follow[symbol].update(first_of_beta - {EPSILON})
                            if EPSILON in first_of_beta:
                                follow[symbol].update(follow[lhs])
                        else:
                            follow[symbol].update(follow[lhs])
                            
                        if len(follow[symbol]) > before: changed = True
        self.follow = follow
        return follow

    def _get_first_of_sequence(self, symbols):
        res = set()
        for s in symbols:
            if s not in self.non_terminals:
                res.add(s)
                return res
            res.update(self.first[s] - {EPSILON})
            if EPSILON not in self.first[s]:
                return res
        res.add(EPSILON)
        return res

    def build_table(self):
        table = collections.defaultdict(dict)
        for lhs, rhs in self.productions:
            first_of_rhs = self._get_first_of_sequence(rhs)
            
            for terminal in first_of_rhs:
                if terminal != EPSILON:
                    if terminal in table[lhs]:
                        print(f"CONFLICT at M[{lhs}, {terminal}]!")
                    table[lhs][terminal] = rhs
            
            if EPSILON in first_of_rhs:
                for terminal in self.follow[lhs]:
                    table[lhs][terminal] = rhs
        self.table = table
        return table

    def parse(self, input_str):
        tokens = input_str.split() + [DOLLAR]
        stack = [DOLLAR, self.start_symbol]
        curr_idx = 0
        
        print(f"\n{'Stack':<25} {'Input':<25} {'Action'}")
        print("-" * 70)
        
        while stack:
            top = stack.pop()
            curr_token = tokens[curr_idx]
            
            stack_str = " ".join(stack + [top])
            input_left = " ".join(tokens[curr_idx:])
            
            if top == curr_token:
                if top == DOLLAR:
                    print(f"{stack_str:<25} {input_left:<25} Accepted")
                    return True
                print(f"{stack_str:<25} {input_left:<25} Match {top}")
                curr_idx += 1
            elif top in self.non_terminals:
                if curr_token in self.table[top]:
                    rhs = self.table[top][curr_token]
                    action = f"{top} -> {' '.join(rhs)}"
                    print(f"{stack_str:<25} {input_left:<25} Output {action}")
                    if rhs != [EPSILON]:
                        for symbol in reversed(rhs):
                            stack.append(symbol)
                else:
                    print(f"{stack_str:<25} {input_left:<25} Error")
                    return False
            else:
                print(f"{stack_str:<25} {input_left:<25} Error")
                return False

# --- Demo Execution ---
grammar_text = """
E  -> T E'
E' -> + T E' | ε
T  -> F T'
T' -> * F T' | ε
F  -> ( E ) | id
"""

parser = LL1Parser(grammar_text)
parser.compute_first()
parser.compute_follow()
parser.build_table()

# Test simulation
parser.parse("id + id * id")