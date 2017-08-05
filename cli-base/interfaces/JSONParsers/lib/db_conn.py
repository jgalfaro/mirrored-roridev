__author__ = 'ender_al'

import MySQLdb

DB_HOST = 'localhost'
DB_USER = 'rori_admin'
DB_PASS = 'rori123'
DB_NAME = 'RORI_DB'


class DBConn:

    def __init__(self, db_host=DB_HOST, db_user=DB_USER, db_pass=DB_PASS, db_name=DB_NAME):
        self.db_host = db_host
        self.db_user = db_user
        self.db_pass = db_pass
        self.db_name = db_name

    def connect(self):
        """Create a database connection"""
        self.db = MySQLdb.connect(host=self.db_host, user=self.db_user,
                                  passwd=self.db_pass, db=self.db_name)

    def open_cursor(self):
        """Open a database cursor"""
        self.cursor = self.db.cursor()

    def execute_query(self, query, values=''):
        """Execute a SQL query"""
        if values != '':
            self.cursor.execute(query, values)
        else:
            self.cursor.execute(query)

    def fetch_data(self):
        """Fetch all the rows from the query"""
        self.rows = self.cursor.fetchall()

    def send_commit(self, query):
        """Send commit to database"""
        sql = query.lower()
        is_select = sql.count('select')
        if is_select < 1:
            self.db.commit()

    def close_cursor(self):
        """Close database cursor"""
        self.cursor.close()

    def execute(self, query, values=''):
        """Compile all the process"""
        # execute all the process if the properties have been defined
        if (self.db_host and self.db_user and self.db_pass and self.db_name and
            query):
            self.connect()
            self.open_cursor()
            self.execute_query(query, values)
            self.send_commit(query)
            self.fetch_data()
            self.close_cursor()

            return self.rows