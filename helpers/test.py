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
        system_current = 11.0
    else:
        print("NT-Tarif")
        system_current = 6.0
    print(f"Charge car with {system_current} A")
    
    try:
        obj = HDEnergyControl("/dev/ttyAMA0", 1)
        obj.connect()
        
        #obj.set_maximal_current_command(11)
        
        print(f'register layout version : {obj.get_register_layout_version()}')
        print(f'charging state : {obj.get_charging_state()}')
        i = obj.get_currents_rms()
        print(f'L1 Current (rms) : {i[0]:.2f} A')
        print(f'L2 Current (rms) : {i[1]:.2f} A')
        print(f'L3 Current (rms) : {i[2]:.2f} A', end='\n\n')
        print(f"PCB temperature : {obj.get_pcb_temperature()} °C")
        u = obj.get_voltages_rms()
        print(f'L1 Voltage (rms) : {u[0]:.1f} V')
        print(f'L2 Voltage (rms) : {u[1]:.1f} V')
        print(f'L3 Voltage (rms) : {u[2]:.1f} V', end='\n\n')
        
        print(f'extern lock state : {obj.get_extern_lock_state()}')
        print(f'Power : {obj.get_power()} VA', end='\n\n')
        
        print(f'energy since power on     : {obj.get_energy_since_power_on()/1000.0} kVAh')
        print(f'energy since installation : {obj.get_energy_since_installation()/1000.0} kVAh')
        print(f'hw config current max : {obj.get_hw_config_max_current()} A') 
        print(f'hw config current min : {obj.get_hw_config_min_current()} A') 
        print(f'appication sw revision : {obj.get_application_software_revision()}')
        print(f'watchdog timeout : {obj.get_watchdog_timeout()} ms')
        print(f'standby function control : {obj.get_standby_function_control()}')
        print(f'remote lock : {obj.get_remote_lock()}')
        print(f'max current : {obj.get_maximal_current_command()} A')
        print(f'failsafe current config : {obj.get_failsafe_current_config()} A')
        
        #values_for_db = (*currents, *voltages, power, temperature, energy_since_wake, energy_total)
        #print("values for DB", values_for_db)

        
        #maria_obj = maria_db(MARIA_DB_CONFIG)
        #ret = maria_obj.insert_by_stored_procedure("add_wb_data", values_for_db)

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
