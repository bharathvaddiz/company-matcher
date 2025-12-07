"""
Command-line entry point for the company matching demo.

This module generates a small list of realistic company names, produces
"dirty" (noisy/altered) variants of those names, then attempts to match
each dirty name back to a canonical company name using the match function.

Intended for quick demonstration and manual testing.
"""

# Import the matching function and the data/name helpers from the package.
from .matching import match
from .generator import generate_realistic_names, dirty_name

if __name__ == "__main__":
    # Generate a few realistic company names (default: 5 here).
    companies = generate_realistic_names(50)

    # Create a corresponding list of "dirty" names (noisy variants) from the real names.
    dirties = [dirty_name(x) for x in companies]

    # For each real name and its dirty variant, try to match the dirty name back
    # to a canonical name and print the result in a readable form.
    for real, bad in zip(companies, dirties):
        r = match(bad)  # attempt to find the best match for the dirty name
        print(real, "=>", bad, "=>", r)