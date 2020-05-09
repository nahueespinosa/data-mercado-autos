#!/usr/bin/env python

import os
import math
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.axes


class DataAnalizer:
    """
    Analizer class to generate various graphs and reports from Mercado Libre's data.
    """
    def __init__(self, file_name):
        print(f"Abriendo: {file_name}")

        with open(file_name, encoding='utf-8') as file:
            self.autos_df = pd.read_csv(file)
            self.autos_df = self.autos_df.drop(['catalog_product_id', 'category_id'], axis=1)
            self.autos_df = self.autos_df.loc[
                (self.autos_df['currency_id'] == 'ARS') & 
                (self.autos_df['condition'] == 'used') &
                (self.autos_df['year'] > 2014)
            ]

    def graph_top_sales(self, limit=10):
        """
        Grafica ranking de marcas más vendidas
        """
        # Cuenta unidades de cada marca
        brand_count = self.autos_df['brand'].value_counts()[:limit,]

        plt.figure(figsize=(10,5))
        sns.barplot(brand_count.index, brand_count.values, alpha=0.8)
        plt.title(f"Top {limit} de marcas más vendidas")
        plt.ylabel("Número de publicaciones", fontsize=12)
        plt.xlabel("Marca", fontsize=12)
        plt.show()

    def graph_brand_model_prices(self, brands, year, max_cols=2):
        """
        Grafica comparativa de precios de modelos por marca y año
        """
        rows = math.ceil(len(brands) / max_cols)
        cols = 1 if len(brands) == 1 else max_cols

        _, axes = plt.subplots(rows, cols)

        for i, brand in enumerate(brands):
            autos_filtered_df = self.autos_df[
                (self.autos_df['brand'] == brand) &
                (self.autos_df['year'] == year)
            ]

            row = math.floor(i / max_cols)
            col = i % max_cols

            ax = axes[row, col] if rows > 1 else axes[col] if cols > 1 else axes

            sns.barplot(
                x = 'year',
                y = 'price',
                hue = 'model',
                palette = 'hls',
                data = autos_filtered_df,
                capsize = 0.05,
                saturation = 8,
                ax = ax
            )

            ax.set_title(f"Comparativa de modelos {brand} {year}")
            ax.set(xlabel='Año', ylabel='Precio')

        plt.show()

    def graph_model_prices(self, models):
        """
        Grafica análisis de precios de modelos elegidos
        """
        autos_filtered_df = self.autos_df[
            self.autos_df['model'].isin(models)
        ]

        plt.figure(figsize=(10,5))

        sns.barplot(
            x = 'year',
            y = 'price',
            hue = 'model',
            palette = 'hls',
            data = autos_filtered_df,
            capsize = 0.05,
            saturation = 8,
        )

        plt.title("Análisis de precios por modelo")
        plt.ylabel("Precio", fontsize=12)
        plt.xlabel("Año", fontsize=12)
        plt.show()


if __name__ == "__main__":
    file_name = os.path.join('data', '2020_05_06_data.csv')
    analizer = DataAnalizer(file_name)
    # analizer.graph_top_sales()
    analizer.graph_brand_model_prices(['Ford', 'Chevrolet', 'Renault', 'Peugeot'], 2018)
    analizer.graph_model_prices(['Ecosport', 'Onix'])