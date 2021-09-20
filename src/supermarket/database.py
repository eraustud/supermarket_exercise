import sqlite3
import logging

# sqlite3 database wrapper that allows using `with` blocks to safely encapsulate database calls.
# inside a `with` statment, e.g. `with Database('example.db') as db:`, only `execute` calls
#   must be performed. upon exiting the `with` block, the connection will commit the transactions.
# NOTE: this implementation is not thread safe.
class Database:
    database_path = None
    def __init__(self, database_path = None):
        if database_path is not None:
            Database.database_path = database_path
        self.log = logging.getLogger('Database_' + str(Database.database_path))
        if Database.database_path is None:
            raise ValueError('Please set a path to the database before attempting to use it')
        self.connection = None
        self.cursor = None

    def __enter__(self):
        self.log.debug('Opening SQLite3 database connection...')
        self.connection = sqlite3.connect(Database.database_path)
        self.cursor = self.connection.cursor()
        return self.cursor
    
    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            import traceback
            traceback.print_exception(exc_type, exc_value, tb)
        self.connection.commit()
        self.connection.close()
        self.log.debug('Closed database connection.')
        return True