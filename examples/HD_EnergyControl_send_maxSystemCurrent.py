"""Script to test connection of HD Energy Control"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cHD_EnergyControl import HD_EnergyControl
from cMariaDB_mysql import cMariaDB_mysql as maria_db
from mariadb_config import MARIA_DB_CONFIG

# Main
if __name__ == "__main__":
    try:
        obj = HD_EnergyControl("/dev/ttyAMA0", 1)
        obj.connect()
        
        obj.set_maximal_current_command()
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
        print("INFO: test finished!")
