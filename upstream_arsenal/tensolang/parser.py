"""
TensoLang Parser — Recursive Descent
Produz AST com suporte a tensores e redes.
"""

class ASTNode:
    def __init__(self, kind, **kwargs):
        self.kind = kind
        for k, v in kwargs.items():
            setattr(self, k, v)
    def __repr__(self):
        fields = ", ".join(f"{k}={v}" for k, v in vars(self).items() if k != "kind")
        return f"{self.kind}({fields})"

class ParseError(Exception):
    def __init__(self, msg, token=None):
        self.token = token
        loc = f" at '{token[1]}'" if token else ""
        super().__init__(f"{msg}{loc}")

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else ("EOF", "")

    def eat(self, kind=None, val=None):
        t = self.peek()
        if kind and t[0] != kind:
            raise ParseError(f"Expected {kind}, got {t[0]}", t)
        if val and t[1] != val:
            raise ParseError(f"Expected '{val}', got '{t[1]}'", t)
        self.pos += 1
        return t

    # ═══════════════════════════════════════════
    # PROGRAM
    # ═══════════════════════════════════════════
    def parse_program(self):
        stmts = []
        while self.pos < len(self.tokens):
            stmts.append(self.parse_stmt())
        return ASTNode("Program", stmts=stmts)

    def parse_stmt(self):
        t = self.peek()
        if t[0] == "KEYWORD":
            kw = t[1]
            if kw == "fn": return self.parse_fn()
            if kw == "tensor": return self.parse_tensor_decl()
            if kw == "let": return self.parse_let()
            if kw == "network": return self.parse_network()
            if kw == "emit": return self.parse_emit()
            if kw == "return": return self.parse_return()
            if kw == "if": return self.parse_if()
            if kw == "for": return self.parse_for()
            if kw == "while": return self.parse_while()
            if kw == "compress": return self.parse_expr_stmt()
            if kw == "contract": return self.parse_expr_stmt()
            if kw == "svd": return self.parse_expr_stmt()
            if kw == "tt": return self.parse_expr_stmt()
        if t[0] == "IDENT":
            return self.parse_assign_or_call()
        raise ParseError(f"Unexpected token", t)

    def parse_block(self):
        self.eat("SEP", "{")
        stmts = []
        while self.peek()[1] != "}":
            stmts.append(self.parse_stmt())
        self.eat("SEP", "}")
        return stmts

    # ═══════════════════════════════════════════
    # DECLARATIONS
    # ═══════════════════════════════════════════
    def parse_tensor_decl(self):
        self.eat("KEYWORD", "tensor")
        name = self.eat("IDENT")[1]
        self.eat("OP", "=")
        val = self.parse_expr()
        return ASTNode("TensorDecl", name=name, value=val)

    def parse_let(self):
        self.eat("KEYWORD", "let")
        name = self.eat("IDENT")[1]
        self.eat("OP", "=")
        val = self.parse_expr()
        return ASTNode("Let", name=name, value=val)

    def parse_fn(self):
        self.eat("KEYWORD", "fn")
        name = self.eat("IDENT")[1]
        self.eat("SEP", "(")
        params = []
        if self.peek()[1] != ")":
            params.append(self.eat("IDENT")[1])
            while self.peek()[1] == ",":
                self.eat("SEP", ",")
                params.append(self.eat("IDENT")[1])
        self.eat("SEP", ")")
        # Arrow function (single expression)
        if self.peek() == ("ARROW", "->"):
            self.eat("ARROW", "->")
            body_expr = self.parse_expr()
            return ASTNode("FnDef", name=name, params=params, body=body_expr, arrow=True)
        # Block function
        body = self.parse_block()
        return ASTNode("FnDef", name=name, params=params, body=body, arrow=False)

    def parse_network(self):
        self.eat("KEYWORD", "network")
        name = self.eat("IDENT")[1]
        self.eat("SEP", "{")
        stmts = []
        while self.peek()[1] != "}":
            stmts.append(self.parse_network_stmt())
        self.eat("SEP", "}")
        return ASTNode("NetworkDef", name=name, stmts=stmts)

    def parse_network_stmt(self):
        t = self.peek()
        if t == ("KEYWORD", "site"):
            self.eat("KEYWORD", "site")
            name = self.eat("IDENT")[1]
            self.eat("OP", "=")
            val = self.parse_expr()
            return ASTNode("SiteDecl", name=name, value=val)
        elif t == ("KEYWORD", "bond"):
            self.eat("KEYWORD", "bond")
            src = self.eat("IDENT")[1]
            self.eat("ARROW", "->")
            dst = self.eat("IDENT")[1]
            strength = None
            if self.peek() == ("OP", "="):
                self.eat("OP", "=")
                strength = self.parse_expr()
            return ASTNode("BondDecl", src=src, dst=dst, strength=strength)
        elif t == ("KEYWORD", "compress"):
            return self.parse_compress_cmd()
        elif t == ("KEYWORD", "contract"):
            return self.parse_contract_cmd()
        else:
            raise ParseError(f"Unexpected token in network", t)

    def parse_compress_cmd(self):
        self.eat("KEYWORD", "compress")
        self.eat("SEP", "(")
        kwargs = {}
        while self.peek()[1] != ")":
            key_t = self.peek()
            if key_t[0] in ("IDENT", "KEYWORD"):
                key = self.eat(key_t[0])[1]
            else:
                raise ParseError(f"Expected parameter name", key_t)
            self.eat("OP", "=")
            val = self.parse_expr()
            kwargs[key] = val
            if self.peek()[1] == ",":
                self.eat("SEP", ",")
        self.eat("SEP", ")")
        return ASTNode("CompressCmd", kwargs=kwargs)

    def parse_contract_cmd(self):
        self.eat("KEYWORD", "contract")
        self.eat("SEP", "(")
        self.eat("SEP", ")")
        return ASTNode("ContractCmd")

    # ═══════════════════════════════════════════
    # STATEMENTS
    # ═══════════════════════════════════════════
    def parse_emit(self):
        self.eat("KEYWORD", "emit")
        val = self.parse_expr()
        return ASTNode("Emit", value=val)

    def parse_return(self):
        self.eat("KEYWORD", "return")
        val = self.parse_expr() if self.peek()[1] not in ("}",) else None
        return ASTNode("Return", value=val)

    def parse_if(self):
        self.eat("KEYWORD", "if")
        cond = self.parse_expr()
        then_block = self.parse_block()
        else_block = None
        if self.peek() == ("KEYWORD", "else"):
            self.eat("KEYWORD", "else")
            if self.peek() == ("KEYWORD", "if"):
                else_block = [self.parse_if()]
            else:
                else_block = self.parse_block()
        return ASTNode("If", cond=cond, then_block=then_block, else_block=else_block or [])

    def parse_for(self):
        self.eat("KEYWORD", "for")
        var = self.eat("IDENT")[1]
        self.eat("KEYWORD", "in")
        start = self.parse_expr()
        self.eat("OP", "..")
        end = self.parse_expr()
        body = self.parse_block()
        return ASTNode("For", var=var, start=start, end=end, body=body)

    def parse_while(self):
        self.eat("KEYWORD", "while")
        cond = self.parse_expr()
        body = self.parse_block()
        return ASTNode("While", cond=cond, body=body)

    def parse_assign_or_call(self):
        name = self.eat("IDENT")[1]
        if self.peek() == ("SEP", "("):
            return self._parse_call(name)
        if self.peek() == ("OP", "="):
            self.eat("OP", "=")
            val = self.parse_expr()
            return ASTNode("Assign", name=name, value=val)
        if self.peek() == ("OP", "."):
            self.eat("OP", ".")
            member = self.eat("IDENT")[1]
            return ASTNode("Member", obj=name, member=member)
        raise ParseError(f"Expected '=' or '(' after ident", self.peek())

    def parse_expr_stmt(self):
        expr = self.parse_expr()
        return ASTNode("ExprStmt", expr=expr)

    def _parse_call(self, name):
        self.eat("SEP", "(")
        args = []
        kwargs = {}
        while self.peek()[1] != ")":
            if self.peek()[0] in ("IDENT", "KEYWORD") and self._lookahead_is_kwarg():
                key = self.eat(self.peek()[0])[1]
                self.eat("OP", "=")
                val = self.parse_expr()
                kwargs[key] = val
            else:
                args.append(self.parse_expr())
            if self.peek()[1] == ",":
                self.eat("SEP", ",")
        self.eat("SEP", ")")
        return ASTNode("FnCall", name=name, args=args, kwargs=kwargs)

    def _lookahead_is_kwarg(self):
        """Verifica se o próximo token é '=' (keyword argument)."""
        saved = self.pos
        try:
            t = self.peek()
            if t[0] in ("IDENT", "KEYWORD"):
                self.eat(t[0])
                is_kw = self.peek() == ("OP", "=")
                self.pos = saved
                return is_kw
            self.pos = saved
            return False
        except:
            self.pos = saved
            return False

    # ═══════════════════════════════════════════
    # EXPRESSIONS
    # ═══════════════════════════════════════════
    def parse_expr(self):
        return self.parse_contract()

    def parse_contract(self):
        """Contração tensorial (@) — menor precedência."""
        left = self.parse_compare()
        while self.peek() == ("OP", "@"):
            self.eat("OP", "@")
            right = self.parse_compare()
            left = ASTNode("TensorContract", left=left, right=right)
        return left

    def parse_compare(self):
        left = self.parse_add()
        ops = {"==", "!=", "<", ">", "<=", ">="}
        if self.peek()[0] == "OP" and self.peek()[1] in ops:
            op = self.eat("OP")[1]
            right = self.parse_add()
            return ASTNode("BinaryOp", op=op, left=left, right=right)
        return left

    def parse_add(self):
        left = self.parse_mul()
        while self.peek() == ("OP", "+") or self.peek() == ("OP", "-"):
            op = self.eat("OP")[1]
            right = self.parse_mul()
            left = ASTNode("BinaryOp", op=op, left=left, right=right)
        return left

    def parse_mul(self):
        left = self.parse_unary()
        while self.peek() == ("OP", "*") or self.peek() == ("OP", "/") or self.peek() == ("OP", "%"):
            op = self.eat("OP")[1]
            right = self.parse_unary()
            left = ASTNode("BinaryOp", op=op, left=left, right=right)
        return left

    def parse_unary(self):
        if self.peek() == ("OP", "-") or self.peek() == ("OP", "!"):
            op = self.eat("OP")[1]
            return ASTNode("UnaryOp", op=op, operand=self.parse_atom())
        return self.parse_atom()

    def parse_atom(self):
        t = self.peek()
        if t[0] == "NUMBER":
            self.eat("NUMBER")
            v = float(t[1]) if '.' in t[1] else int(t[1])
            return ASTNode("Number", value=v)
        if t[0] == "STRING":
            self.eat("STRING")
            return ASTNode("String", value=t[1][1:-1])
        if t == ("KEYWORD", "true"):
            self.eat("KEYWORD", "true")
            return ASTNode("Bool", value=True)
        if t == ("KEYWORD", "false"):
            self.eat("KEYWORD", "false")
            return ASTNode("Bool", value=False)
        if t == ("KEYWORD", "null"):
            self.eat("KEYWORD", "null")
            return ASTNode("Null")
        if t == ("SEP", "["):
            return self.parse_tensor_literal()
        if t == ("SEP", "("):
            self.eat("SEP", "(")
            expr = self.parse_expr()
            self.eat("SEP", ")")
            return expr
        if t[0] == "IDENT":
            name = self.eat("IDENT")[1]
            if self.peek() == ("SEP", "("):
                return self._parse_call(name)
            if self.peek() == ("OP", "."):
                self.eat("OP", ".")
                member = self.eat("IDENT")[1]
                return ASTNode("Member", obj=name, member=member)
            return ASTNode("Var", name=name)
        if t[0] == "KEYWORD":
            kw = t[1]
            if kw == "compress":
                self.eat("KEYWORD", "compress")
                self.eat("SEP", "(")
                target = self.parse_expr()
                kwargs = {}
                while self.peek()[1] == ",":
                    self.eat("SEP", ",")
                    key_t = self.peek()
                    if key_t[0] in ("IDENT", "KEYWORD"):
                        key = self.eat(key_t[0])[1]
                    else:
                        raise ParseError(f"Expected parameter name, got {key_t[0]}", key_t)
                    self.eat("OP", "=")
                    kwargs[key] = self.parse_expr()
                self.eat("SEP", ")")
                return ASTNode("CompressExpr", target=target, kwargs=kwargs)
            if kw == "svd":
                self.eat("KEYWORD", "svd")
                self.eat("SEP", "(")
                target = self.parse_expr()
                kwargs = {}
                while self.peek()[1] == ",":
                    self.eat("SEP", ",")
                    key_t = self.peek()
                    if key_t[0] in ("IDENT", "KEYWORD"):
                        key = self.eat(key_t[0])[1]
                    else:
                        raise ParseError(f"Expected parameter name, got {key_t[0]}", key_t)
                    self.eat("OP", "=")
                    kwargs[key] = self.parse_expr()
                self.eat("SEP", ")")
                return ASTNode("SVDExpr", target=target, kwargs=kwargs)
        raise ParseError(f"Unexpected token in expression", t)

    def parse_tensor_literal(self):
        """Parse tensor literal: [1, 2, 3] or [[1,0],[0,1]]"""
        items = self._parse_list_items()
        return ASTNode("TensorLit", items=items)

    def _parse_list_items(self):
        self.eat("SEP", "[")
        items = []
        if self.peek()[1] != "]":
            if self.peek() == ("SEP", "["):
                items.append(self._parse_list_items())
            else:
                items.append(self.parse_expr())
            while self.peek()[1] == ",":
                self.eat("SEP", ",")
                if self.peek()[1] == "]":
                    break  # trailing comma
                if self.peek() == ("SEP", "["):
                    items.append(self._parse_list_items())
                else:
                    items.append(self.parse_expr())
        self.eat("SEP", "]")
        return items


def parse(tokens):
    parser = Parser(tokens)
    return parser.parse_program()
