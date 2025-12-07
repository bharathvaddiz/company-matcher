"""
Elasticsearch client helper used by the matching pipeline.

This module contains a small convenience wrapper around the Elasticsearch HTTP
API (via requests). It builds a multi_match query against several company name
fields and returns the raw list of hit documents produced by ES.

Note: This file intentionally does not change behavior or error handling —
only comments and documentation are added for clarity.
"""

# Use requests for simple HTTP communication with Elasticsearch.
import requests

# Application configuration: ES endpoint for the company index search.
from .config import ES_URL

def search_es(query, top_n=10):
    """
    Search the configured Elasticsearch index for company names similar to `query`.

    Args:
        query (str): The free-text company name or phrase to search for.
        top_n (int): Maximum number of hits to request from ES (size).

    Returns:
        list: The list of Elasticsearch hit objects (as returned under hits.hits).
              Each hit is a dict that typically contains '_source', '_score', etc.
    """
    # Build the Elasticsearch multi_match query body:
    # - size: limit number of results returned
    # - multi_match: search across multiple fields with fuzziness
    #   Fields:
    #     - company_name: primary exact/name field
    #     - company_name.normalized: normalized form for canonical matching
    #     - company_name.autocomplete: n-gram/autocomplete field for prefix matches
    #   fuzziness: "AUTO" lets ES determine an appropriate edit distance
    body = {
        "size": top_n,
        "query": {
            "multi_match": {
                "query": query,
                "fields": [
                    "company_name",
                    "company_name.normalized",
                    "company_name.autocomplete"
                ],
                "fuzziness": "AUTO"
            }
        }
    }

    # Issue the POST request to the ES _search endpoint and parse JSON
    resp = requests.post(ES_URL, json=body)

    # The ES response contains hits under the path: {"hits": {"hits": [...]}}
    # Return an empty list if the expected structure is missing to avoid None.
    return resp.json().get("hits", {}).get("hits", [])
