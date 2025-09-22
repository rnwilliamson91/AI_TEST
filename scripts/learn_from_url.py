import requests
from bs4 import BeautifulSoup

def extract_text_from_url(url):
    print(f"🌐 Fetching URL: {url}")

    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return ""

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove non-content elements
    for tag in soup(["script", "style", "noscript", "iframe", "svg"]):
        tag.decompose()

    # Extract visible text
    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    result = "\n".join(lines[:100])  # Limit to first 100 lines for safety

    print(f"📄 Extracted {len(result)} characters of text.")
    return result