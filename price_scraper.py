# # Price scraper

import sys
import os
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import csv
from datetime import datetime
from redmail import EmailSender

import plotly.express as px



# ## Constants

# where to save results
PRICES_FILE = './data/df_prices.csv'
IMAGE_FILE = './data/prices.jpg'

# which browser are we using
headers = {
    "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36 OPR/67.0.3575.137"}

# ### Urls for extraction

# add item urls for price scraping
item_urls = [
    # busilica
    'https://www.gama-alati.rs/elektro-pneumatski-cekic-bosch-gbh-2-28-f-sds-plus-0611267600.html',
    'https://www.gama-alati.rs/elektro-pneumatski-cekic-bosch-gbh-2-28-f-sds-plus-l-boxx-izmenljiva-glava-0611267601.html',
    'https://www.prodavnicaalata.rs/proizvodi/elektro-pneumatski-cekic-bosch-gbh-2-28-f-880w/',
    'https://www.prodavnicaalata.rs/proizvodi/elektro-pneumatski-cekic-bosch-gbh-2-28-f-880w-l-boxx/',
    'https://www.okov.rs/sr/alati/elektricni-alat-i-pribor/busilice-odvijaci-i-elektropneumatski-cekici/gbh-2-28-f-el-pneumatski-cekic-sds-880w',
    # detektor
    'https://www.gama-alati.rs/bosch-d-tect-120-detektor-struje-kablova-pod-naponom-u-l-boxx-koferu-1x2-0ah-0601081301.html',
    'https://www.prodavnicaalata.rs/proizvodi/detektor-struje-bosch-d-tect-120-120mm/',
    'https://www.prodavnicaalata.rs/proizvodi/detektor-struje-bosch-d-tect-120-1x15ah-u-l-boxx-u/',
    'https://www.prodavnicaalata.rs/proizvodi/detektor-struje-bosch-d-tect-120-solo-bez-baterija-i-punjaca-u-l-boxx-u/',
    'https://www.okov.rs/sr/alati/laseri/laseri-i-oprema-za-njih/d-tect-120-detektor-12v-li-ion-20ah',
    # brusilica
    'https://www.gama-alati.rs/bosch-gws-1400-ugaona-brusilica-1400w-125mm-0601824800.html',
    'https://www.prodavnicaalata.rs/proizvodi/ugaona-brusilica-bosch-gws-1400-1400w-125-mm/',
    'https://www.okov.rs/sr/alati/elektricni-alat-i-pribor/brusilice/gws-1400-ugaona-brusilica-125mm-1400w-bosch',
]


# ## Extraction functions

def gama_extractor(url):
    """Returns item name, price, old price and item code from www.gama-alati.rs url"""
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    # item info (price, old price, item code)
    product_info = soup.find("div", attrs={"class":"product-top-part"})
    
    # item name
    item_name = product_info.find("span", attrs={"class": "base"}).text
    # item price
    item_price = float(product_info.find('span', attrs={'data-price-type':"finalPrice"})['data-price-amount'])
    # old price
    if product_info.find('span', attrs={'data-price-type':"oldPrice"}):
        item_old_price = float(product_info.find('span', attrs={'data-price-type':"oldPrice"})['data-price-amount'])
    else: item_old_price = np.NaN
    # article_code
    item_code = product_info.find("div", attrs={"class":"product attribute sku"}).text.strip().split()[1]
    
    return (item_name, item_price, item_old_price, item_code)
    
    
# gama_extractor('https://www.gama-alati.rs/metabo-khe-2860-quick-sds-plus-elektro-pneumatska-busilica-600878510.html')


def prodavnica_alata_extractor(url):
    """Returns item name, price, old price and item code from www.prodavnicaalata.rs url"""
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    # item info (price, old price, item code)
    product_info = soup.find("div", attrs={"class":"product__content"})
    # product_info
    # item name
    item_name = product_info.find('h1', attrs={'class':'product__name'}).string
    # item price
    if product_info.find('div', attrs={'class':'product__prices'}).find('span', attrs={'class':'product-sale-price'}):
        item_price = product_info.find('div', attrs={'class':'product__prices'}).find('span', attrs={'class':'product-sale-price'}).text.strip().replace('.','').split()[0]
    else:
        item_price = product_info.find('div', attrs={'class':'product__prices'}).text.strip().replace('.','').split()[0]
    item_price = float(item_price)
    # old price
    if product_info.find('div', attrs={'class':'product__prices'}).find('del'):
        item_old_price = float(product_info.find('div', attrs={'class':'product__prices'}).find('del').text.replace('.','').split()[-2])
    else: item_old_price = np.NaN
    # article_code
    item_code = product_info.find('ul', attrs={'class':'product__meta'},).text.strip().split()[-1]
    
    return (item_name, item_price, item_old_price, item_code)

# prodavnica_alata_extractor('https://www.prodavnicaalata.rs/proizvodi/elektro-pneumatski-cekic-bosch-gbh-2-28-f-880w/')


