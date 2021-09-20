import sqlite3
import logging
from .scheme import Scheme
from .database import Database

class Checkout:
    def __init__(self, scheme):
        self.scheme = scheme
        self.items = {}

    def scan(self, sku):
        with Database() as db:
            try: 
                db.execute('SELECT Id FROM products WHERE SKU=(?)', (sku,))
                record = db.fetchall()
                if len(record) == 0:
                    raise ValueError('Requested product SKU %s does not match any products in the database' % sku)
            except sqlite3.Error as err:
                logging.getLogger('Checkout').error('Error occurred attempting to fetch product Id: %s' % str(err))
        try:
            self.items[sku] += 1
        except KeyError:
            self.items[sku] = 1

    # Apply scheme to all items and sum up total cost
    def getTotal(self):
        return self.scheme.get_total(self.items)