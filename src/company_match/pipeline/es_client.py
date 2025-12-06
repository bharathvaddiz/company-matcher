import requests
from .config import ES_URL

def search_es(query, top_n=10):
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
    resp = requests.post(ES_URL, json=body)
    return resp.json().get("hits", {}).get("hits", [])
