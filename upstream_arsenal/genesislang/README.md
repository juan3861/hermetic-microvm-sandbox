# GenesisLang v1.0 — GEN11

Linguagem compilada criada pelo motor evolutivo AetherMind GEN11.
Tokenizador 17.1x mais rápido que GEN18 (4.73M tok/s).

## Estrutura

```
GenesisLang/
├── compiler.py      # Compilador principal (CLI + REPL)
├── tokenizer.py     # Tokenizador GEN11 (4.73M tok/s)
├── parser.py        # Parser recursivo descendente
├── codegen.py       # Gerador de código (Python + JS)
├── examples/        # Programas exemplo
│   ├── fibonacci.gen
│   ├── fizzbuzz.gen
│   ├── factorial.gen
│   └── prime_sieve.gen
└── tests/           # Testes
```

## Uso

```bash
# Compilar e executar
python compiler.py run examples/fibonacci.gen

# Compilar para Python
python compiler.py build examples/fibonacci.gen

# Compilar para JavaScript
python compiler.py build examples/fibonacci.gen --js

# REPL interativo
python compiler.py repl
```

## Sintaxe

### Variáveis
```
let nome = "Ruan"
let idade = 25
let ativo = true
```

### Funções
```
fn soma(a, b) {
    return a + b
}

fn main() {
    emit soma(3, 4)
}
```

### Condicionais
```
if x > 10 {
    emit "grande"
} else {
    emit "pequeno"
}
```

### Loops
```
for i in 0..10 {
    emit i
}

while x > 0 {
    x = x - 1
    emit x
}
```

### Tipos
- `Int`: números inteiros (`42`, `0`, `-7`)
- `String`: texto (`"olá"`, `"mundo"`)
- `Bool`: `true` / `false`
- `List`: `[1, 2, 3]`
- `Null`: `null`

### Operadores
- Aritméticos: `+` `-` `*` `/` `%`
- Comparação: `==` `!=` `<` `>` `<=` `>=`
- Lógicos: `&&` `||` `!`
- Range: `..` (em loops for)

### Comentários
```
// comentário de linha
```

### Funções nativas
- `emit(expr)` — imprime no console
- `len(lista)` — tamanho da lista
- `push(lista, item)` — adiciona item à lista

## Performance

| Geração | ms | tok/s | Speedup |
|---------|-----|-------|---------|
| GEN0 (seed) | 0.1323 | 438K | 1.0x |
| GEN5 (frozenset) | 0.0130 | 4.45M | 10.2x |
| **GEN11 (champion)** | **0.0123** | **4.73M** | **10.7x** |
| GEN18 (baseline) | 0.2100 | 171K | — |
| **vs GEN18** | — | — | **17.1x** |

## Arquitetura do Tokenizador

- Zero regex no hot path
- Scan caractere-a-caractere
- Lookup O(1) via dict para keywords
- Aliases locais (`s = source`, `a = append`)
- Single-pass, sem backtracking
- Suporte a comentários `//`

## Backends

- **Python** (padrão) — compila para Python 3.x executável
- **JavaScript** — compila para JS (em desenvolvimento)
