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

# HT = 7...20; NT = 20...7
HT_TIME = (7, 20)


def get_wallbox_data(obj):
    """get actual wallbox data for saving to database"""
    currents = obj.get_currents_rms()
    voltages = obj.get_voltages_rms()
    power = obj.get_power()
    temperature = obj.get_pcb_temperature()
    energy_since_wake = obj.get_energy_since_power_on()/1000
    energy_total = obj.get_energy_since_installation()/1000
    values_for_db = (*currents, *voltages, power, temperature, energy_since_wake, energy_total)
    # print("values for DB", values_for_db)
    return values_for_db


def get_target_current():
    """calculate actual target current for wallbox"""
    # get struct tm
    tm = time.localtime()
    if (tm.tm_hour >= HT_TIME[0] and tm.tm_hour < HT_TIME[1]):
        print("HT-Tarif")
        system_current = 10.0
    else:
        print("NT-Tarif")
        system_current = 8.0
    return system_current


def send_data_to_database(values):
    """send values provided to Maria DB Database"""
    maria_obj = maria_db(MARIA_DB_CONFIG)
    ret = maria_obj.insert_by_stored_procedure("add_wb_data", values)


def main():
    """ main function """
    # wait for full 10 s
    sleep_time = 10  - (time.time() % 10)
    time.sleep(sleep_time)
    next_communication = time.monotonic()
    next_db_send_time = (int(time.time()) // 60 + 1) * 60
    while True:
        obj = None
        try:
            obj = HDEnergyControl("/dev/ttyAMA0", 1)
            obj.connect()
            target_current = get_target_current()
            print(f"Charge car with {target_current} A")
            obj.set_maximal_current_command(target_current)

            # send data all 60 s
            now = time.time()
            if now >= next_db_send_time:
                next_db_send_time += 60
                values = get_wallbox_data(obj)
                send_data_to_database(values)

        except ImportError as error:
            print(f"Import-/Konfigurationsfehler: {error}", file=sys.stderr)
        except NameError as error:
            print(f"Programmfehler: {error}", file=sys.stderr)
        except Exception as error:
            print(f"ERROR: {error} ({type(error).__name__})", file=sys.stderr)
        finally:
            if obj is not None:
                try:
                    obj.close()
                except Exception as error:
                    print(f"Fehler beim Schließen: {error}", file=sys.stderr)
            obj = None
            next_communication += 10
            sleep_time = next_communication - time.monotonic()
            if sleep_time < 0:
                sleep_time = 10
            print("INFO: finished!", end="\n\n")
            time.sleep(sleep_time)

# main
if __name__ == "__main__":
    main()
