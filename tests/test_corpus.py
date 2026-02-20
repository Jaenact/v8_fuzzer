import random

from fuzzer.corpus import mutate_text


def test_mutate_text_preserves_nonempty_output() -> None:
    rng = random.Random(7)
    src = "let a = 0;\nlet b = 1;\n"
    out = mutate_text(src, rng)
    assert out.strip()
    assert out != ""
