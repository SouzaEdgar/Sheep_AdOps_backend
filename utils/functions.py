import re
from urllib.parse import urlparse, parse_qs

# ===== Principais ===== #
def valid_url(url):
    regex = re.compile(r"^(https?://)([\w.-]+)(\.[a-zA-Z]{2,})(:[0-9]+)?(/.*)?$")
    return bool(regex.match(url))

def parameters_search(url, parameters: list):
    parsed = urlparse(url)
    queries = parse_qs(parsed.query)
    found = []

    for param in parameters:
        if param in queries:
            for val in queries[param]:
                found.append((param, val))
    return found


