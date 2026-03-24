import requests
from bs4 import BeautifulSoup

def scrape_amazon(product_name):
    try:
        query = product_name.replace(" ", "+")
        url = f"https://www.amazon.in/s?k={query}"

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        product = soup.select_one("div[data-component-type='s-search-result']")
        if not product:
            return None

        title = product.select_one("h2 span")
        price = product.select_one(".a-price-whole")
        link = product.select_one("h2 a")

        if title and price and link:
            return {
                "website": "Amazon",
                "title": title.text.strip(),
                "price": float(price.text.strip().replace(",", "").replace(".", "")),
                "link": "https://www.amazon.in" + link["href"]
            }
    except:
        return None