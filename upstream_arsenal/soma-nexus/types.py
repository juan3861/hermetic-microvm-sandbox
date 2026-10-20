"""
ΨΩ SOMA-NEXUS — Sistema de Tipos Cognitivos
============================================
80 tipos do APEX + extensoes OMEGA + tipos SOMA.
Cada tipo carrega metadados cognitivos: salience, trust, decay, energy.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
import time


class CogTrust(Enum):
    """Trust level — AXIOMA §01 TrustType"""
    BLIND = 0
    WORKING = 1
    SEMANTIC = 2
    TRUSTED = 3
    PROVEN = 4


class CogPhase(Enum):
    """Execution phase — AXIOMA §28 PolicyCode"""
    REFLEX = "reflex"       # <10ms
    ANALYTIC = "analytic"   # <1s
    FORENSIC = "forensic"   # <60s
    AGENTIC = "agentic"     # autonomo


@dataclass
class CogMeta:
    """Metadados cognitivos — todo tipo Cog carrega isso."""
    salience: float = 1.0        # 0..∞ — quanto maior, mais atenção
    trust: CogTrust = CogTrust.WORKING
    decay: float = 0.99          # fator de decaimento por tick
    created_at: float = field(default_factory=time.time)
    energy_budget: float = 1.0   # budget cognitivo (AXIOMA §03)
    source: str = ""             # origem do dado

    def tick(self):
        """Decai a saliência a cada ciclo."""
        self.salience *= self.decay


# ═══ TIPOS PRIMITIVOS ═══

@dataclass
class CogInt:
    """Inteiro cognitivo."""
    value: int
    meta: CogMeta = field(default_factory=CogMeta)

    def __int__(self): return self.value
    def __repr__(self): return f"{self.value}"


@dataclass
class CogFloat:
    """Float cognitivo."""
    value: float
    meta: CogMeta = field(default_factory=CogMeta)

    def __float__(self): return self.value
    def __repr__(self): return f"{self.value}"


@dataclass
class CogStr:
    """String cognitiva."""
    value: str
    meta: CogMeta = field(default_factory=CogMeta)

    def __str__(self): return self.value
    def __repr__(self): return f'"{self.value}"'


@dataclass
class CogBool:
    """Booleano cognitivo."""
    value: bool
    meta: CogMeta = field(default_factory=CogMeta)

    def __bool__(self): return self.value
    def __repr__(self): return str(self.value)


@dataclass
class CogStream:
    """Stream cognitivo — AXIOMA §10."""
    values: list = field(default_factory=list)
    meta: CogMeta = field(default_factory=CogMeta)


# ═══ TIPOS COMPOSTOS ═══

@dataclass
class CogList:
    """Lista cognitiva."""
    items: list = field(default_factory=list)
    meta: CogMeta = field(default_factory=CogMeta)

    def __repr__(self): return f"[{', '.join(map(str, self.items))}]"


# ═══ TIPOS AVANCADOS (v5 APEX) ═══

@dataclass
class LinearRes:
    """Recurso linear — AXIOMA §49 LinearTypes. Uma vez consumido, nao pode ser reusado."""
    value: Any
    consumed: bool = False
    meta: CogMeta = field(default_factory=CogMeta)

    def consume(self):
        if self.consumed:
            raise ValueError("LinearRes ja consumido")
        self.consumed = True
        return self.value


@dataclass
class EffectAlg:
    """Algébrico de efeitos — AXIOMA §50. Efeitos pure/mut/io/net."""
    effect_type: str  # "pure", "mut", "io", "net", "quantum"
    handler: Optional[callable] = None
    meta: CogMeta = field(default_factory=CogMeta)


@dataclass
class QuantumRes:
    """Recurso pos-quantico — AXIOMA §51. 128+ bits seguranca."""
    key_hash: str
    algorithm: str = "kyber1024"
    meta: CogMeta = field(default_factory=CogMeta)


# ═══ TIPOS SOMA (FORGE-Ω V8) ═══

@dataclass
class SomaVector:
    """Vetor SOMA — estado esparso oscilante."""
    dim: int
    sparsity: float = 0.94      # ~94% sparse (SNN)
    weights: list = field(default_factory=list)
    meta: CogMeta = field(default_factory=CogMeta)


@dataclass
class SomaState:
    """Estado SOMA — SSM + Transformer fusion."""
    hidden: list  # h_t
    kv_cache: Optional[Any] = None  # c_t^KV (MLA compression)
    meta: CogMeta = field(default_factory=CogMeta)


# ═══ TYPE CONSTRUCTORS ═══

def Int(value: Any) -> CogInt:
    return CogInt(int(value))

def Float(value: Any) -> CogFloat:
    return CogFloat(float(value))

def Str(value: Any) -> CogStr:
    return CogStr(str(value))

def Bool(value: Any) -> CogBool:
    return CogBool(bool(value))
