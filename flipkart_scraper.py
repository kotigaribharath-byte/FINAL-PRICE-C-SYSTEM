from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

def scrape_flipkart(product_name):
    driver = None
    try:
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("user-agent=Mozilla/5.0")

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

        query = product_name.replace(" ", "%20")
        url = f"https://www.flipkart.com/search?q={query}"
        driver.get(url)
        time.sleep(4)

        titles = driver.find_elements(By.CSS_SELECTOR, "div.KzDlHZ")
        prices = driver.find_elements(By.CSS_SELECTOR, "div.Nx9bqj")
        links = driver.find_elements(By.CSS_SELECTOR, "a.CGtC98")

        if titles and prices and links:
            title = titles[0].text.strip()
            price = prices[0].text.strip().replace("₹", "").replace(",", "")
            link = links[0].get_attribute("href")

            return {
                "website": "Flipkart",
                "title": title,
                "price": float(price),
                "link": link
            }

        return None

    except Exception as e:
        print("Flipkart scraper error:", e)
        return None

    finally:
        if driver:
            driver.quit()