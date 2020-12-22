import requests
from glob import glob
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from time import sleep

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
    "Accept-Language": "en-US, en;q=0.5",
}


def search_product_list(interval_count=1, interval_hours=6):

    prod_tracker = pd.read_csv(
        "C:/Users/jf_ro/Desktop/Proyectos/Web Scraping/Test_Amazon/trackers/TRACKER_PRODUCTS.csv",
        sep=";",
    )
    prod_tracker_URLS = prod_tracker.url
    tracker_log = pd.DataFrame()
    now = datetime.now().strftime("%Y-%m-%d %Hh%Mm")
    interval = 0

    while interval < interval_count:

        for x, url in enumerate(prod_tracker_URLS):
            page = requests.get(url, headers=HEADERS)
            soup = BeautifulSoup(page.content, features="lxml")

            # Titulo del producto

            title = soup.find(id="productTitle").get_text().strip()

            # Precio. Prevenimos un crash por si no hay precio

            try:
                price = float(
                    soup.find(id="priceblock_ourprice")
                    .get_text()
                    .replace("$", "")
                    .replace(",", "")
                    .strip()
                )
            except:
                price = ""
            # Review Score y Count

            try:
                review_score = float(
                    soup.select(".a-icon.a-star-5")[0]
                    .get_text()
                    .split(" ")[0]
                    .replace(",", ".")
                )
                review_count = int(
                    soup.select("#acrCustomerReviewText")[0]
                    .get_text()
                    .split(" ")[0]
                    .replace(".", "")
                )
            except:
                try:
                    review_score = float(
                        soup.select(".a-icon.a-star-5")[1]
                        .get_text()
                        .split(" ")[0]
                        .replace(",", ".")
                    )
                    review_count = int(
                        soup.select("#acrCustomerReviewText")[0]
                        .get_text()
                        .split(" ")[0]
                        .replace(".", "")
                    )
                except:
                    review_score = ""
                    review_count = ""

            # Chequear disponibilidad
            try:
                soup.select("#availability .a-color-state")[0].get_text().strip()
                stock = "Out of Stock"
            except:
                # checking if there is "Out of stock" on a second possible position
                try:
                    soup.select("#availability .a-color-price")[0].get_text().strip()
                    stock = "Out of Stock"
                except:
                    # if there is any error in the previous try statements, it means the product is available
                    stock = "Available"

            log = pd.DataFrame(
                {
                    "date": now.replace("h", ":").replace("m", ""),
                    "code": prod_tracker.code[x],
                    "url": url,
                    "title": title,
                    "buy_below": prod_tracker.buy_below[x],
                    "price": price,
                    "stock": stock,
                    "review_score": review_score,
                    "review_count": review_count,
                },
                index=[x],
            )

            try:

                if price < prod_tracker.buy_below[x]:
                    print(
                        "************************ ALERT! Buy the "
                        + prod_tracker.code[x]
                        + " ************************"
                    )
            except:
                pass

            tracker_log = tracker_log.append(log)
            print("appended" + prod_tracker.code[x] + "\n" + title + "\n\n")
            # print(tracker_log)
            sleep(5)

        interval += 1

        sleep(interval_hours * 1 * 1)
        print("end of interval" + str(interval))

    last_search = glob(
        "C:/Users/jf_ro/Desktop/Proyectos/Web Scraping/Test_Amazon/search_history/SEARCH_HISTORY.xlsx"
    )[-1]
    search_hist = pd.read_excel(last_search, engine="openpyxl")
    final_df = search_hist.append(tracker_log, sort=False)
    # print(final_df)
    final_df.to_excel(
        "C:/Users/jf_ro/Desktop/Proyectos/Web Scraping/Test_Amazon/search_history/SEARCH_HISTORY_{}.xlsx".format(
            now
        ),
        index=False,
    )
    print("end of search")


search_product_list()