def okov_extractor(url):
    """Returns item name, price, old price and item code from www.okov.rs url"""
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    # item info (price, old price, item code)
    product_info = soup.find("div", attrs={"class":"product-content"})
    # product_info
    # item name
    item_name = (product_info.find('h1', attrs={'class':'product-content-title'}).text                                 )
    # item price
    item_price = product_info.find('div', attrs={'class':'regular_price'}).text.strip().replace('.','').split()[0]
    item_price = float(item_price)
    # old price
    if product_info.find('div', attrs={'class':'old_price'}):
        item_old_price = float(product_info.find('div', attrs={'class':'old_price'}).text.replace('.','').split()[0])
    else: item_old_price = np.NaN
    # article_code
    item_code = product_info.find('div', attrs={'class':'product_code'},).text.strip()
    
    return (item_name, item_price, item_old_price, item_code)

# okov_extractor('https://www.okov.rs/sr/alati/elektricni-alat-i-pribor/busilice-odvijaci-i-elektropneumatski-cekici/gbh-2-28-f-el-pneumatski-cekic-sds-880w')
# okov_extractor('https://www.okov.rs/sr/tehnika/mali-kucni-aparati-za-pripremu-hrane/aparati-i-mlinovi-za-kafu/aparat-za-kafu-1340-1600w-infinissina-cosmic-d-gusto-krups')


# domain: (item_name, item_price, item_old_price)
extractor_functions = {'www.gama-alati.rs': gama_extractor,
                       'www.prodavnicaalata.rs': prodavnica_alata_extractor,
                       'www.okov.rs': okov_extractor,
                      }


# ## Scraping algorithm

# where to save results
if os.path.isfile(PRICES_FILE):
    df_prices = pd.read_csv(PRICES_FILE)
else: # if there is no file, create new empty one
    df_prices = pd.DataFrame()


# timestamp of price sampling
current_time = datetime.isoformat(datetime.now())
# save results from current price sampling (all items)
df_results = pd.DataFrame()

print(f"{datetime.now()} Ekstrakcija cijena zapoceta!")

# extract price for all urls in list
for item_url in item_urls:
    item_seller = urlparse(item_url).netloc
    try:
        item_name, item_price, item_old_price, item_code = \
            extractor_functions[item_seller](item_url)
    except Exception as e:
        print(f'Greska u izvlacenju cijene za url: {item_url}')
        print(e)
        item_name, item_price, item_old_price, item_code = \
        'Invalid', np.NaN, np.NaN, 'Invalid'
#     print('\n'+'*'*80)
#     print(f"Extracting data from: {item_url}")
#     print(f"Item name: {item_name}")
#     print(f"Item price: {item_price}")
#     print(f"Item old_price: {item_old_price}")
#     print(f"Item code: {item_code}")
    df_result = pd.DataFrame([dict(zip(['Time', 'Item', 'Price', 'Old price', 'Item code', 'Seller', 'URL'],
                 [current_time, item_name, item_price, item_old_price, item_code, item_seller, item_url]))]
            )
    df_results = df_results.append(df_result, ignore_index=True)

# add all results to historical data
df_prices = df_prices.append(df_results, ignore_index=True)
# save scraped data to csv file
df_prices.to_csv(PRICES_FILE, index=False)

print(f"{datetime.now()} Ekstrakcija cijena zavrsena!")

df_prices = pd.read_csv(PRICES_FILE)

# df_prices

prices_fig = (px.line(df_prices,
                      x='Time', 
                      y='Price', 
                      color='Item', 
                      hover_data=df_prices.columns, 
                      title='Historical item prices',
                     )
                .update_layout({'legend_orientation':'h'})
            )
prices_fig.write_html('./data/prices.html')

# save figure for sending
prices_fig.write_image(IMAGE_FILE, )

# prices_fig
print(f"{datetime.now()} Slika sa izvjestajem zavrsena!")

# ## Sending e-mail with results

# df_prices contains all data, while df_results contains only current price

# check if we extracted all prices (and if not send notification)
# any(df_results['Price'].isna())

####### EMAIL FIELDS ########
sender = os.environ['MAIL_USERNAME']
password = os.environ['MAIL_PASSWORD']
receiver = os.environ['MAIL_RECEIVER']
subject=f"Cijena izabranih artikala - {datetime.date(datetime.now())}"
body = f"Istorijske vrijednosti cijena za {datetime.now()}\n"
body += f"Uspjesno izvuceno {df_results['Price'].notna().sum()}/{df_results.shape[0]} cijena\n\n"
html = df_results[['Seller', 'Item', 'Price', 'Old price', 'URL']].to_markdown(tablefmt="html")
# save results for sending message to messenger
df_results[['Seller', 'Item', 'Price', 'Old price', 'URL']].to_markdown(buf='data/results.html' , tablefmt="html", )
filename = IMAGE_FILE

# yag = yagmail.SMTP(os.environ['MAIL_USERNAME'], 
#                      password=os.environ['MAIL_PASSWORD'],
# )
# yag.send(
#     to=receiver,
#     subject=subject,
#     contents=[body, html], 
#     attachments=filename,
# )

email = EmailSender(host="smtp.mail.yahoo.com", port=587, use_starttls=True, user_name=sender, password=password)

email.send(
    subject=subject,
    sender=sender,
    receivers=[receiver],
    text=body,
    html=html,
    attachments=filename,
)

print(f"{datetime.now()} Mejl poslat!")
