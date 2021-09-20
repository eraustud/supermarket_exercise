import sqlite3
import logging
from .database import Database
from .item import Item

class PricingCategory:
    def __init__(self):
        pass
    
    # abstract method
    def get_subtotal(self, checkout_items):
        raise NotImplementedError 

# Simple is a special case in that there is no need to permanently store a Simple object.
#  simple prices are stored in the products table.
class Simple(PricingCategory):
    def __init__(self):
        PricingCategory.__init__(self)

    def get_subtotal(self, checkout_items):
        subtotal = 0.0 # price in cents (but Real)
        for sku in checkout_items.keys():
            checkout_item = Item.read_product(sku)
            subtotal += checkout_item.price * checkout_items[sku] # multiply price by quantity
        return subtotal

class BuyXGetYFree(PricingCategory):
    pc_type_string = 'buyxgetyfree'
    def __init__(self, sku, x, y, name):
        self.x = int(x)
        self.y = int(y)
        self.sku = sku
        self.name = name
        PricingCategory.__init__(self)

    def get_subtotal(self, checkout_items):
        subtotal = 0.0
        quantity = checkout_items.get(self.sku)
        if quantity is None:
            return subtotal
        else:
            progress = 0
            free = 0
            discount = 0
            for i in range(quantity):
                if progress < self.x and free < self.y:
                    progress += 1
                elif progress == self.x and free < self.y:
                    free += 1
                    discount += 1
                elif progress == self.x and free == self.y:
                    progress = 0
                    free = 0

            item = Item.read_product(self.sku)
            subtotal -= item.price * discount
            return subtotal

    def create_pricing_category(self):
        # insert a pricing category reference to the master table
        with Database() as db:
            try:
                prcrefid_args = (BuyXGetYFree.pc_type_string, self.name)
                db.execute('INSERT INTO pcrefs(pctype, name) VALUES (?, ?)', prcrefid_args)  # safe insertion of variables
            except sqlite3.Error as err:
                logging.getLogger('BuyXGetYFree').error('Error occurred attempting to get a new BuyXGetYFree pcrefid: %s' % str(err))
        
        # insert a BuyXGetYFree entry to the pc_buyxgety table
        with Database() as db:
            try:
                pcrefid_args = (self.name, BuyXGetYFree.pc_type_string)
                db.execute('SELECT pcrefid FROM pcrefs WHERE name=(?) AND pctype=(?)', pcrefid_args)  # safe insertion of variables
                pcrefid = db.fetchone()[0]  # fetch the pcrefid from the pcref entry we just created
                buyxgetyfree_args = (self.x, self.y, self.sku, pcrefid, self.name)
                db.execute('INSERT INTO pc_buyxgety(x, y, sku, pcrefid, name) VALUES (?, ?, ?, ?, ?)', buyxgetyfree_args)  # safe insertion of variables
            except sqlite3.Error as err:
                logging.getLogger('BuyXGetYFree').error('Error occurred attempting to insert new BuyXGetYFree entry into the database: %s' % str(err))

    def read_pricing_category(pcrefid):
        result = None
        with Database() as db:
            try:
                args = (pcrefid,)
                db.execute('SELECT * FROM pc_buyxgety WHERE pcrefid=(?)', args)  # safe insertion of variables
                record = db.fetchone()  # fetch the pcrefid from the pcref entry we just created # x y sku name 1 2 3 4
                result = BuyXGetYFree(record[1], record[2], record[3], record[4])
            except sqlite3.Error as err:
                logging.getLogger('BuyXGetYFree').error('Error occurred attempting to fetch BuyXGetYFree entry: %s' % str(err))
        return result

