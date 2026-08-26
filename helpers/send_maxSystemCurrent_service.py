"""Script to test connection of HD Energy Control"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from hd_energy_control import HDEnergyControl
from maria_db_mysql import MariaDBMysql as maria_db
from mariadb_config import MARIA_DB_CONFIG
import time
import sys
import logging

logging.getLogger("pymodbus").setLevel(logging.CRITICAL)


def getWallboxData(obj):
   currents = obj.get_currents_rms()
   voltages = obj.get_voltages_rms()
   power = obj.get_power()
   temperature = obj.get_pcb_temperature()
   energy_since_wake = obj.get_energy_since_power_on()/1000
   energy_total = obj.get_energy_since_installation()/1000
   values_for_db = (*currents, *voltages, power, temperature, energy_since_wake, energy_total)
   #print("values for DB", values_for_db)
   return values_for_db


def main():
   # warten auf volle 10 s
   sleep_time = 10  - (time.time() % 10)
   time.sleep(sleep_time)
   next_communication = time.monotonic()
   next_db_sendTime = (int(time.time()) // 60 + 1) * 60
   while (True):
      try:
         obj = HDEnergyControl("/dev/ttyAMA0", 1)
         obj.connect()
         # Kommunication alle 10 s
         # HT = 7...20; NT = 20...7
         HT_TIME = (7, 20)
         # get struct tm
         tm = time.localtime()
         if (tm.tm_hour >= HT_TIME[0] and tm.tm_hour < HT_TIME[1]):
            print("HT-Tarif")
            system_current = 10.0
         else:
            print("NT-Tarif")
            system_current = 8.0
         print(f"Charge car with {system_current} A")
         obj.set_maximal_current_command(system_current)

         # Daten senden alle 60 s
         now = time.time()
         if now >= next_db_sendTime:
            next_db_sendTime += 60
            values = getWallboxData(obj)
            maria_obj = maria_db(MARIA_DB_CONFIG)
            ret = maria_obj.insert_by_stored_procedure("add_wb_data", values)

      except NameError as error:
         print(f"\n\tName Error: {error}, {type(error)}!\n", file=sys.stderr)
      except ModuleNotFoundError as error:
         print(f"\n\tModule not found Error: {error}, {type(error)}\n!\n", file=sys.stderr)
      except ImportError as error:
         print(f"\n\tImport Error: {error}, {type(error)}\n!\n", file=sys.stderr)
      except Exception as error:
         print(f"\n\tERROR: {error}, {type(error)}\n\tPossibly the device is in standBy-Mode!\n")
      finally:
         obj.close()
         next_communication += 10
         sleep_time = next_communication - time.monotonic()
         if sleep_time < 0:
            sleep_time = 10
         print("INFO: finished!", end="\n\n")
         time.sleep(sleep_time)

# main
if __name__ == "__main__":
   main()


