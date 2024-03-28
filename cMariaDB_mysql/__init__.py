#!/usr/bin/python3
# -*- coding: utf-8 -*-
import mysql.connector
from mysql.connector import errorcode


class mariaDB_mysql:
    '''
    class to connect to mariaDB and update the table
    '''
    def __init__(self, config):
        self._config = config

    def mariaBD_insert(self, values):
        '''
        function to update mariaDB table
        '''
        
        try:
            # connect to db
            cnx = mysql.connector.connect(**self._config)
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
                print("ERROR: {}".format(err.errno))
                return False
        else:
            try:
                # cursor object
                cursor = cnx.cursor()
                # => use procedure keep in mind ...
                #tablecolumns_E = "`E_import_tot`, `E_export_tot`"
                tablevalues = values
                #print(tablevalues)
                cursor.callproc("add_wb_data", tablevalues)
                cnx.commit()
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_PARSE_ERROR:
                    print("ERROR: Syntax! ({})".format(err.errno))
                    return False
                else:
                    print("ERROR: {}".format(err.errno))
                    return False
            cursor.close()
            cnx.close()
        finally:
            #print("finally")
            pass
        return True