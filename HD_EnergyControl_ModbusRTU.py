"""Script to test connection of HD Energy Control"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cHD_EnergyControl import HD_EnergyControl

# Main
if __name__ == "__main__":
    try:
        obj = HD_EnergyControl("/dev/ttyAMA0", 1)
    except NameError as error:
        print(f"\n\tName Error: {error}, {type(error)}!\n")
    except Exception as error:
        print(f"\n\tERROR: {error}, {type(error)} \
              \n\tError in creating hd_energyControl_mb object!\n")
    else:
        try:
            obj.connect()
            obj.get_register_layout_version()
            obj.get_application_software_revision()

            obj.get_charging_state()
            obj.get_pcb_temperature()
            obj.get_extern_lock_state()
            #obj.set_RemoteLock(1)

            obj.get_power()
            obj.get_currents_rms()
            obj.get_voltages_rms()
            obj.get_energy_since_power_on()
            obj.get_energy_since_installation()

            obj.get_hw_config_max_current()
            obj.get_hw_config_min_current()

            obj.get_standby_function_control()
            #obj.set_standby_function_control(0)
            #obj.get_standby_function_control()

            obj.get_watchdog_timeout()
            #obj.set_watchdog_timeout(65535)


            obj.get_maximal_current_command()
            #obj.set_maximal_current_command()
            #obj.get_maximal_current_command()

            obj.get_failsafe_current_config()
            #obj.set_failsafe_current_config(10.0)
            #obj.get_failsafe_current_config()
        except NameError as error:
            print(f"\n\tName Error: {error}, {type(error)}!\n")
        except ModuleNotFoundError as error:
            print(f"\n\tModule not found Error: {error}, {type(error)}\n!\n")
        except ImportError as error:
            print(f"\n\tImport Error: {error}, {type(error)}\n!\n")
        except Exception as error:
            print(f"\n\tERROR: {error}, {type(error)}\n\tPossibly the device is in standBy-Mode!\n")
    finally:
        obj.close()
        print("INFO: test finished!")