class AdditionalTaxes(PricingCategory):
    pc_type_string = 'additionaltaxes'
    def __init__(self, sku, tax_rate_percent, name):
        self.sku = sku
        self.tax_rate_percent = tax_rate_percent
        self.name = name
        PricingCategory.__init__(self)
    
    def get_subtotal(self, checkout_items):
        subtotal = 0.0
        quantity = checkout_items.get(self.sku)
        if quantity is None:
            return subtotal
        else:
            item = Item.read_product(self.sku)
            subtotal +=  item.price * quantity * (self.tax_rate_percent / 100.0)
            return subtotal

    def create_pricing_category(self):
        # insert a pricing category reference to the master table
        with Database() as db:
            try:
                prcrefid_args = (AdditionalTaxes.pc_type_string, self.name)
                db.execute('INSERT INTO pcrefs(pctype, name) VALUES (?, ?)', prcrefid_args)  # safe insertion of variables
            except sqlite3.Error as err:
                logging.getLogger('AdditionalTaxes').error('Error occurred attempting to get a new AdditionalTaxes pcrefid: %s' % str(err))
        
        # insert an AdditionalTaxes entry to the pc_taxes table
        with Database() as db:
            try:
                pcrefid_args = (self.name, AdditionalTaxes.pc_type_string)
                db.execute('SELECT pcrefid FROM pcrefs WHERE name=(?) AND pctype=(?)', pcrefid_args)  # safe insertion of variables
                pcrefid = db.fetchone()[0]  # fetch the pcrefid from the pcref entry we just created
                additionaltaxesargs = (self.sku, self.tax_rate_percent, self.name, pcrefid)
                db.execute('INSERT INTO pc_taxes(sku, tax_rate, name, pcrefid) VALUES (?, ?, ?, ?)', additionaltaxesargs)  # safe insertion of variables
            except sqlite3.Error as err:
                logging.getLogger('AdditionalTaxes').error('Error occurred attempting to insert new AdditionalTaxes entry into the database: %s' % str(err))

    def read_pricing_category(pcrefid):
        result = None
        with Database() as db:
            try:
                args = (pcrefid,)
                db.execute('SELECT * FROM pc_taxes WHERE pcrefid=(?)', args)  # safe insertion of variables
                record = db.fetchone()  # fetch the pcrefid from the pcref entry we just created # x y sku name 1 2 3 4
                result = AdditionalTaxes(record[1], record[2], record[3])
            except sqlite3.Error as err:
                logging.getLogger('AdditionalTaxes').error('Error occurred attempting to fetch AdditionalTaxes entry: %s' % str(err))
        return result

class Bundled(PricingCategory):
    pc_type_string = 'bundled'
    def __init__(self, price, skus, name):
        self.price = price
        self.skus = skus
        self.name = name
        
    def get_subtotal(self, checkout_items):
        bundle_items = {}
        for sku in self.skus:
            bundle_items[sku] = 0
        for sku in checkout_items.keys():
            if sku in self.skus:
                bundle_items[sku] += checkout_items[sku]
        base_price = sum([Item.read_product(sku).price for sku in self.skus])
        discount = self.price - base_price
        # min will grab the number of complete bundles that exist in the checkout items
        return discount * min(bundle_items.values() if len(bundle_items.values()) else [0]) 

    def create_pricing_category(self):
        # insert a pricing category reference to the master table
        with Database() as db:
            try:
                prcrefid_args = (Bundled.pc_type_string, self.name)
                db.execute('INSERT INTO pcrefs(pctype, name) VALUES (?, ?)', prcrefid_args)  # safe insertion of variables
            except sqlite3.Error as err:
                logging.getLogger('Bundled').error('Error occurred attempting to get a new Bundled pcrefid: %s' % str(err))

        # insert a Bundled entry to the pc_taxes table
        with Database() as db:
            try:
                pcrefid_args = (self.name, Bundled.pc_type_string)
                db.execute('SELECT pcrefid FROM pcrefs WHERE name=(?) AND pctype=(?)', pcrefid_args)  # safe insertion of variables
                pcrefid = db.fetchone()[0]  # fetch the pcrefid from the pcref entry we just created
                bundledargs = (self.price, ','.join(self.skus), self.name, pcrefid)
                db.execute('INSERT INTO pc_bundled(price, skus, name, pcrefid) VALUES (?, ?, ?, ?)', bundledargs)  # safe insertion of variables
            except sqlite3.Error as err:
                logging.getLogger('Bundled').error('Error occurred attempting to insert new Bundled entry into the database: %s' % str(err))

    def read_pricing_category(pcrefid):
        result = None
        with Database() as db:
            try:
                args = (pcrefid,)
                db.execute('SELECT * FROM pc_bundled WHERE pcrefid  =(?)', args)  # safe insertion of variables
                record = db.fetchone()  # fetch the pcrefid from the pcref entry we just created # x y sku name 1 2 3 4
                result = Bundled(record[1],  record[2].split(','), record[3])
            except sqlite3.Error as err:
                logging.getLogger('Bundled').error('Error occurred attempting to fetch Bundled entry: %s' % str(err))
        return result


PRICING_CATEGORY_TYPE_MAP = {
    'buyxgetyfree' : BuyXGetYFree,
    'additionaltaxes' : AdditionalTaxes,
    'bundled' : Bundled
}