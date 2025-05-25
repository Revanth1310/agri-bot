import requests

SERPAPI_KEY = "983858ca65811d41b677aa8e6f0e6a2e24b3fa34ecc4c9e2dff82bf139ab016d"

def fetch_content_from_sites(query):
    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": 5
    }

    domain_filters = [
        "india.gov.in",
        "agriwelfare.gov.in",
        "icar.org.in",
        "manage.gov.in",
        "kisanmandi.com"
    ]

    results = []
    for domain in domain_filters:
        params["q"] = f"{query} site:{domain}"
        r = requests.get("https://serpapi.com/search", params=params)
        data = r.json()
        if "organic_results" in data:
            for res in data["organic_results"]:
                results.append(res.get("snippet", ""))

    combined = "\n".join(results)
    return combined[:1500]  # Trim to fit prompt length
