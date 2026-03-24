import requests
from bs4 import BeautifulSoup

def scrape_croma(product_name):
    try:
        query = product_name.replace(" ", "+")
        url = f"https://www.croma.com/searchB?q={query}:relevance"

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.select_one("h3.product-title")
        price = soup.select_one("span.amount")
        link = soup.select_one("a.product-item")

        if title and price and link:
            return {
                "website": "Croma",
                "title": title.text.strip(),
                "price": float(price.text.strip().replace("₹", "").replace(",", "")),
                "link": "https://www.croma.com" + link["href"]
            }

        return None
    except:
        return None