import re
from collections import defaultdict

class DataFlowAnalyzer:
    def __init__(self, tac_code):
        self.tac_code = tac_code
        self.blocks = {}
        self.definitions = {}  # { 'd1': {'var': 'x', 'block': 'B1', 'text': 'x=1'} }
        self.block_order = []
        self.parse_code()

    def parse_code(self):
        lines = [line.strip() for line in self.tac_code.split('\n') if line.strip()]
        current_block = None
        def_counter = 1

        # Phase 1: Identify Blocks and Definitions
        for line in lines:
            if line.endswith(':'):
                current_block = line[:-1]
                self.block_order.append(current_block)
                self.blocks[current_block] = {
                    'lines': [], 'gen': set(), 'kill': set(),
                    'in': set(), 'out': set(), 'succ': set(), 'pred': set()
                }
            else:
                if not current_block:
                    current_block = "B0"
                    self.block_order.append(current_block)
                    self.blocks[current_block] = {'lines': [], 'gen': set(), 'kill': set(), 'in': set(), 'out': set(), 'succ': set(), 'pred': set()}
                
                # Check for definition (assignment)
                def_match = re.match(r'^(\w+)\s*=\s*(.+)$', line)
                is_def = def_match and '==' not in line
                
                stmt_info = {'text': line, 'is_def': False, 'def_id': None, 'var': None}
                
                if is_def:
                    d_id = f"d{def_counter}"
                    def_counter += 1
                    var_name = def_match.group(1)
                    stmt_info.update({'is_def': True, 'def_id': d_id, 'var': var_name})
                    self.definitions[d_id] = {'var': var_name, 'block': current_block, 'text': line}
                
                self.blocks[current_block]['lines'].append(stmt_info)

                # Check for control flow
                goto_match = re.search(r'goto\s+(\w+)', line)
                if goto_match:
                    dest = goto_match.group(1)
                    self.blocks[current_block]['succ'].add(dest)

        # Phase 2: Establish Predecessors and Fall-throughs
        for i, b_name in enumerate(self.block_order):
            # Handle implicit fall-through
            has_uncond_jump = any('goto' in l['text'] and 'if' not in l['text'] for l in self.blocks[b_name]['lines'])
            if not has_uncond_jump and i + 1 < len(self.block_order):
                self.blocks[b_name]['succ'].add(self.block_order[i+1])
            
            for s_name in self.blocks[b_name]['succ']:
                if s_name in self.blocks:
                    self.blocks[s_name]['pred'].add(b_name)

    def analyze(self):
        # 1. Compute Local GEN and KILL sets
        for b_name in self.block_order:
            b = self.blocks[b_name]
            defined_vars = set()
            
            # GEN: The last definition of a variable in the block
            for stmt in reversed(b['lines']):
                if stmt['is_def'] and stmt['var'] not in defined_vars:
                    b['gen'].add(stmt['def_id'])
                    defined_vars.add(stmt['var'])
            
            # KILL: All definitions of these variables in OTHER blocks
            for d_id, d_info in self.definitions.items():
                if d_info['block'] != b_name and d_info['var'] in defined_vars:
                    b['kill'].add(d_id)
            
            b['out'] = set(b['gen']) # Initialize OUT as GEN

        # 2. Iterative Fixed-Point Analysis
        iterations = 0
        while True:
            iterations += 1
            changed = False
            for b_name in self.block_order:
                b = self.blocks[b_name]
                
                # IN[B] = Union(OUT[P] for all predecessors P)
                new_in = set()
                for p_name in b['pred']:
                    new_in.update(self.blocks[p_name]['out'])
                b['in'] = new_in

                # OUT[B] = GEN[B] U (IN[B] - KILL[B])
                new_out = b['gen'].union(b['in'] - b['kill'])
                
                if new_out != b['out']:
                    b['out'] = new_out
                    changed = True
            
            if not changed: break
        return iterations

    def print_results(self):
        print(f"{'Block':<8} | {'GEN':<15} | {'KILL':<15} | {'IN':<15} | {'OUT':<15}")
        print("-" * 80)
        for b in self.block_order:
            data = self.blocks[b]
            f = lambda s: "{" + ",".join(sorted(s, key=lambda x: int(x[1:]))) + "}" if s else "∅"
            print(f"{b:<8} | {f(data['gen']):<15} | {f(data['kill']):<15} | {f(data['in']):<15} | {f(data['out']):<15}")

# --- Execution ---
tac_input = """
B1:
x = 5
y = 1

B2:
y = 2
if x > 0 goto B2

B3:
z = y
"""

analyzer = DataFlowAnalyzer(tac_input)
iters = analyzer.analyze()
analyzer.print_results()
print(f"\nConverged in {iters} iterations.")