"""
GenesisLang Parser — Recursive Descent
Produces AST from token stream.
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
        super().__init__(f"{msg}" + (f" at '{token[1]}'" if token else ""))

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

    def parse_program(self):
        stmts = []
        while self.pos < len(self.tokens):
            stmts.append(self.parse_stmt())
        return ASTNode("Program", stmts=stmts)

    def parse_stmt(self):
        t = self.peek()
        if t[0] == "KEYWORD":
            if t[1] == "fn": return self.parse_fn()
            if t[1] == "let": return self.parse_let()
            if t[1] == "if": return self.parse_if()
            if t[1] == "for": return self.parse_for()
            if t[1] == "while": return self.parse_while()
            if t[1] == "return": return self.parse_return()
            if t[1] == "emit": return self.parse_emit()
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
        body = self.parse_block()
        return ASTNode("FnDef", name=name, params=params, body=body)

    def parse_let(self):
        self.eat("KEYWORD", "let")
        name = self.eat("IDENT")[1]
        self.eat("OP", "=")
        val = self.parse_expr()
        return ASTNode("Let", name=name, value=val)

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

    def parse_return(self):
        self.eat("KEYWORD", "return")
        val = self.parse_expr() if self.peek()[1] not in ("}", ";") else None
        return ASTNode("Return", value=val)

    def parse_emit(self):
        self.eat("KEYWORD", "emit")
        val = self.parse_expr()
        return ASTNode("Emit", value=val)

    def parse_assign_or_call(self):
        name = self.eat("IDENT")[1]
        # fn call
        if self.peek() == ("SEP", "("):
            self.eat("SEP", "(")
            args = []
            if self.peek()[1] != ")":
                args.append(self.parse_expr())
                while self.peek()[1] == ",":
                    self.eat("SEP", ",")
                    args.append(self.parse_expr())
            self.eat("SEP", ")")
            return ASTNode("FnCall", name=name, args=args)
        # assignment
        if self.peek() == ("OP", "="):
            self.eat("OP", "=")
            val = self.parse_expr()
            return ASTNode("Assign", name=name, value=val)
        # member access
        if self.peek() == ("OP", "."):
            self.eat("OP", ".")
            member = self.eat("IDENT")[1]
            # method call
            if self.peek() == ("SEP", "("):
                self.eat("SEP", "(")
                args = []
                if self.peek()[1] != ")":
                    args.append(self.parse_expr())
                    while self.peek()[1] == ",":
                        self.eat("SEP", ",")
                        args.append(self.parse_expr())
                self.eat("SEP", ")")
                return ASTNode("MethodCall", obj=name, method=member, args=args)
            return ASTNode("Member", obj=name, member=member)
        raise ParseError(f"Expected '=' or '(' after ident", self.peek())

    def parse_expr(self):
        return self.parse_or()

    def parse_or(self):
        left = self.parse_and()
        while self.peek() == ("OP", "||"):
            self.eat("OP", "||")
            right = self.parse_and()
            left = ASTNode("BinaryOp", op="||", left=left, right=right)
        return left

    def parse_and(self):
        left = self.parse_compare()
        while self.peek() == ("OP", "&&"):
            self.eat("OP", "&&")
            right = self.parse_compare()
            left = ASTNode("BinaryOp", op="&&", left=left, right=right)
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
        if t[0] == "INT":
            self.eat("INT")
            return ASTNode("Int", value=int(t[1]))
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
        if t[0] == "IDENT":
            name = self.eat("IDENT")[1]
            # fn call
            if self.peek() == ("SEP", "("):
                self.eat("SEP", "(")
                args = []
                if self.peek()[1] != ")":
                    args.append(self.parse_expr())
                    while self.peek()[1] == ",":
                        self.eat("SEP", ",")
                        args.append(self.parse_expr())
                self.eat("SEP", ")")
                return ASTNode("FnCall", name=name, args=args)
            # member access
            if self.peek() == ("OP", "."):
                self.eat("OP", ".")
                member = self.eat("IDENT")[1]
                if self.peek() == ("SEP", "("):
                    self.eat("SEP", "(")
                    args = []
                    if self.peek()[1] != ")":
                        args.append(self.parse_expr())
                        while self.peek()[1] == ",":
                            self.eat("SEP", ",")
                            args.append(self.parse_expr())
                    self.eat("SEP", ")")
                    return ASTNode("MethodCall", obj=name, method=member, args=args)
                return ASTNode("Member", obj=name, member=member)
            return ASTNode("Var", name=name)
        if t == ("SEP", "("):
            self.eat("SEP", "(")
            expr = self.parse_expr()
            self.eat("SEP", ")")
            return expr
        if t == ("SEP", "["):
            return self.parse_list()
        raise ParseError(f"Unexpected token in expression", t)

    def parse_list(self):
        self.eat("SEP", "[")
        items = []
        if self.peek()[1] != "]":
            items.append(self.parse_expr())
            while self.peek()[1] == ",":
                self.eat("SEP", ",")
                items.append(self.parse_expr())
        self.eat("SEP", "]")
        return ASTNode("List", items=items)


def parse(tokens):
    parser = Parser(tokens)
    return parser.parse_program()
