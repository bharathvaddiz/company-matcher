"""
Configuration values for the company matching pipeline.

- ES_URL: endpoint used to query the Elasticsearch company index.
- THRESHOLD_ACCEPT: lower similarity threshold used to consider a candidate match acceptable.
- THRESHOLD_HIGH: higher similarity threshold indicating a strong/high-confidence match.
"""

# Elasticsearch search endpoint for the company index.
# Keep the index and path format as expected by the code that performs searches.
ES_URL = "http://localhost:9200/company_index/_search"

# Matching thresholds:
# - THRESHOLD_ACCEPT: when a candidate score is above this, it may be accepted.
# - THRESHOLD_HIGH: when a candidate score is above this, it is considered a high-confidence match.
THRESHOLD_ACCEPT = 0.55
THRESHOLD_HIGH = 0.75
