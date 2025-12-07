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
    # random.random is only called for tokens that appear in the name, then
    # for vowel removal, swap, and final capitalization. For
    # 'Tech Services Limited' the phonetic checks will be performed in the
    # order the dict is iterated but only when the substring is present. We
    # therefore provide the sequence of random values corresponding to the
    # three phonetic checks (services, tech, limited) followed by the
    # vowel/swap/cap checks.
    seq = [0.1, 0.1, 0.1, 0.9, 0.9, 0.9]  # 3 replacements, then no vowel removal/swap, final cap -> capitalize()

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
    # Ensure no phonetic replacements (none of the phonetic tokens in 'Alpha'),
    # but vowel removal happens. Only three random checks will be performed:
    # vowel removal, small swap, and final capitalization.
    seq = [0.1, 0.9, 0.9]  # vowel removal -> yes, then no swap, final capitalization path

    def fake_random():
        return seq.pop(0)

    monkeypatch.setattr(generator.random, "random", fake_random)

    out = generator.dirty_name("Alpha")
    assert out == "Lph"
