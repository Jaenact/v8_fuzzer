import random

from fuzzer.generator import generate_program


def test_generate_program_contains_function() -> None:
    rng = random.Random(1)
    program = generate_program(rng)
    assert "function" in program
