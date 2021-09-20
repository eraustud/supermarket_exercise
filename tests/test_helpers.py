# helper methods for unit and integration testing

import sqlite3
import os
import logging
from src.supermarket.item import Item
from src.supermarket.database import Database
from src.supermarket.pricing_category import *
from src.supermarket.scheme import Scheme

def kill_database(database_path):
    if (os.path.isfile(database_path)):
        os.remove(database_path)

def init_empty_database(database_path):
    kill_database(database_path)
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    cursor.execute('CREATE TABLE products (Id INTEGER PRIMARY KEY, SKU TEXT UNIQUE, name TEXT, price INTEGER)')
    cursor.execute('CREATE TABLE schemes (Id INTEGER PRIMARY KEY, name TEXT UNIQUE, pcrefids TEXT)')
    cursor.execute('CREATE TABLE pcrefs (pcrefid INTEGER PRIMARY KEY, pctype TEXT, name TEXT)')
    cursor.execute('CREATE TABLE pc_buyxgety (Id INTEGER PRIMARY KEY, sku  TEXT, x INTEGER, y INTEGER, name TEXT, pcrefid INTEGER UNIQUE)')
    cursor.execute('CREATE TABLE pc_taxes (Id INTEGER PRIMARY KEY, sku TEXT, tax_rate REAL, name TEXT, pcrefid INTEGER UNIQUE)')
    cursor.execute('CREATE TABLE pc_bundled (Id INTEGER PRIMARY KEY, price INTEGER, skus TEXT, name TEXT, pcrefid INTEGER UNIQUE)')
    connection.commit()
    connection.close()

def populate_products(database_path):
    Database.database_path = database_path
    toothbrush = Item('1983', 'toothbrush', 199)
    toothbrush.create_product()
    salsa = Item('4900', 'salsa', 349)
    salsa.create_product()
    milk = Item('8873', 'milk', 249)
    milk.create_product()
    chips = Item('6732', 'chips', 249)
    chips.create_product()
    wine = Item('0923', 'wine', 1549)
    wine.create_product()

def populate_pricing_categories(database_path):
    Database.database_path = database_path
    buy2get1_toothbrush = BuyXGetYFree('1983', 2, 1, 'buy2get1toothbrush')
    buy2get1_toothbrush.create_pricing_category()
    wine_additional_taxes = AdditionalTaxes('0923', 9.25, 'wine')
    wine_additional_taxes.create_pricing_category()
    bundled_chips_and_salsa = Bundled(499, ['6732', '4900'], 'chips_and_salsa')
    bundled_chips_and_salsa.create_pricing_category()

# assignment assumes populate_pricing_categories was run first
def populate_schemes(database_path):
    Database.database_path = database_path
    default_scheme = Scheme('default')
    for i in range(1,4): 
        default_scheme.pricing_category_refids.append(i) 
    default_scheme.create_scheme()