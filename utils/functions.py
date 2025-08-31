import re

# ===== Principais ===== #
def valid_url(url):
    regex = re.compile(r"^(https?://)([\w.-]+)(\.[a-zA-Z]{2,})(:[0-9]+)?(/.*)?$")
    return bool(regex.match(url))

def parameters_search(url, parameters: list):
    found_params = []
    for x in parameters:
        match = re.findall(rf"(?:[?&])([^=&#]*{re.escape(x)}[^=&#]*)=([^&#]*)", url)
        found_params.extend(match)
    return found_params

