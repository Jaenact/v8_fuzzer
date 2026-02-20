from fuzzer.runner import RunResult, differential_interesting


def test_differential_interesting_on_return_code() -> None:
    a = RunResult(0, False, "", "", ["d8"])
    b = RunResult(1, False, "", "", ["d8"])
    assert differential_interesting(a, b)
