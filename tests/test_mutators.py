import random

from fuzzer.mutators import MutatorPool


def test_mutator_stats_exposed() -> None:
    pool = MutatorPool()
    m = pool.choose(random.Random(0))
    pool.reward(m.name, 1.0)
    stats = pool.stats()
    assert stats
    assert all("name" in item and "score" in item for item in stats)
