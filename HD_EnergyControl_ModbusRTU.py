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
            #obj.set_watchdog_timeout(65535)
            print(f'standby function control : {obj.get_standby_function_control()}')
            #obj.set_standby_function_control(0)
            #obj.get_standby_function_control()
            print(f'remote lock : {obj.get_remote_lock()}')
            #obj.set_RemoteLock(1)
            print(f'max current : {obj.get_maximal_current_command()} A')
            #obj.set_maximal_current_command()
            #obj.get_maximal_current_command()
            print(f'failsafe current config : {obj.get_failsafe_current_config()} A')
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
