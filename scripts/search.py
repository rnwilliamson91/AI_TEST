import requests
from bs4 import BeautifulSoup

def search_web(query):
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.text, "html.parser")
    snippets = []

    for g in soup.find_all('div', class_='BNeawe s3v9rd AP7Wnd'):
        text = g.get_text()
        if text and text not in snippets:
            snippets.append(text)
        if len(snippets) >= 3:
            break

    return "\n".join(snippets)