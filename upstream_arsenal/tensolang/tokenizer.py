"""
TensoLang Tokenizer
Baseado no GEN11 Champion, estendido para sintaxe tensorial.
"""
_KW = {
    "fn":1, "let":1, "tensor":1, "network":1, "site":1, "bond":1,
    "if":1, "else":1, "return":1, "emit":1, "for":1, "in":1,
    "while":1, "compress":1, "contract":1, "svd":1, "tt":1, "mps":1,
    "true":1, "false":1, "null":1,
}
_OP = set("+-*/%@<>=!&|.→:")
_SEP = set("[](),:;{}")

def tokenize(source):
    tokens = []
    pos = 0
    n = len(source)
    a = tokens.append
    s = source
    while pos < n:
        c = s[pos]
        # String
        if c == '"':
            e = s.find('"', pos + 1)
            if e == -1: e = n - 1
            a(("STRING", s[pos:e+1]))
            pos = e + 1
        # Comment //
        elif c == '/' and pos + 1 < n and s[pos+1] == '/':
            e = s.find('\n', pos + 2)
            if e == -1: e = n
            pos = e
        # Arrow ->
        elif c == '-' and pos + 1 < n and s[pos+1] == '>':
            a(("ARROW", "->"))
            pos += 2
        # Ident or keyword
        elif c.isalpha() or c == '_':
            e = pos + 1
            while e < n and (s[e].isalnum() or s[e] == '_'): e += 1
            w = s[pos:e]
            a(("KEYWORD" if w in _KW else "IDENT", w))
            pos = e
        # Number (int or float) — handle range operator '..'
        elif c.isdigit():
            e = pos + 1
            dot_seen = False
            while e < n and (s[e].isdigit() or (s[e] == '.' and not dot_seen)):
                if s[e] == '.':
                    # Só consome o ponto se for parte de float (seguido de dígito)
                    if e + 1 < n and s[e + 1].isdigit():
                        dot_seen = True
                    else:
                        break  # '..' range operator, para antes
                e += 1
            num = s[pos:e]
            # Se terminou com '.', devolve o ponto
            if num.endswith('.'):
                num = num[:-1]
                e -= 1
            if num:
                a(("NUMBER", num))
            pos = e
        # Operator or dot
        elif c in _OP:
            e = pos + 1
            while e < n and s[e] in _OP: e += 1
            a(("OP", s[pos:e]))
            pos = e
        # Separator
        elif c in _SEP:
            a(("SEP", c))
            pos += 1
        # Whitespace
        else:
            pos += 1
    return tokens
