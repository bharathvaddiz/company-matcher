from .matching import match
from .generator import generate_realistic_names, dirty_name

if __name__ == "__main__":
    companies = generate_realistic_names(5)
    dirties = [dirty_name(x) for x in companies]

    for real,bad in zip(companies, dirties):
        r=match(bad)
        print(real, "=>", bad, "=>", r)
