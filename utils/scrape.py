import requests
from bs4 import BeautifulSoup
import pandas as pd
import pycountry
import numpy as np
import re


class IndicatorScraper:
    def __init__(self):
        self.url = "https://www.ceicdata.com/en/countries"
        self.base_url = "https://www.ceicdata.com"
        self.data = pd.DataFrame(columns=['name', 'code', 'url'])

    def scrape_for_country_urls(self):
        page = requests.get(self.url)
        soup = BeautifulSoup(page.content, "html.parser")
        country_lists = soup.find_all("div", class_="countries-list")
        for i in country_lists:
            for j in i.find_all("a", class_="country-link"):
                # print(j.string, j.get('href'))
                try:
                    code = pycountry.countries.get(name=j.string).alpha_2
                    self.data = self.data.append({'name': j.string,
                                                  'code': code,
                                                  'url': j.get('href')}, ignore_index=True)
                except AttributeError:
                    pass
        self.get_attributes("nominal-gdp")
        print(self.data)

    def get_attributes(self, attribute_name):
        if attribute_name not in self.data.columns:
            self.data[attribute_name] = np.nan
        for index, row in self.data.iterrows():
            self.scrape_for_attributes(row['code'], attribute_name)

    def scrape_for_attributes(self, country_code, attribute_name):
        print(country_code)
        country_row = self.data[self.data['code'] == country_code]
        url = country_row.iloc[0]['url']
        print(url)
        page = requests.get(self.base_url + url)
        soup = BeautifulSoup(page.content, "html.parser")
        try:
            indicator_url = soup.find_all('a', href=re.compile(r"/" + attribute_name + "$"))[0].get('href')
            indicator_page = requests.get(self.base_url + indicator_url)
            indicator_soup = BeautifulSoup(indicator_page.content, "html.parser")
            value = indicator_soup.find('table', class_="dp-table dp-table-auto").find('td').text.split('\n')[3].replace(
                ",", "")
            self.data.loc[self.data['code'] == country_code, attribute_name] = float(value)

        except IndexError:
            return
        except AttributeError:
            return

if __name__ == '__main__':
    scraper = IndicatorScraper()
    scraper.scrape_for_country_urls()
