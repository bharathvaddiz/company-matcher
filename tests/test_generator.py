# python
import company_match.pipeline.generator as generator


def test_generate_realistic_names_default_count(monkeypatch):
    # make fake.company deterministic
    monkeypatch.setattr(generator.fake, "company", lambda: "Acme Corp")
    res = generator.generate_realistic_names()
    assert isinstance(res, list)
    assert len(res) == 10
    assert all(isinstance(x, str) for x in res)
    assert all(x == "Acme Corp" for x in res)


def test_generate_realistic_names_custom_n(monkeypatch):
    monkeypatch.setattr(generator.fake, "company", lambda: "X")
    res = generator.generate_realistic_names(n=3)
    assert len(res) == 3
    assert res == ["X", "X", "X"]


def test_dirty_name_phonetic_replacement(monkeypatch):
    # Input contains 'tech', 'services', 'limited' -> expect replacements
    # Prepare random.random() sequence:
    #  - one value per phonetic_variations key (12 keys) -> return 0.1 for matching keys, 0.9 otherwise
    #  - vowel removal check -> 0.9 (no removal)
    #  - small swap check -> 0.9 (no swap)
    #  - final capitalization choice -> 0.9 (use n.capitalize())
    seq = []
    keys_order = [
        "services", "solutions", "industries", "consulting", "global", "tech",
        "technology", "company", "limited", "software", "systems", "corporation"
    ]
    for k in keys_order:
        # return 0.1 for keys we want replaced, else 0.9
        seq.append(0.1 if k in ("services", "tech", "limited") else 0.9)
    seq.extend([0.9, 0.9, 0.9])  # vowel removal, swap, final cap

    def fake_random():
        return seq.pop(0)

    # random.choice should return specific replacements in the order encountered
    choices = ["sirvices", "teck", "limtied"]
    def fake_choice(variants):
        return choices.pop(0)

    monkeypatch.setattr(generator.random, "random", fake_random)
    monkeypatch.setattr(generator.random, "choice", fake_choice)

    out = generator.dirty_name("Tech Services Limited")
    assert out == "Teck sirvices limtied"


def test_dirty_name_vowel_removal(monkeypatch):
    # Ensure no phonetic replacements, but vowel removal happens
    seq = [0.9] * 12  # phonetic checks -> no replacements
    seq.append(0.1)   # vowel removal -> yes
    seq.append(0.9)   # small swap -> no
    seq.append(0.9)   # final capitalization path -> n.capitalize()

    def fake_random():
        return seq.pop(0)

    monkeypatch.setattr(generator.random, "random", fake_random)

    out = generator.dirty_name("Alpha")
    assert out == "Lph"
