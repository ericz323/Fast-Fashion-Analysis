import os
import re
import csv
import time
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

user_name = "user_name"
chrome_user_data_path = f"C:\\Users\\{user_name}\\AppData\\Local\\Google\\Chrome\\User Data\\Default"
chrome_exe_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"

BASE_DIR = Path(__file__).resolve().parent

# Webpage URLs
# H&M and Shein blocked my scraper, so I downloaded their website HTML files
targets = [
    {
        "brand": "Zara",
        "item_type": "Tops",
        "url": "https://www.zara.com/us/en/woman-tops-l1322.html?v1=2419940&regionGroupId=41",
        "selector": 'span.money-amount__main'
    },
    {
        "brand": "Zara",
        "item_type": "Tops",
        "url": "https://www.zara.com/us/en/woman-tshirts-l1362.html?v1=2420417&regionGroupId=41",
        "selector": 'span.money-amount__main'
    },
    {
        "brand": "Zara",
        "item_type": "Tops",
        "url": "https://www.zara.com/us/en/woman-shirts-l1217.html?v1=2420369&regionGroupId=41",
        "selector": 'span.money-amount__main'
    },
    {
        "brand": "Zara",
        "item_type": "Dresses",
        "url": "https://www.zara.com/us/en/woman-dresses-l1066.html?v1=2420896&regionGroupId=41",
        "selector": 'span.money-amount__main'
    },
    {
        "brand": "Zara",
        "item_type": "Pants & Jeans",
        "url": "https://www.zara.com/us/en/woman-jeans-l1119.html?v1=2419185&regionGroupId=41",
        "selector": 'span.money-amount__main'
    },
    {
        "brand": "Zara",
        "item_type": "Pants & Jeans",
        "url": "https://www.zara.com/us/en/woman-trousers-l1335.html?v1=2420795&regionGroupId=41",
        "selector": "span.money-amount__main"
    },
    {
        "brand": "Zara",
        "item_type": "Coats & Jackets",
        "url": "https://www.zara.com/us/en/woman-outerwear-l1184.html?v1=2664773&regionGroupId=41",
        "selector": 'span.money-amount__main'
    },
    {
        "brand": "Gap",
        "item_type": "Tops",
        "url": "https://www.gap.com/browse/women/t-shirts-and-tanks?cid=17076&nav=meganav%3AWomen%3ACategories%3AT-Shirts+%26+Tanks#pageId=0&department=136",
        "selector": 'span.fds__core-web-price-small'
    },
    {
        "brand": "Gap",
        "item_type": "Tops",
        "url": "https://www.gap.com/browse/women/shirts-and-tops?cid=34608&nav=meganav%3AWomen%3ACategories%3AShirts+%26+Tops#pageId=0&department=136",
        "selector": 'span.fds__core-web-price-small'
    },
    {
        "brand": "Gap",
        "item_type": "Dresses",
        "url": "https://www.gap.com/browse/women/dresses?cid=13658&nav=meganav%3AWomen%3ACategories%3ADresses#pageId=0&department=136",
        "selector": 'span.fds__core-web-price-small'
    },
    {
        "brand": "Gap",
        "item_type": "Pants & Jeans",
        "url": "https://www.gap.com/browse/women/jeans?cid=5664&nav=meganav%3AWomen%3ACategories%3AJeans#pageId=0&department=136",
        "selector": 'span.fds__core-web-price-small'
    },
    {
        "brand": "Gap",
        "item_type": "Pants & Jeans",
        "url": "https://www.gap.com/browse/women/pants?cid=1011761&nav=meganav%3AWomen%3ACategories%3APants#pageId=0&department=136",
        "selector": "span.fds__core-web-price-small"
    },
    {
        "brand": "Gap",
        "item_type": "Coats & Jackets",
        "url": "https://www.gap.com/browse/women/outerwear-and-jackets?cid=5736&nav=meganav%3AWomen%3ACategories%3ACoats+%26+Jackets#pageId=0&department=136",
        "selector": 'span.fds__core-web-price-small'
    },
    {
        "brand": "H&M",
        "item_type": "Tops",
        "url": (BASE_DIR / "data" / "Women's%20Blouses%20&%20Shirts%20_%20Denim,%20Satin%20&%20Linen%20_%20H&M%20US.html"),
        "selector": 'span[translate="no"]'
    },
    {
        "brand": "H&M",
        "item_type": "Tops",
        "url": (BASE_DIR / "data" / "Women's%20Tops%20_%20Corsets%20Crops%20Bodysuits%20&%20T-Shirts%20_%20H&M%20US.html").as_uri(),
        "selector": 'span[translate="no"]'
    },
    {
        "brand": "H&M",
        "item_type": "Dresses",
        "url": (BASE_DIR / "data" / "Dresses%20_%20Fall%20Dresses,%20Plaid,%20Satin%20Slip%20&%20Velvet%20Styles%20_%20H&M%20US.html").as_uri(),
        "selector": 'span[translate="no"]'
    },
    {
        "brand": "H&M",
        "item_type": "Pants & Jeans",
        "url": (BASE_DIR / "data" / "Women's%20Jeans%20_%20Skinny,%20Boyfriend%20&%20Wide%20Leg%20Styles%20_%20H&M%20US.html").as_uri(),
        "selector": 'span[translate="no"]'
    },
    {
        "brand": "H&M",
        "item_type": "Pants & Jeans",
        "url": (BASE_DIR / "data" / "Women's%20Pants%20&%20Leggings%20_%20Cargo,%20Linen%20&%20Wide-Leg%20_%20H&M%20US.html").as_uri(),
        "selector": 'span[translate="no"]'
    },
    {
        "brand": "H&M",
        "item_type": "Coats & Jackets",
        "url": (BASE_DIR / "data" / "Women's%20Coats%20&%20Jackets%20_%20Leather%20Trench%20&%20Winter%20_%20H&M%20US.html").as_uri(),
        "selector": 'span[translate="no"]'
    },
    {
        "brand": "Shein",
        "item_type": "Tops",
        "url": (BASE_DIR / "data" / "T-Shirts%20&%20Tees%20_%20Women's%20Tops%20_%20SHEIN%20USA.html").as_uri(),
        "selector": 'span.normal-price-ctn__sale-price'
    },
    {
        "brand": "Shein",
        "item_type": "Tops",
        "url": (BASE_DIR / "data" / "Women's%20Blouses,%20Shirts%20_%20Dressy%20Tops%20_%20SHEIN%20USA.html").as_uri(),
        "selector": 'span.normal-price-ctn__sale-price'
    },
    {
        "brand": "Shein",
        "item_type": "Tops",
        "url": (BASE_DIR / "data" / "Women's%20Tank%20Tops%20&%20Camis%20_%20Summer%20Tops%20_%20SHEIN%20USA.html").as_uri(),
        "selector": 'span.normal-price-ctn__sale-price'
    },
    {
        "brand": "Shein",
        "item_type": "Tops",
        "url": (BASE_DIR / "data" / "Women's%20Tops%20&%20Blouses%20_%20Tees%20&%20Skirts%20_%20SHEIN%20USA.html").as_uri(),
        "selector": 'span.normal-price-ctn__sale-price'
    },
    {
        "brand": "Shein",
        "item_type": "Dresses",
        "url": (BASE_DIR / "data" / "Women%20Dresses%20_%20Fashion%20Women%20Dresses%20_%20SHEIN%20USA.html").as_uri(),
        "selector": 'span.normal-price-ctn__sale-price'
    },
    {
        "brand": "Shein",
        "item_type": "Pants & Jeans",
        "url": (BASE_DIR / "data" / "Women's%20Denim%20Shop%20_%20Trendy%20Jeans,%20Dresses,%20Tops%20_%20SHEIN%20USA.html").as_uri(),
        "selector": 'span.normal-price-ctn__sale-price'
    },
    {
        "brand": "Shein",
        "item_type": "Pants & Jeans",
        "url": (BASE_DIR / "data" / "Women's%20Pants%20_%20Dress%20Pants%20for%20Women%20_%20SHEIN%20USA.html").as_uri(),
        "selector": "span.normal-price-ctn__sale-price"
    },
    {
        "brand": "Shein",
        "item_type": "Coats & Jackets",
        "url": (BASE_DIR / "data" / "Women's%20Coats%20&%20Jackets%20_%20Warm%20Outerwear%20_%20SHEIN%20USA.html").as_uri(),
        "selector": 'span.normal-price-ctn__sale-price'
    },
]

