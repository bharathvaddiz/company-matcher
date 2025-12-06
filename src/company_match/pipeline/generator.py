from faker import Faker
import random

fake = Faker()

# mapping of realistic Indian spelling variants
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
    return [fake.company() for _ in range(n)]


def dirty_name(name):
    n = name.lower()

    # replace words as per Indian pronunciation patterns
    for word, variants in phonetic_variations.items():
        if word in n and random.random() < 0.5:
            n = n.replace(word, random.choice(variants))

    # vowel removal sometimes
    if random.random() < 0.2:
        n = "".join(ch for ch in n if ch not in "aeiou")

    # small letter swap
    if random.random() < 0.2 and len(n) > 4:
        i = random.randint(0, len(n)-2)
        n = list(n)
        n[i], n[i+1] = n[i+1], n[i]
        n = "".join(n)

    # remove punctuation
    n = n.replace("&", "").replace(".", "")

    # lower/upper
    if random.random() < 0.3:
        return n.lower().capitalize()
    return n.capitalize()
