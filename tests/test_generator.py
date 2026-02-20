import random

from fuzzer.generator import generate_program


def test_generate_program_contains_engine_features() -> None:
    rng = random.Random(1)
    sample = "\n".join(generate_program(rng) for _ in range(20))
    assert "function" in sample
    assert any(token in sample for token in ["Proxy", "DataView", "WebAssembly", "%OptimizeFunctionOnNextCall"])
