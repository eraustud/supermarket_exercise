import unittest
import logging
from src.supermarket import *
from test_helpers import *

class TestPricingCategory(unittest.TestCase):
    def setup(self):
        self.log = logging.getLogger('TestPricingCategory')

        # implement dummy database
        self.db_path = 'example.db'
        database.Database.database_path = self.db_path
        init_empty_database(self.db_path)
        populate_products(self.db_path)


    def teardown(self):
        kill_database(self.db_path)

    def test_constructor(self):
        pc = pricing_category.PricingCategory()
        self.assertNotEqual(pc, None)

    def test_get_subtotal(self):
        pc = pricing_category.PricingCategory()
        try:
            pc.get_subtotal({})
        except NotImplementedError:
            pass # abstract method

class TestSimplePricingCategory(TestPricingCategory):
    def test_constructor(self):
        pc = pricing_category.Simple()
        self.assertNotEqual(pc, None)
    
    def test_get_subtotal(self):
        self.setup()
        pc = pricing_category.Simple()
        item_skus = Item.get_skus()
        checkout_items = {}
        correct_total = 0  # comparison point for subtotal
        for sku in item_skus:
            item_obj = Item.read_product(sku)
            correct_total += item_obj.price
            checkout_items[sku] = 1
        
        subtotal = pc.get_subtotal(checkout_items)
        self.assertEqual(subtotal, correct_total)
        self.teardown()

class TestBuyXGetYFreePricingCategory(TestPricingCategory):
    def test_constructor(self):
        sku = '1983'
        buy_x = 2
        get_y = 1
        name = 'buy2get1toothbrush'
        pc = pricing_category.BuyXGetYFree(sku, buy_x, get_y, name)
        self.assertEqual(pc.sku, sku)
        self.assertEqual(pc.x, int(buy_x))
        self.assertEqual(pc.y, int(get_y))
        self.assertEqual(pc.name, name)

    def test_get_subtotal(self):
        self.setup()

        pc = pricing_category.BuyXGetYFree('1983', 2, 1, 'buy2get1toothbrush')
        checkout_items = {'1983': 5}
        subtotal = pc.get_subtotal(checkout_items)
        self.assertEqual(subtotal, -199)  # two free items for buying 5 on a buy2get1

        self.teardown()

    def test_read_pricing_category(self):
        self.setup()

        pc = pricing_category.BuyXGetYFree('1983', 2, 1, 'buy2get1toothbrush')
        # insert a pricing category reference to the master table
        with Database() as db:
            try:
                prcrefid_args = (BuyXGetYFree.pc_type_string, pc.name)
                db.execute('INSERT INTO pcrefs(pctype, name) VALUES (?, ?)', prcrefid_args)  # safe insertion of variables
            except sqlite3.Error as err:
                logging.getLogger('BuyXGetYFree').error('Error occurred attempting to get a new BuyXGetYFree pcrefid: %s' % str(err))
        
        # insert a BuyXGetYFree entry to the pc_buyxgety table
        with Database() as db:
            try:
                pcrefid_args = (pc.name, BuyXGetYFree.pc_type_string)
                db.execute('SELECT pcrefid FROM pcrefs WHERE name=(?) AND pctype=(?)', pcrefid_args)  # safe insertion of variables
                pcrefid = db.fetchone()[0]  # fetch the pcrefid from the pcref entry we just created
                buyxgetyfree_args = (pc.x, pc.y, pc.sku, pcrefid, pc.name)
                db.execute('INSERT INTO pc_buyxgety(x, y, sku, pcrefid, name) VALUES (?, ?, ?, ?, ?)', buyxgetyfree_args)  # safe insertion of variables
            except sqlite3.Error as err:
                logging.getLogger('BuyXGetYFree').error('Error occurred attempting to insert new BuyXGetYFree entry into the database: %s' % str(err))

        pc_record = pricing_category.BuyXGetYFree.read_pricing_category(pcrefid)
        self.assertEqual(pc_record.sku, pc.sku)
        self.assertEqual(pc_record.x, pc.x)
        self.assertEqual(pc_record.y, pc.y)
        self.assertEqual(pc_record.name, pc.name)

        self.teardown()

    def test_create_pricing_category(self):
        self.setup()

        pc = pricing_category.BuyXGetYFree('1983', 2, 1, 'buy2get1toothbrush')
        pc.create_pricing_category()

        result = None
        with Database() as db:
            try:
                pcrefsargs = (pc.name, pricing_category.BuyXGetYFree.pc_type_string)
                db.execute('SELECT pcrefid FROM pcrefs WHERE name=(?) AND pctype=(?)', pcrefsargs)
                pcrefid = db.fetchone()[0]
                
                args = (pcrefid,)
                db.execute('SELECT * FROM pc_buyxgety WHERE pcrefid=(?)', args)  # safe insertion of variables
                record = db.fetchone()  # fetch the pcrefid from the pcref entry we just created # x y sku name 1 2 3 4
                result = BuyXGetYFree(record[1], record[2], record[3], record[4])
            except sqlite3.Error as err:
                logging.getLogger('BuyXGetYFree').error('Error occurred attempting to fetch BuyXGetYFree entry: %s' % str(err))

        self.assertEqual(result.sku, pc.sku)
        self.assertEqual(result.x, pc.x)
        self.assertEqual(result.y, pc.y)
        self.assertEqual(result.name, pc.name)

        self.teardown()

