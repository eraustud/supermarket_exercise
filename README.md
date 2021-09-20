# Supermarket Price Coding Exercise
Sample implementation of a basic supermarket checkout point-of-sale price calculator

## Introduction
This interactive program provides a framework for entering and totaling supermarket items against a given pricing scheme.  
Supermarket Price Coding Exercise (SPCE) was developed with Python 3.7.3 for portability.  
The backing database is built on Sqlite3 for ease of installation and use.
An example database exists in the root directory for exploring the framework from the python console.

## Installation
Ensure both python3 >= 3.7 and python3-pip are installed on your system or use a python virtualenv
pip install the supermarket_exercise directory:  
```bash
    cd supermarket_exercise
    pip3 install .
```

## Use
To test program functionality, open a shell inside the repository's root directory.  
  **NOTE:** You may have to add executable permissions to runtests.sh.
```bash
    ./runtests.sh
```
### Example python console interaction
```python
from supermarket import *
database.Database.database_path = 'supermarket_exercise.db'
todaysScheme = scheme.Scheme.read_scheme('default')
c = checkout.Checkout(todaysScheme)
c.scan('1983')
c.scan('4900')
c.scan('8873')
c.scan('6732')
c.scan('0923')
c.scan('1983')
c.scan('1983')
c.scan('1983')
print(c.getTotal()) # prints 3037
```

## How It Works
- A SPCE Checkout object requires a Scheme object at instantiation.  
- This Scheme object includes information about the day's price adjustments.  
- At checkout, each item scanned is added to the Checkout's "basket".  

- When the Checkout is ready to calculate the total cost of goods, each price adjustment in  
the Scheme (e.g., toothbrushes are "buy two, get one free") is applied against the list of items in the basket.

Once all price adjustments have been applied, the Checkout total is returned (in cents).

## Notable Design Assumptions
- Pricing categories are allowed to "stack" with one another.  
  I.e., if an item is part of a BuyXGetYFree deal and also part of a bundle, the discounts from both can be applied.  
  If desired, the Checkout functionality and PricingCategory data models can be modified in the future to allow for exclusivity.

## Future improvement options
Including but not limited to:  
- Add sad paths and other edge cases to unit testing  
- Expand database model class interfaces to implement full CRUD operations (not needed to complete this coding exercise)  
- Refactor database model classes to use a Model base class with an abstract interface  
- Command line interface for interactivity
- Input validation and sanitization for method calls and properties