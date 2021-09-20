import unittest
from src.supermarket import *
from test_helpers import *
import sqlite3


class TestItem(unittest.TestCase):
    def setup(self):
        self.database_path = 'example.db'
        init_empty_database(self.database_path)
        database.Database.database_path = self.database_path

    def teardown(self):
        kill_database(self.database_path)

    def test_constructor(self):
        test_item = item.Item('1983', 'toothbrush', 199)
        self.assertNotEqual(test_item, None)

    def test_create_product(self):
        self.setup()

        toothbrush = item.Item('1983', 'toothbrush', 199)
        toothbrush.create_product()  # save to database

        # fetch from database directly (don't contaminate this test with the read_product method)
        connection = sqlite3.connect(self.database_path)
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM products WHERE SKU=(?)', ('1983',))
        result = cursor.fetchall()
        connection.commit()
        connection.close()

        # make sure the created product has the expected properties
        self.assertEqual(len(result), 1)
        record = result[0]
        self.assertEqual(record[1], toothbrush.sku)
        self.assertEqual(record[2], toothbrush.name)
        self.assertEqual(record[3], toothbrush.price)

        self.teardown()


    def test_read_product(self):
        self.setup()

        # create database record directly (don't contaminate this test with the create_product method)
        connection = sqlite3.connect(self.database_path)
        cursor = connection.cursor()
        sku = '1983'
        item_args = (sku, 'toothbrush', 199)
        cursor.execute('INSERT INTO products(SKU, name, price) VALUES(?, ?, ?)', item_args)
        connection.commit()
        connection.close()

        # check that the product record read has the expected properties
        toothbrush = item.Item.read_product(sku)
        self.assertEqual(toothbrush.sku, sku)
        self.assertEqual(toothbrush.name, 'toothbrush')
        self.assertEqual(toothbrush.price, 199)

        self.teardown()

if __name__ == "__main__":
    unittest.main()