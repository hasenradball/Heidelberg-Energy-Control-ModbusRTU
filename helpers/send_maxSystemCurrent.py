"""Script to test connection of HD Energy Control"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from hd_energy_control import HDEnergyControl
from maria_db_mysql import MariaDBMysql as maria_db
from mariadb_config import MARIA_DB_CONFIG
import time

# main
if __name__ == "__main__":
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

    try:
        obj = HDEnergyControl("/dev/ttyAMA0", 1)
        obj.connect()

        obj.set_maximal_current_command(system_current)
        currents = obj.get_currents_rms()
        voltages = obj.get_voltages_rms()
        power = obj.get_power()
        temperature = obj.get_pcb_temperature()
        energy_since_wake = obj.get_energy_since_power_on()/1000
        energy_total = obj.get_energy_since_installation()/1000
        values_for_db = (*currents, *voltages, power, temperature, energy_since_wake, energy_total)
        #print("values for DB", values_for_db)

        maria_obj = maria_db(MARIA_DB_CONFIG)
        ret = maria_obj.insert_by_stored_procedure("add_wb_data", values_for_db)

    except NameError as error:
        print(f"\n\tName Error: {error}, {type(error)}!\n")
    except ModuleNotFoundError as error:
        print(f"\n\tModule not found Error: {error}, {type(error)}\n!\n")
    except ImportError as error:
        print(f"\n\tImport Error: {error}, {type(error)}\n!\n")
    except Exception as error:
        print(f"\n\tERROR: {error}, {type(error)}\n\tPossibly the device is in standBy-Mode!\n")

    finally:
        print("INFO: finished!")