csv_filename = "fast_fashion_prices_item.csv"
with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Brand", "Item Type", "Price"])


def scrape_brand_prices(brand_name, item_type, url, price_selector, page):
    print(f"\n--- Starting {brand_name} ({item_type}) ---")

    try:
        page.goto(url, timeout=60000)
        page.mouse.wheel(0, 2000)
        time.sleep(3)
        html = page.content()

    except Exception as e:
        print(f"Error loading {brand_name}: {e}")
        return

    soup = BeautifulSoup(html, 'html.parser')
    price_elements = soup.select(price_selector)
    saved_count = 0

    with open(csv_filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        for element in price_elements:
            raw_text = element.get_text()
            match = re.search(r'(\d+\.\d{2})', raw_text)
            if match:
                price_val = float(match.group(1))
                # Now we write the brand, the type, and the price to the CSV
                writer.writerow([brand_name, item_type, price_val])
                saved_count += 1

    if saved_count > 0:
        print(f"Success! Saved {saved_count} {item_type} prices for {brand_name}.")
    else:
        print(f"Warning: Could not find any valid prices.")


if __name__ == "__main__":
    print(f"Initializing persistent Chrome session...")
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=chrome_user_data_path,
            executable_path=chrome_exe_path,
            headless=False,
            viewport={'width': 1920, 'height': 1080}
        )
        page = browser.pages[0]

        for target in targets:
            scrape_brand_prices(target["brand"], target["item_type"], target["url"], target["selector"], page)

        print("\nAll done! Data saved to fast_fashion_prices_item.csv")
        browser.close()