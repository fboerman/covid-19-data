#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup

baseurl = "https://www.saude.gov.br/noticias/agencia-saude?limitstart="

for i in range(10+1):
    print("base page {}".format(i))
    r = requests.get(baseurl + str(i*10))
    base_soup = BeautifulSoup(r.text, 'lxml')

    links = [h2.find("a")["href"] for h2 in base_soup.find_all('h2', class_="tileHeadline")]
    print("found {} item links".format(len(links)))
    for x, url in enumerate(links):
        print("trying item link {}".format(x))
        url = "https://www.saude.gov.br/" + url
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'lxml')
        if len(soup.find_all('table')) > 0:
            print(url)