class TestAdditionalTaxesPricingCategory(TestPricingCategory):
    def test_constructor(self):
        pc = pricing_category.AdditionalTaxes('0923', 9.25, 'wine')
        self.assertNotEqual(pc, None)
        self.assertEqual(pc.sku, '0923')
        self.assertEqual(pc.tax_rate_percent, 9.25)
        self.assertEqual(pc.name, 'wine')

    def test_get_subtotal(self):
        self.setup()

        pc = pricing_category.AdditionalTaxes('0923', 9.25, 'wine')
        checkout_items = {'0923': 3}
        subtotal = pc.get_subtotal(checkout_items)
        correct_subtotal = 1549 * .0925 * 3
        self.assertEqual(subtotal, correct_subtotal)

        self.teardown()

    def test_read_pricing_category(self):
        self.setup()

        pc = pricing_category.AdditionalTaxes('0923', 9.25, 'wine')
        # insert a pricing category reference to the master table
        with database.Database() as db:
            try:
                prcrefid_args = (AdditionalTaxes.pc_type_string, pc.name)
                db.execute('INSERT INTO pcrefs(pctype, name) VALUES (?, ?)', prcrefid_args)  # safe insertion of variables
            except sqlite3.Error as err:
                logging.getLogger('AdditionalTaxes').error('Error occurred attempting to get a new AdditionalTaxes pcrefid: %s' % str(err))
        
        # insert an AdditionalTaxes entry to the pc_taxes table
        pcrefid = None
        with database.Database() as db:
            try:
                pcrefid_args = (pc.name, AdditionalTaxes.pc_type_string)
                db.execute('SELECT pcrefid FROM pcrefs WHERE name=(?) AND pctype=(?)', pcrefid_args)  # safe insertion of variables
                pcrefid = db.fetchone()[0]  # fetch the pcrefid from the pcref entry we just created
                additionaltaxesargs = (pc.sku, pc.tax_rate_percent, pc.name, pcrefid)
                db.execute('INSERT INTO pc_taxes(sku, tax_rate, name, pcrefid) VALUES (?, ?, ?, ?)', additionaltaxesargs)  # safe insertion of variables
            except sqlite3.Error as err:
                logging.getLogger('AdditionalTaxes').error('Error occurred attempting to insert new AdditionalTaxes entry into the database: %s' % str(err))

        pc_record = pricing_category.AdditionalTaxes.read_pricing_category(pcrefid)
        self.assertEqual(pc_record.sku, pc.sku)
        self.assertEqual(pc_record.tax_rate_percent, pc.tax_rate_percent)
        self.assertEqual(pc_record.name, pc.name)

        self.teardown()

    def test_create_pricing_category(self):
        self.setup()

        pc = pricing_category.AdditionalTaxes('0923', 9.25, 'wine')
        pc.create_pricing_category()

        result = None
        with Database() as db:
            try:
                pcrefsargs = (pc.name, pricing_category.AdditionalTaxes.pc_type_string)
                db.execute('SELECT pcrefid FROM pcrefs WHERE name=(?) AND pctype=(?)', pcrefsargs)
                pcrefid = db.fetchone()[0]
                
                args = (pcrefid,)
                db.execute('SELECT * FROM pc_taxes WHERE pcrefid=(?)', args)  # safe insertion of variables
                record = db.fetchone()  # fetch the pcrefid from the pcref entry we just created # x y sku name 1 2 3 4
                result = AdditionalTaxes(record[1], record[2], record[3])
            except sqlite3.Error as err:
                logging.getLogger('AdditionalTaxes').error('Error occurred attempting to fetch AdditionalTaxes entry: %s' % str(err))

        self.assertEqual(result.sku, pc.sku)
        self.assertEqual(result.tax_rate_percent, pc.tax_rate_percent)
        self.assertEqual(result.name, pc.name)

        self.teardown()



