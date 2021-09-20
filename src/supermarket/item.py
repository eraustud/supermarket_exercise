# TODO: imports
import sqlite3
from .database import Database
import logging

class Item:
    def __init__(self, sku, name, price):
        self.log = logging.getLogger('Item_' + name)
        self.sku = sku
        self.name = name
        self.price = price

    # creates a product record in the database for this object if the SKU does not already exist
    def create_product(self):
        with Database() as db:
            try:
                item_args = (self.sku, self.name, self.price)
                db.execute('INSERT INTO products(SKU, name, price) VALUES (?, ?, ?)', item_args)  # safe insertion of variables
            except sqlite3.Error as err:
                self.log.error('Error occurred attempting to write a new product to the database: %s' % str(err))

    # returns an Item instance with the data from the SKU record in the database
    @staticmethod
    def read_product(sku):
        item = None
        with Database() as db:
            try:
                db.execute('SELECT * FROM products WHERE SKU=(?)', (sku,))
                result = db.fetchone()
                item = Item(result[1], result[2], result[3])
            except sqlite3.Error as err:
                logging.getLogger('Item').error('Error occurred attempting to read product %s from the database: %s' % (sku, str(err)))
        return item

    # updates the product record in the database for this SKU
    def update_product(self):
        raise NotImplementedError

    @staticmethod
    def delete_product(sku):
        raise NotImplementedError

    @staticmethod
    def get_skus():
        skus = []
        with Database() as db:
            try:
                db.execute('SELECT DISTINCT SKU FROM products')
                skus = db.fetchall()
            except sqlite3.Error as err:
                logging.getLogger('Item').error('Error occurred attempting to fetch product SKUs: %s' % str(err))
        return [sku[0] for sku in skus]

