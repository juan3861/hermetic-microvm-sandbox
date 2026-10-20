"""
TensoLang Runtime v2 — Com propagação correta de return via exceção.
"""
import sys, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

class ReturnValue(Exception):
    def __init__(self, value): self.value = value

class ASTNode:
    def __init__(self, kind, **kwargs):
        self.kind = kind
        for k, v in kwargs.items(): setattr(self, k, v)

class TensoRuntime:
    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.networks = {}
        self.tensor_core = None
        self.compression_log = []

    def _ensure_core(self):
        if self.tensor_core is None:
            import tensor_core as tc
            self.tensor_core = tc

    def execute(self, ast):
        for stmt in ast.stmts:
            self._exec_stmt(stmt)

    def _exec_stmt(self, node):
        kind = node.kind
        method = getattr(self, f"_exec_{kind}", None)
        if method: return method(node)
        raise NotImplementedError(f"No executor for {kind}")

    def _exec_Program(self, node):
        for s in node.stmts: self._exec_stmt(s)

    def _exec_TensorDecl(self, node):
        val = self._eval(node.value)
        if isinstance(val, list):
            self._ensure_core()
            t = self.tensor_core.Tensor.from_list(val)
            self.variables[node.name] = t
            print(f"  [tensor] {node.name}: shape={t.shape}, params={t.size}")
        else:
            self.variables[node.name] = val

    def _exec_Let(self, node): self.variables[node.name] = self._eval(node.value)
    def _exec_Assign(self, node): self.variables[node.name] = self._eval(node.value)
    def _exec_FnDef(self, node): self.functions[node.name] = node
    def _exec_ExprStmt(self, node): return self._eval(node.expr)

    def _exec_NetworkDef(self, node):
        self._ensure_core()
        mps = self.tensor_core.MPS(name=node.name)
        for stmt in node.stmts:
            if stmt.kind == "SiteDecl":
                val = self._eval(stmt.value)
                if isinstance(val, list): mps.add_node(val, site_name=stmt.name, energy=1.0)
                elif isinstance(val, self.tensor_core.Tensor): mps.add_node(val.data, site_name=stmt.name, energy=1.0)
                else: mps.add_node([float(val)], site_name=stmt.name)
            elif stmt.kind == "BondDecl":
                strength = self._eval(stmt.strength) if stmt.strength else 1.0
                mps.add_bond(stmt.src, stmt.dst, strength=strength)
            elif stmt.kind == "CompressCmd":
                kwargs = {k: self._eval(v) for k, v in stmt.kwargs.items()}
                energy = kwargs.get("energy", 0.95)
                max_rank = kwargs.get("rank", None)
                before = sum(n.tensor.size for n in mps.nodes)
                mps.compress(max_bond=max_rank, energy_threshold=energy)
                after = sum(n.tensor.size for n in mps.nodes)
                ratio = before / after if after > 0 else 1.0
                self.compression_log.append({"network": node.name, "op": "compress",
                    "ratio": round(ratio, 2) if isinstance(ratio, float) else ratio, "energy": energy})
                print(f"  [compress] {node.name}: {ratio:.1f}x, sites={mps.stats()['sites']}")
            elif stmt.kind == "ContractCmd":
                result = mps.contract()
                self.variables[node.name] = result
                print(f"  [contract] {node.name}: result shape={result.shape}")
        self.networks[node.name] = mps

    def _exec_Return(self, node):
        val = self._eval(node.value) if node.value else None
        raise ReturnValue(val)

    def _exec_Emit(self, node): print(self._eval(node.value))

    def _exec_If(self, node):
        if self._eval(node.cond):
            for s in node.then_block: self._exec_stmt(s)
        elif node.else_block:
            for s in node.else_block: self._exec_stmt(s)

    def _exec_For(self, node):
        start, end = int(self._eval(node.start)), int(self._eval(node.end))
        for i in range(start, end):
            self.variables[node.var] = i
            for s in node.body: self._exec_stmt(s)

    def _exec_While(self, node):
        while self._eval(node.cond):
            for s in node.body: self._exec_stmt(s)

    def _exec_FnCall(self, node):
        fn = self.functions.get(node.name)
        if fn:
            saved = dict(self.variables)
            for p, a in zip(fn.params, node.args): self.variables[p] = self._eval(a)
            try:
                if fn.arrow:
                    result = self._eval(fn.body)
                else:
                    for s in fn.body: self._exec_stmt(s)
                return None
            except ReturnValue as rv:
                return rv.value
            finally:
                self.variables = saved
        else:
            return self._call_builtin(node.name, node.args, node.kwargs)

    def _exec_TensorContract(self, node):
        self._ensure_core()
        left, right = self._eval(node.left), self._eval(node.right)
        if isinstance(left, self.tensor_core.Tensor) and isinstance(right, self.tensor_core.Tensor):
            return self.tensor_core._contract_tensors(left, right)
        return None

    def _exec_CompressExpr(self, node):
        self._ensure_core()
        target = self._eval(node.target)
        kwargs = {k: self._eval(v) for k, v in node.kwargs.items()}
        if isinstance(target, self.tensor_core.Tensor):
            mat = target.to_matrix()
            U, S, Vt = self.tensor_core.svd(mat, kwargs.get("rank"))
            U, S, Vt = self.tensor_core.svd_truncate(U, S, Vt, kwargs.get("energy", 0.95))
            ratio = self.tensor_core.compression_ratio(U, S, Vt, (len(mat), len(mat[0]) if mat else 0))
            self.compression_log.append({"op": "compress_expr", "ratio": round(ratio, 2), "energy": kwargs.get("energy", 0.95)})
            print(f"  [compress] shape{target.shape} → rank={len(S)}, {ratio:.1f}x, energy={kwargs.get('energy',0.95)*100:.0f}%")
            return {"U": U, "S": S, "Vt": Vt, "ratio": ratio}
        return None

    def _exec_SVDExpr(self, node):
        self._ensure_core()
        target = self._eval(node.target)
        if isinstance(target, self.tensor_core.Tensor):
            U, S, Vt = self.tensor_core.svd(target.to_matrix())
            kwargs = {k: self._eval(v) for k, v in node.kwargs.items()}
            U, S, Vt = self.tensor_core.svd_truncate(U, S, Vt, kwargs.get("energy", 0.95))
            print(f"  [svd] singular values: {[round(s,4) for s in S[:5]]}{'...' if len(S)>5 else ''}")
            return {"U": U, "S": S, "Vt": Vt}
        return None

    def _call_builtin(self, name, args, kwargs):
        self._ensure_core()
        evaled = [self._eval(a) for a in args]
        if name == "len": return len(evaled[0]) if evaled else 0
        if name == "str": return str(evaled[0]) if evaled else ""
        if name == "compress_ratio":
            ratios = [e["ratio"] for e in self.compression_log if isinstance(e.get("ratio"), (int, float))]
            return sum(ratios)/len(ratios) if ratios else 1.0
        raise NameError(f"Unknown: {name}")

    # ── EVAL ──
    def _eval(self, node):
        if node is None: return None
        method = getattr(self, f"_eval_{node.kind}", None)
        if method: return method(node)
        raise NotImplementedError(f"No evaluator for {node.kind}")

    def _eval_Number(self, n): return n.value
    def _eval_String(self, n): return n.value
    def _eval_Bool(self, n): return n.value
    def _eval_Null(self, n): return None
    def _eval_Var(self, n):
        if n.name in self.variables: return self.variables[n.name]
        raise NameError(f"Variable '{n.name}' not defined")

    def _eval_BinaryOp(self, node):
        l, r, op = self._eval(node.left), self._eval(node.right), node.op
        if op == "+" and (isinstance(l, str) or isinstance(r, str)): return str(l) + str(r)
        ops = {"+": lambda a,b: a+b, "-": lambda a,b: a-b, "*": lambda a,b: a*b,
               "/": lambda a,b: a/b, "%": lambda a,b: a%b,
               "==": lambda a,b: a==b, "!=": lambda a,b: a!=b,
               "<": lambda a,b: a<b, ">": lambda a,b: a>b,
               "<=": lambda a,b: a<=b, ">=": lambda a,b: a>=b}
        if op in ops: return ops[op](l, r)
        raise ValueError(f"Unknown op: {op}")

    def _eval_UnaryOp(self, n):
        v = self._eval(n.operand)
        return -v if n.op == "-" else not v

    def _eval_TensorLit(self, n):
        def resolve(item):
            if isinstance(item, list): return [resolve(i) for i in item]
            return self._eval(item)
        return resolve(n.items)

    def _eval_FnCall(self, n): return self._exec_FnCall(n)
    def _eval_TensorContract(self, n): return self._exec_TensorContract(n)
    def _eval_CompressExpr(self, n): return self._exec_CompressExpr(n)
    def _eval_SVDExpr(self, n): return self._exec_SVDExpr(n)

    def _eval_Member(self, n):
        obj = self._eval(ASTNode("Var", name=n.obj))
        if isinstance(obj, dict):
            return obj.get(n.member)
        return getattr(obj, n.member, None)


def compile_and_run(source):
    from tokenizer import tokenize
    from parser import parse
    tokens = tokenize(source)
    ast = parse(tokens)
    runtime = TensoRuntime()
    runtime.execute(ast)
    if "main" in runtime.functions:
        fn = runtime.functions["main"]
        saved = dict(runtime.variables)
        try:
            for s in fn.body: runtime._exec_stmt(s)
        except ReturnValue:
            pass
        runtime.variables = saved
    if runtime.compression_log:
        print()
        print("═" * 50)
        print("  RELATÓRIO DE COMPRESSÃO ALIENÍGENA")
        print("═" * 50)
        for e in runtime.compression_log:
            label = e.get("network", e.get("op", "?"))
            print(f"  [{label}] {e.get('ratio', '?')}x @ {e.get('energy', 0.95)*100:.0f}% energia")
        print(f"  Compressão média: {runtime._call_builtin('compress_ratio', [], {}):.1f}x")
        print("═" * 50)
    return runtime

def run_file(path):
    return compile_and_run(Path(path).read_text(encoding="utf-8"))
