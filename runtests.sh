#! /usr/bin/env bash
export PYTHONPATH=:`pwd`

python3 tests/item_test.py
python3 tests/pricing_category_test.py
python3 tests/scheme_test.py
python3 tests/checkout_test.py