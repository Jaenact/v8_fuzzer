from fuzzer.profiles import resolve_profile_flags


def test_resolve_profile_flags_maglev() -> None:
    flags = resolve_profile_flags("maglev")
    assert "--maglev" in flags