class TestBundledPricingCategory(TestPricingCategory):
    def test_constructor(self):
        pc = pricing_category.Bundled(499, ['6732', '4900'], 'chips_and_salsa')  # chips & salsa for 4.99
        self.assertNotEqual(pc, None)
        self.assertEqual(pc.price, 499)
        # this assert also tests that the item list hasn't been rearranged, which doesn't matter, but doesn't hurt, either
        self.assertEqual(pc.skus, ['6732', '4900'])
        self.assertEqual(pc.name, 'chips_and_salsa')

    def test_get_subtotal(self):
        self.setup()

        pc = pricing_category.Bundled(499, ['6732', '4900'], 'chips_and_salsa')  # chips & salsa for 4.99
        checkout_items = {  '6732': 3,
                            '4900': 2
        }
        subtotal = pc.get_subtotal(checkout_items)
        correct_subtotal = (499 - 249 - 349) * 2  # discount for two bundles
        self.assertEqual(subtotal, correct_subtotal)

    def test_read_pricing_category(self):
        self.setup()

        pc = pricing_category.Bundled(499, ['6732', '4900'], 'chips_and_salsa')  # chips & salsa for 4.99
        # insert a pricing category reference to the master table
        with database.Database() as db:
            try:
                prcrefid_args = (Bundled.pc_type_string, pc.name)
                db.execute('INSERT INTO pcrefs(pctype, name) VALUES (?, ?)', prcrefid_args)  # safe insertion of variables
            except sqlite3.Error as err:
                logging.getLogger('Bundled').error('Error occurred attempting to get a new Bundled pcrefid: %s' % str(err))
        
        # insert a Bundled entry to the pc_taxes table
        pcrefid = None
        with database.Database() as db:
            try:
                pcrefid_args = (pc.name, Bundled.pc_type_string)
                db.execute('SELECT pcrefid FROM pcrefs WHERE name=(?) AND pctype=(?)', pcrefid_args)  # safe insertion of variables
                pcrefid = db.fetchone()[0]  # fetch the pcrefid from the pcref entry we just created
                bundledargs = (pc.price, ','.join(pc.skus), pc.name, pcrefid)
                db.execute('INSERT INTO pc_bundled(price, skus, name, pcrefid) VALUES (?, ?, ?, ?)', bundledargs)  # safe insertion of variables
            except sqlite3.Error as err:
                logging.getLogger('Bundled').error('Error occurred attempting to insert new Bundled entry into the database: %s' % str(err))

        pc_record = pricing_category.Bundled.read_pricing_category(pcrefid)
        self.assertEqual(pc_record.price, pc.price)
        self.assertEqual(pc_record.skus, pc.skus)
        self.assertEqual(pc_record.name, pc.name)

        self.teardown()

    def test_create_pricing_category(self):
        self.setup()

        pc = pricing_category.Bundled(499, ['6732', '4900'], 'chips_and_salsa')  # chips & salsa for 4.99
        pc.create_pricing_category()

        result = None
        with Database() as db:
            try:
                pcrefsargs = (pc.name, pricing_category.Bundled.pc_type_string)
                db.execute('SELECT pcrefid FROM pcrefs WHERE name=(?) AND pctype=(?)', pcrefsargs)
                pcrefid = db.fetchone()[0]
                
                args = (pcrefid,)
                db.execute('SELECT * FROM pc_bundled WHERE pcrefid=(?)', args)  # safe insertion of variables
                record = db.fetchone()  # fetch the pcrefid from the pcref entry we just created # x y sku name 1 2 3 4
                result = Bundled(record[1],  record[2].split(','), record[3])
            except sqlite3.Error as err:
                logging.getLogger('Bundled').error('Error occurred attempting to fetch Bundled entry: %s' % str(err))

        self.assertEqual(result.price, pc.price)
        self.assertEqual(result.skus, pc.skus)
        self.assertEqual(result.name, pc.name)

        self.teardown()

if __name__ == "__main__":
    unittest.main()