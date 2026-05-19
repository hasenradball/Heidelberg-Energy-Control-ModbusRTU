"""module for connecting and insert into mariaDB database"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import inspect
import mysql.connector
from mysql.connector import errorcode

import logging

logging.basicConfig(
   level=logging.ERROR,
   format="%(asctime)s | %(levelname)s | %(message)s",
   datefmt="%Y-%m-%d %H:%M:%S"
)

class MariaDBMysql:
   """Class connecting MariaDB Database"""

   def __init__(self, config):
      """Constructor of cMariaDB_mysql class 
      -----

      Args:
         config: configuration for mariaDB access
      """
      self._config = config
      # call connect to have the connection object inside
      self.connector = self.connect()

   def __del__(self):
      #destroy the connector object
      #print("Call destructor")
      self.connector.close()

   def print_caller_file(self, caller_frame):
      """"Method to print caller filename
      """
      caller_file = caller_frame.filename
      print(f"Called by: {caller_file}")
      
   def log_error(self, error):
      caller = inspect.stack()[2]
      logging.error(
         f"Caller: {caller.filename} | "
         f"Line: {caller.lineno} | "
         f"ErrorNo: {getattr(error, 'errno', 'N/A')} | "
         f"Message: {error}"
      )
      print(f"   ERROR({error.errno}): {error.msg}")
      
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
         self.log_error(err)
         return False
      else:
         #print("Connection: successfully established!")
         return connector_obj

   def insert_by_stored_procedure(self, procedure_name, arguments) -> bool:
      """Insert data into mariaDB by calling a stored procedure
      -----

      Args:
         procedure_name: name of the stored procedure function
         arguments: function parameters for the stored procedure

      Returns:
         True when successful or False when failed
      """
      try:
         cursor = self.connector.cursor()
         cursor.callproc(procedure_name, arguments)
         self.connector.commit()
      except mysql.connector.Error as err:
         self.log_error(err)
         return False
      else:
         cursor.close()
         return True

   def insert_by_sql_insert_stmt(self, table, columns, *values) -> bool:
      """Insert data into mariaDB by insert statement
      -----
      Args:
         table: string 
         columns: tuple 
         values: tuple

      Returns:
         True when successful or False when failed
      """
      placeholders = ", ".join(["%s"] * len(values))
      try:
         cursor = self.connector.cursor()
         # INSERT INTO `waermepumpe`.`energie` (E_import_tot, E_export_tot) VALUES(20.9, 31.4)
         query_str = (
            f"INSERT INTO `{self._config['database']}`.`{table}`"
            f"({columns}) VALUES({placeholders})"
         )
         #print(query_str)
         cursor.execute(query_str, values)
         self.connector.commit()
      except mysql.connector.Error as err:
         self.log_error(err)
         return False
      else:
         cursor.close()
         return True
