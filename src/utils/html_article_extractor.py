from bs4 import BeautifulSoup
import requests


def extract_article(url: str) -> tuple[str, str]:
    soup = BeautifulSoup(requests.get(url).content, features="html.parser")
    title = soup.title.string
    for script in soup(["script", "style"]):
        script.extract()
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = tuple(
        chunk
        for line in lines
        for phrase in line.split("  ")
        if (chunk := phrase.strip())
    )
    return title, "\n".join(chunks)
