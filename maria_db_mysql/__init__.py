"""Class for connecting and insert into mariaDB"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import mysql.connector
from mysql.connector import errorcode


class MariaDBMysql:
    """Class connecting MariaDB Database"""

    def __init__(self, config):
        """Contructor of cMariaDB_mysql class 
        -----

        Args:
            config: configuration for mariaDB access
        """
        self._config = config
        # call connect to have the connection object inside
        self.connector = self.connect()

    def __del__(self):
        #destoy the connector object
        #print("Call destructor")
        self.connector.close()

    def connect(self):
        """Method to establish connection to database
        -----

        Returns:
            MySQLConnection object or False
        """
        try:
            connector_obj = mysql.connector.connect(**self._config)
            #print("cnx: ", cnx)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("ERROR: User/Password!")
                return False
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("ERROR: No Database!")
                return False
            elif err.errno == errorcode.CR_CONN_HOST_ERROR:
                print("ERROR: Connection!")
                return False
            else:
                print(f"ERROR: {err.errno}")
                return False
        else:
            #print("Connection: successfully established!")
            return connector_obj

    def insert_by_stored_procedure(self, prodedure_name, arguments) -> bool:
        """Insert data into mariaDB by calling a strored procedure
        -----

        Args:
            procedure_name: name of the stored procedure function
            arguments: function parameters for the stored procedure

        Returns:
            True when successful or False when failed
        """
        try:
            cursor = self.connector.cursor()
            cursor.callproc(prodedure_name, arguments)
            self.connector.commit()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_PARSE_ERROR:
                print(f"ERROR: Syntax! ({err.errno})")
                return False
            else:
                print(f"ERROR: {err.errno}")
                return False
        else:
            cursor.close()
            return True

    def insert_by_sql_insert_stmt(self, table, columns, values) -> bool:
        """Insert data into mariaDB by insert statement
        -----

        Args:
            table: string 
            columns: tuple 
            values: tuple

        Returns:
            True when successful or False when failed
        """
        try:
            cursor = self.connector.cursor()
            # INSERT INTO `waermepumpe`.`energie` (E_import_tot, E_export_tot) VALUES(20.9, 31.4)
            query_str = f"INSERT INTO `{self._config['database']}`.`{table}` ({columns}) VALUES({str(values)})"
            #print(query_str)
            cursor.execute(query_str)
            self.connector.commit()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_PARSE_ERROR:
                print(f"ERROR: Syntax! ({err.errno})")
                return False
            else:
                print(f"ERROR: {err.errno}")
                return False
        else:
            cursor.close()
            return True
