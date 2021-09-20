import unittest
from src.supermarket import *
from test_helpers import *
import sqlite3

class TestScheme(unittest.TestCase):
    def setup(self):
        # create dummy empty database with products table for testing
        self.database_path = 'example.db'
        init_empty_database(self.database_path)
        database.Database.database_path = self.database_path

    def teardown(self):
        kill_database(self.database_path)

    def test_constructor(self):
        test_scheme = scheme.Scheme('default', [1, 2, 3])
        self.assertEqual(test_scheme.name, 'default')
        self.assertEqual(test_scheme.pricing_category_refids, [1, 2, 3])

    def test_read_scheme(self):
        self.setup()
        populate_pricing_categories(self.database_path)
        
        test_scheme = scheme.Scheme('default', [1, 2, 3])
        with database.Database() as db:
            try:
                scheme_args = (test_scheme.name, ','.join([str(id) for id in test_scheme.pricing_category_refids]))
                db.execute('INSERT INTO schemes(name, pcrefids) VALUES(?, ?)', scheme_args)
            except sqlite3.Error as err:
                logging.getLogger('TestScheme').error('Error occurred attempting to write a new Scheme to the database: %s' % str(err))
        scheme_result = scheme.Scheme.read_scheme(test_scheme.name)
        
        self.assertEqual(test_scheme.name, scheme_result.name)
        self.assertEqual(test_scheme.pricing_category_refids, scheme_result.pricing_category_refids)

        self.teardown()

    def test_create_scheme(self):
        self.setup()
        populate_pricing_categories(self.database_path)

        test_scheme = scheme.Scheme('default', [1, 2, 3])
        test_scheme.create_scheme()
        scheme_result = None
        with database.Database() as db:
            try:
                scheme_args = (test_scheme.name,)
                db.execute('SELECT * FROM schemes WHERE name=(?)', scheme_args)
                record = db.fetchone()
                scheme_result = scheme.Scheme(record[1], [int(id) for id in record[2].split(',')])
            except sqlite3.Error as err:
                logging.getLogger('TestScheme').error('Error occurred attempting to fetch Scheme from the database: %s' % str(err))
        
        self.assertEqual(test_scheme.name, scheme_result.name)
        self.assertEqual(test_scheme.pricing_category_refids, scheme_result.pricing_category_refids)

        self.teardown()

    def test_get_total(self):
        self.setup()
        populate_products(self.database_path)
        populate_pricing_categories(self.database_path)
        populate_schemes(self.database_path)

        checkout_items = {
            '1983' : 4,
            '4900' : 1,
            '8873' : 1,
            '6732' : 1,
            '0923' : 1,
        }
        test_scheme = scheme.Scheme.read_scheme('default')
        total = test_scheme.get_total(checkout_items)
        self.assertEqual(total, 3037)

if __name__ == "__main__":
    unittest.main()