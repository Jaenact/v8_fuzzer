from fuzzer.reducer import minimize_by_lines


def test_minimize_by_lines_reduces_program() -> None:
    src = """
let a = 1;
let b = 2;
throw new Error('boom');
let c = 3;
"""

    def interesting(s: str) -> bool:
        return "throw new Error('boom');" in s

    out = minimize_by_lines(src, interesting)
    assert "throw new Error('boom');" in out
    assert len(out.splitlines()) <= len(src.splitlines())
