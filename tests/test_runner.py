from fuzzer.runner import D8Runner, RunResult, differential_interesting


def test_differential_interesting_on_return_code() -> None:
    a = RunResult(0, False, "", "", ["d8"])
    b = RunResult(1, False, "", "", ["d8"])
    assert differential_interesting(a, b)


def test_runner_cmd_includes_extra_flags() -> None:
    r = D8Runner("/tmp/d8", flags=["--stress-opt"])
    cmd = r._cmd(__import__('pathlib').Path("/tmp/a.js"), extra_flags=["--trace-turbo"])
    assert "--stress-opt" in cmd
    assert "--trace-turbo" in cmd
