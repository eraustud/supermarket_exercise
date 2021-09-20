from . import pricing_category as pc
from .database import Database
import sqlite3
import logging

class Scheme:
    def __init__(self, name, pricing_category_refids = []):
        self.name = name
        self.pricing_category_refids = pricing_category_refids
        self.price_adjustments = []
        self.price_adjustments.append(pc.Simple())
        
    def create_scheme(self):
        with Database() as db:
            try:
                scheme_args = (self.name, ','.join([str(id) for id in self.pricing_category_refids]))
                db.execute('INSERT INTO schemes(name, pcrefids) VALUES (?, ?)', scheme_args)  # safe insertion of variables
            except sqlite3.Error as err:
                self.log.error('Error occurred attempting to write a new Scheme to the database: %s' % str(err))
        self.load_pricing_categories()

    @staticmethod
    def read_scheme(name):
        scheme = None
        with Database() as db:
            try:
                db.execute('SELECT * FROM schemes WHERE name=(?)', (name,))
                result = db.fetchone()
                scheme = Scheme(result[1], [int(id) for id in result[2].split(',')])
            except sqlite3.Error as err:
                logging.getLogger('Scheme').error('Error occurred attempting to read Scheme %s from the database: %s' % (name, str(err)))
        if scheme is None:
            raise ValueError("Failed to fetch Scheme of name '%s' from the database" % name)
        scheme.load_pricing_categories()
        return scheme


    def load_pricing_categories(self):
        # load the pricing category objects into the scheme
        for pricing_category_id in self.pricing_category_refids:
            with Database() as db:
                try:
                    db.execute('SELECT pctype FROM pcrefs WHERE pcrefid=(?)', (pricing_category_id,))
                    pc_type = db.fetchone()
                    try:
                        pc_class = pc.PRICING_CATEGORY_TYPE_MAP.get(pc_type[0])
                        pricing_category = pc_class.read_pricing_category(pricing_category_id)
                    except:
                        import pdb
                        pdb.set_trace()
                except sqlite3.Error as err:
                    logging.getLogger('Scheme').error('Error occurred attempting to read pricing category refid: %s from the database: %s'
                     % (pricing_category_id, str(err)))
                if pricing_category.__dict__ not in [pa.__dict__ for pa in self.price_adjustments]:
                    self.price_adjustments.append(pricing_category)

    # apply all pricing schemes to the provided dict of checkout item quantities
    def get_total(self, checkout_items):
        total = 0.0
        for pricing_category in self.price_adjustments:
            total += pricing_category.get_subtotal(checkout_items)
        return int(total)