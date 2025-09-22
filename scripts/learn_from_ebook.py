from ebooklib import epub
from bs4 import BeautifulSoup

def extract_text_from_epub(path):
    book = epub.read_epub(path)
    text = []

    for item in book.get_items():
        if item.get_type() == epub.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), "html.parser")
            text.append(soup.get_text())

    return "\n".join(text)