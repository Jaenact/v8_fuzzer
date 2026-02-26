import random

from fuzzer.corpus import Corpus
from fuzzer.mutators import tweak_numeric_literal


def test_mutate_text_preserves_nonempty_output() -> None:
    rng = random.Random(7)
    src = "let a = 0;\nlet b = 1;\n"
    out = tweak_numeric_literal(src, rng)
    assert out.strip()


def test_corpus_choose_seed_returns_name(tmp_path) -> None:
    c = Corpus(tmp_path)
    c.add("function x(){ return 1; }\n")
    text, name = c.choose_seed(random.Random(1))
    assert text is not None
    assert name is not None
    assert name.endswith('.js')


def test_import_directory_dedups_content(tmp_path) -> None:
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.js").write_text("let x=1;\n", encoding="utf-8")
    (src / "b.js").write_text("let x=1;\n", encoding="utf-8")
    (src / "c.js").write_text("let y=2;\n", encoding="utf-8")

    c = Corpus(tmp_path / "corpus")
    added = c.import_directory(src)
    assert added == 2
    assert len(c.seeds()) == 2
