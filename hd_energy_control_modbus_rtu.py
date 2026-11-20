"""Script to test connection of HD Energy Control"""

import sys


def main():
    obj = None

    try:
        try:
            from hd_energy_control import HDEnergyControl
        except ImportError as error:
            print(f"Importfehler: {error}", file=sys.stderr)
            return

        obj = HDEnergyControl("/dev/ttyAMA0", 1)
        obj.connect()

        print(f"register layout version : {obj.get_register_layout_version()}")
        print(f"charging state : {obj.get_charging_state()}")

        i = obj.get_currents_rms()
        print(f"L1 Current (rms) : {i[0]:.2f} A")
        print(f"L2 Current (rms) : {i[1]:.2f} A")
        print(f"L3 Current (rms) : {i[2]:.2f} A", end="\n\n")

        print(f"PCB temperature : {obj.get_pcb_temperature()} °C")
        u = obj.get_voltages_rms()
        print(f"L1 Voltage (rms) : {u[0]:.1f} V")
        print(f"L2 Voltage (rms) : {u[1]:.1f} V")
        print(f"L3 Voltage (rms) : {u[2]:.1f} V", end="\n\n")

        print(f"extern lock state : {obj.get_extern_lock_state()}")
        print(f"Power : {obj.get_power()} VA", end="\n\n")

        print(f"energy since power on     : {obj.get_energy_since_power_on() / 1000.0} kVAh")
        print(f"energy since installation : {obj.get_energy_since_installation() / 1000.0} kVAh")
        print(f"hw config current max : {obj.get_hw_config_max_current()} A")
        print(f"hw config current min : {obj.get_hw_config_min_current()} A")
        print(f"application sw revision : {obj.get_application_software_revision()}")
        print(f"watchdog timeout : {obj.get_watchdog_timeout()} ms")
        print(f"standby function control : {obj.get_standby_function_control()}")
        print(f"remote lock : {obj.get_remote_lock()}")
        print(f"max current : {obj.get_maximal_current_command()} A")
        print(f"failsafe current config : {obj.get_failsafe_current_config()} A")

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
