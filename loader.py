#!/usr/bin/env python

import requests
import logging
import json
import pandas as pd
import re
import os
from time import gmtime, strftime

import sys
sys.path.append('./python-sdk/lib')
from meli import Meli

from dotenv import load_dotenv


class DataLoader:
    """
    Loader class to search and format Mercado Libre's data.
    """
    states = [
        {
            "id":"TUxBUENPU2ExMmFkMw",
            "name":"Bs.As. Costa Atlántica"
        },
        {
            "id":"TUxBUEdSQWU4ZDkz",
            "name":"Bs.As. G.B.A. Norte"
        },
        {
            "id":"TUxBUEdSQWVmNTVm",
            "name":"Bs.As. G.B.A. Oeste"
        },
        {
            "id":"TUxBUEdSQXJlMDNm",
            "name":"Bs.As. G.B.A. Sur"
        },
        {
            "id":"TUxBUFpPTmFpbnRl",
            "name":"Buenos Aires Interior"
        },
        {
            "id":"TUxBUENBUGw3M2E1",
            "name":"Capital Federal"
        }
    ]
    search_url = 'http://api.mercadolibre.com/sites/MLA/search'
    access_token = None
    result_limit = 50
    columns = ['id', 'title', 'category_id', 'catalog_product_id', 'price', 'currency_id', 'condition', 'permalink', 'brand', 'model', 'year']
    items = []

    def __init__(self, page_limit = None, file_name = 'data.csv'):
        self.file_name = file_name
        self.page_limit = page_limit

    def get_access_token(self):
        raise NotImplementedError

    def get_category_id(self, category_name):
        """
        Returns the category id based on the category name.
        If there is no category with the given name, returns None.
        """
        # More info in: https://developers.mercadolibre.com.ar/es_ar/categorias-y-atributos

        jsdata = requests.get("https://api.mercadolibre.com/sites/MLA/categories").json()
        category_data = next((item for item in jsdata if item['name'] == category_name), None)
        
        return category_data['id'] if category_data is not None else None

    def search(self, category_name):
        """
        Request category data, perform a search and process pages to obtain items.
        """
        self.category_id = self.get_category_id(category_name)

        for state in self.states:
            # Get the number of pages in the search
            print("-" * 83)
            print(f"Buscando: {category_name} en {state['name']}")

            search_params = {
                'category': self.category_id,
                'state': state["id"],
            }

            if self.access_token is not None:
                search_params['access_token'] = self.access_token

            response = requests.get(
                self.search_url,
                params = search_params
            )

            page_count = 1 + round(response.json()['paging']['total'] / self.result_limit)
            
            logging.info(f"URL: {response.request.url}")

            if self.page_limit is None:
                self.page_limit = page_count
            else:
                self.page_limit = min(self.page_limit, page_count)

            # Perform a search requesting every page
            for page in range(0, self.page_limit):
                print(f"Página {page + 1} de {self.page_limit}")

                search_params = {
                    'category': self.category_id,
                    'state': state["id"],
                    'limit': self.result_limit,
                    'offset': str(page*self.result_limit),
                }

                if self.access_token is not None:
                    search_params['access_token'] = self.access_token

                jsdata = requests.get(
                    self.search_url,
                    params = search_params
                ).json()

                try:
                    self.items += jsdata['results']
                except KeyError:
                    logging.error(f"Error agregando items desde {response.request.url}")
                    logging.debug(f'{jsdata}')

        self.serialize()

    def serialize(self):
        data = pd.DataFrame(self.items)
        
        # Remove duplicates
        data = data.groupby(['id']).first().reset_index()

        print("-" * 83)
        for i in range(0, data.shape[0]):
            if i % 100 == 0:
                print(f"Procesando {i + 1:05} de {data.shape[0]:05} -- {data.loc[i, 'title']}")

            try:
                dataAttr = pd.DataFrame(data.loc[i, 'attributes'])

                brandAttr = dataAttr.loc[dataAttr['id']=='BRAND']
                modelAttr = dataAttr.loc[dataAttr['id']=='MODEL']
                yearAttr = dataAttr.loc[dataAttr['id']=='VEHICLE_YEAR']
            
                data.loc[i, 'brand'] = brandAttr['value_name'].item() if brandAttr['value_name'].count() > 0 else ''
                data.loc[i, 'model'] = modelAttr['value_name'].item() if modelAttr['value_name'].count() > 0 else ''
                data.loc[i, 'year'] = yearAttr['value_name'].item() if yearAttr['value_name'].count() > 0 else ''

            except KeyError as e:
                logging.debug(f"Error adaptando item {i + 1:05} ({data.loc[i, 'id']}) -- no existe key {e} en 'attributes'.")
                pass

        data = data.fillna('')
        self.items = data[self.columns]

    def export(self):
        # Make directory if it doesn't exist yet
        try:
            os.makedirs('data')
        except FileExistsError:
            logging.debug("'data' directory already exists.")

        with open(os.path.join('data', strftime("%Y_%m_%d", gmtime()) + '_' + self.file_name), "w+", encoding='utf-8') as file:
            print("-" * 83)
            print(f"Guardando datos en {self.file_name}")
            self.items.to_csv(file, sep=",", decimal=".")


if __name__ == '__main__':
    # logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

    load_dotenv()
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    if client_id is not None and client_secret is not None:
        meli = Meli(client_id=client_id, client_secret=client_secret)

    loader = DataLoader()
    loader.search("Autos, Motos y Otros")
    loader.export()

    # print(loader.items)