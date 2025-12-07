"""
Helpers to generate realistic company names and produce noisy/"dirty" variants.

This module is intended for creating demo/test inputs for the matching pipeline.
It exposes:
- generate_realistic_names(n): produce n plausible company-like names using Faker.
- dirty_name(name): apply a sequence of small, randomized transformations to
  simulate common human errors, OCR mistakes, shorthand, and phonetic/spelling
  variants often observed in real-world company name inputs.

All modifications are intentionally lightweight and randomized so the output
remains varied while still resembling the original company name.
"""

# Use Faker to create plausible company-like names for demonstrations and tests.
# Faker is intentionally instantiated without a locale here; callers can set a
# seed if deterministic outputs are required for tests.
from faker import Faker
import random

# Initialize a Faker instance (kept global to reuse Faker's internal state).
fake = Faker()

# Mapping of common phonetic/spelling variants observed in business names.
# These entries reflect frequent misspellings or pronunciation-driven variants
# (for example, 'services' -> 'sirvices' or 'servies'), useful to simulate how
# users or data capture systems might alter canonical tokens.
# The mapping keys are canonical tokens; values are plausible noisy variants.
phonetic_variations = {
    "services": ["sirvices", "servies", "sarvices"],
    "solutions": ["solutons", "soltions"],
    "industries": ["industres", "industris", "industrys"],
    "consulting": ["consalting", "consultng", "consltng"],
    "global": ["globel", "globaly"],
    "tech": ["teck", "tek", "techn"],
    "technology": ["technolgy", "tecnology", "technlogy"],
    "company": ["compny", "compani"],
    "limited": ["limtied", "limeted", "limitid"],
    "software": ["softwere", "softwar"],
    "systems": ["systms", "sistem"],
    "corporation": ["corpration", "corporatn", "corporaton"]
}


def generate_realistic_names(n=10):
    """
    Generate a list of realistic-looking company names.

    Args:
        n (int): Number of names to generate (default 10).

    Returns:
        list[str]: A list of generated company name strings from Faker.
    """
    # Use Faker.company() repeatedly to construct sample company names.
    return [fake.company() for _ in range(n)]


def dirty_name(name):
    """
    Produce a noisy/dirty variant of a company name.

    The function applies several randomized transformations that together mimic
    common real-world input noise:
      - lowercasing to simplify substring matching and replacements
      - probabilistic substitution of tokens using phonetic_variations
      - occasional vowel removal to simulate shorthand or OCR losses
      - occasional adjacent-character swap to simulate typing transpositions
      - removal of common punctuation like '&' and '.'
      - randomized capitalization to keep outputs human-like

    The random choices preserve the original unpredictability of the generator.
    """
    # Start from a lowercase representation to make token matching simpler.
    n = name.lower()

    # Iterate known canonical tokens and possibly replace them with a noisy variant.
    # We apply replacements with ~50% probability per token to diversify outputs.
    for word, variants in phonetic_variations.items():
        if word in n and random.random() < 0.5:
            # Choose one variant at random and replace all occurrences of the token.
            n = n.replace(word, random.choice(variants))

    # Occasionally remove vowels to simulate aggressive shorthand or OCR errors.
    # This keeps a consonant skeleton which matching algorithms may still recognize.
    if random.random() < 0.2:
        # Build a new string excluding vowels.
        n = "".join(ch for ch in n if ch not in "aeiou")

    # Simulate a common human typing error: swapping two adjacent characters.
    # Only attempt when the string is sufficiently long to avoid short-string issues.
    if random.random() < 0.2 and len(n) > 4:
        # Pick an index and swap characters at i and i+1.
        i = random.randint(0, len(n) - 2)
        n_list = list(n)
        n_list[i], n_list[i + 1] = n_list[i + 1], n_list[i]
        n = "".join(n_list)

    # Strip a couple of common punctuation/connectors that might be omitted in input.
    # This models user-entered variations where '&' or '.' are often left out.
    n = n.replace("&", "").replace(".", "")

    # Randomize the final capitalization to keep results human-readable.
    # With ~30% probability return capitalized-first-letter; otherwise return title-like.
    if random.random() < 0.3:
        return n.lower().capitalize()
    return n.capitalize()
