import unittest
from src.supermarket import *
from test_helpers import *

class TestCheckout(unittest.TestCase):
    def setup(self):
        # create dummy empty database with products table for testing
        self.database_path = 'example.db'
        init_empty_database(self.database_path)
        populate_products(self.database_path)
        populate_pricing_categories(self.database_path)
        populate_schemes(self.database_path)
        database.Database.database_path = self.database_path
        self.s = scheme.Scheme.read_scheme('default')

    def teardown(self):
        kill_database(self.database_path)

    def test_constructor(self):
        self.setup()

        self.c = checkout.Checkout(self.s)
        self.assertNotEqual(self.c, None)

        self.teardown()

    def test_scan(self):
        self.setup()

        self.c = checkout.Checkout(self.s)
        self.c.scan('1983')
        self.assertEqual(self.c.items['1983'], 1)
        self.c.scan('1983')
        self.assertEqual(self.c.items['1983'], 2)

        self.teardown()

    def test_get_total(self):
        self.setup()

        self.c = checkout.Checkout(self.s)
        self.c.scan('1983')  # toothbrush
        self.c.scan('4900')  # salsa
        self.c.scan('8873')  # milk
        self.c.scan('6732')  # chips
        self.c.scan('0923')  # wine
        self.c.scan('1983')  # toothbrush
        self.c.scan('1983')  # toothbrush
        self.c.scan('1983')  # toothbrush
        self.assertEqual(self.c.getTotal(), 3037)

        self.teardown()

if __name__ == "__main__":
    unittest.main()