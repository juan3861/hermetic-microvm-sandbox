# TensoLang v1.0 — Tensor Network Language

**O DISCÍPULO QUE SUPERA O MESTRE.**

Linguagem de programação com **Tensor Network embutida** no runtime.
Compressão alienígena via SVD, MPS (Matrix Product State) e TT (Tensor Train).

## Filosofia

> Tudo é tensor. Código = Rede Tensorial.
> Execução = Contração. Compressão = Sobrevivência.

Enquanto linguagens tradicionais tratam código como texto e dados como bits,
TensoLang trata **tudo como tensores** que são naturalmente comprimidos
via decomposição tensorial. O compilador encontra padrões latentes que
o programador nem sabia que existiam.

## Estrutura

```
TensoLang/
├── compiler.py       # CLI (run, repl, demo)
├── tokenizer.py      # Tokenizador (base GEN11)
├── parser.py         # Parser recursivo completo
├── runtime.py        # Runtime com Tensor Network
├── tensor_core.py    # Motor tensorial (SVD, MPS, TT)
├── examples/
│   ├── demo_compressao.tn
│   ├── rede_mps.tn
│   ├── compress_imagem.tn
│   └── fibonacci_compressed.tn
└── README.md
```

## Uso

```bash
# Executar programa
python compiler.py run examples/demo_compressao.tn

# Demonstração do motor tensorial
python compiler.py demo

# REPL interativo
python compiler.py repl
```

## Sintaxe

### Variáveis Tensoriais
```
tensor v = [1, 2, 3, 4]           // vetor (tensor 1D)
tensor M = [[1,0],[0,1]]          // matriz (tensor 2D)
tensor T = [[[1,2],[3,4]],[[5,6],[7,8]]]  // tensor 3D
```

### Compressão Alienígena
```
// SVD com threshold de energia
let comprimido = compress(M, energy=0.95)

// Decomposição completa
let decomp = svd(T)

// Tensor Train (compressão multi-dimensional)
let tt = tt_decompose(T, max_rank=4)
```

### Redes Tensoriais (MPS)
```
network processador {
    site entrada = [1, 0.8, 0.6]
    site camada1 = [0.8, 1, 0.4]
    site camada2 = [0.6, 0.4, 1]

    compress(energy=0.90)   // comprime a rede
    contract()              // executa (contrai)
}
```

### Contração Tensorial
```
tensor a = [1, 2, 3]
tensor b = [4, 5, 6]
tensor c = a @ b    // operador @ = contração
```

### Funções
```
fn add(a, b) -> a + b           // arrow function
fn fib(n) {                     // block function
    if n <= 1 { return n }
    return fib(n-1) + fib(n-2)
}
```

### Métricas
```
let ratio = compress_ratio()    // razão de compressão média
let r = rank(T)                 // rank do tensor
let s = shape(T)                // dimensões
```

## Motor Tensorial

| Componente | Descrição |
|-----------|-----------|
| **SVD** | Decomposição em valores singulares com truncamento por energia |
| **MPS** | Matrix Product State — código sequencial como rede 1D |
| **TT** | Tensor Train — decomposição multi-dimensional |
| **Contração** | Operador `@` — contrai dois tensores |

## Compressão Alienígena

A "compressão alienígena" funciona assim:

1. Cada operação no código vira um **site** na rede tensorial
2. Conexões entre operações viram **bonds** (dimensões de entanglement)
3. A rede é comprimida via **SVD truncado** — apenas os componentes
   que carregam mais "energia" (informação) sobrevivem
4. O rank de compressão é determinado **automaticamente** pelo
   threshold de energia (padrão: 95%)

Isso significa que o código se **auto-otimiza** — padrões redundantes
são dissolvidos, estrutura latente emerge, e o programa roda
numa representação comprimida.

## Exemplos

| Arquivo | Descrição |
|---------|-----------|
| `demo_compressao.tn` | Compressão SVD, decomposição, contração |
| `rede_mps.tn` | Rede tensorial MPS com compressão |
| `compress_imagem.tn` | Compressão de matriz via SVD |
| `fibonacci_compressed.tn` | Fibonacci com métricas de compressão |
