import requests
from bs4 import BeautifulSoup

# URL сторінки для скрейпінгу
url = "https://example.com"

# Виконуємо запит до веб-сторінки
response = requests.get(url)

# Перевіряємо, чи успішний запит
if response.status_code == 200:
    # Парсимо HTML-код сторінки
    soup = BeautifulSoup(response.content, "html.parser")

    # Збираємо всі посилання
    links = soup.find_all("a", href=True)

    # Фільтруємо зовнішні та внутрішні посилання
    external_links = [link['href'] for link in links if link['href'].startswith('http')]
    internal_links = [link['href'] for link in links if not link['href'].startswith('http')]

    print("Зовнішні посилання:", external_links)
    print("Внутрішні посилання:", internal_links)
else:
    print(f"Не вдалося отримати сторінку. Статус код: {response.status_code}")
