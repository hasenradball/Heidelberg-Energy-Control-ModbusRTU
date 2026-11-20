"""Example for setting the maximum charging current and storing wallbox data."""

import sys


def main():
    obj = None

    try:
        try:
            from hd_energy_control import HDEnergyControl
            from maria_db_mysql import MariaDBMysql as maria_db
            from mariadb_config import MARIA_DB_CONFIG
        except ImportError as error:
            print(f"Importfehler: {error}", file=sys.stderr)
            raise SystemExit(1) from error

        obj = HDEnergyControl("/dev/ttyAMA0", 1)
        obj.connect()

        obj.set_maximal_current_command()

        currents = obj.get_currents_rms()
        voltages = obj.get_voltages_rms()
        power = obj.get_power()
        temperature = obj.get_pcb_temperature()
        energy_since_wake = obj.get_energy_since_power_on() / 1000
        energy_total = obj.get_energy_since_installation() / 1000
        values_for_db = (
            *currents,
            *voltages,
            power,
            temperature,
            energy_since_wake,
            energy_total,
        )

        maria_obj = maria_db(MARIA_DB_CONFIG)
        maria_obj.insert_by_stored_procedure("add_wb_data", values_for_db)

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
        print("INFO: test finished!")


if __name__ == "__main__":
    main()
