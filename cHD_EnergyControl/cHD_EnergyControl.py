#!/usr/bin/python3
# -*- coding: utf-8 -*-

from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.client import ModbusSerialClient as ModBusClient
from .Modbus_Constants import Modbus_Contants as CONSTS

class ModbusRTU:
    '''Base class for ModbusRTU
    1.) make sure the python lib 'pymodbus' is installed
    2.) Please check if the an terminating resistor is needed
    3.) check Register description --> see specific documentation of manufacturer
        e.g.: https://www.amperfied.de/en/service-support-e/downloads-e/ 
    '''
    def __init__(self, device_unit_id, port = "/dev/ttyUSB0"):
        self._client = ModBusClient(port=port, baudrate = 19200, bytesize = 8, stopbits = 1, parity = 'E')
        self._device_unit_id = device_unit_id
        print("Device Unit: ", self._device_unit_id)


    def __del__(self):
        del self._client
        del self._device_unit_id


    def connect(self):
        '''Establish conncetion of client
        '''
        try:
            if self._client.connect():
                print("INFO: client connected successfully to Modbus-RTU Device!", end='\n\n')
            else:
                print("ERROR: client cannot connect to Modbus-RTU Device!")
        except:
            print("ERROR: Propably an Syntax Error!")
            
        finally:
            pass
        

    def close(self):
        '''Close connection of client
        '''
        if self._client.is_socket_open():
            self._client.close()
            print("INFO: Connection closed!")
        return None

    def read_input_register(self, register_address, datatype, count = 1):
        '''Read the input register from the HD Wallbox
        '''
        length = CONSTS.TYPE_TO_LENGTH[datatype] * count
        #print(f'length : {length}')
        result = self._client.read_input_registers(register_address, length, slave=self._device_unit_id)
        #print(type(result.registers), ": ", result.registers)
        data = self.decode_register_readings(result, datatype, count)
        return data


    def read_holding_register(self, register_address, datatype, count = 1):
        '''Read the holding register from the HD Wallbox
        '''
        length = CONSTS.TYPE_TO_LENGTH[datatype] * count
        #print(f'length : {length}')
        result = self._client.read_holding_registers(register_address, length, slave=self._device_unit_id)
        #print(type(result.registers), ": ", result.registers)
        data = self.decode_register_readings(result, datatype, count)
        return data

    def decode_register_readings(self, readings, datatype, count):
        '''Decode the register readings dependend on datatype
        '''
        decoder = BinaryPayloadDecoder.fromRegisters(readings.registers, byteorder=Endian.BIG, wordorder=Endian.BIG)
        #print(f'decoder : {decoder}')
        if (datatype == 'U16'):
            data = [decoder.decode_16bit_uint() for i in range(count)]
        elif (datatype == 'U32'):
            data = [decoder.decode_32bit_uint() for i in range(count)]
        elif (datatype == 'U64'):
            data = [decoder.decode_64bit_uint() for i in range(count)]
        elif (datatype == 'S16'):
            data = [decoder.decode_16bit_int() for i in range(count)]
        elif (datatype == 'S32'):
            data = [decoder.decode_32bit_int() for i in range(count)]
        return data



class HD_EnergyControl(ModbusRTU):
    '''class for conntetion to the Wallbox Heidelberg Energy Control
    '''
    def get_register_layout_version(self):
        '''Read out the Register Layout Version
            Register-Adress:      4
            Datatype:             uint16; U16
            Function-Code:        0x04
        '''
        version_dec = self.read_input_register(4, 'U16')[0]
        #print(type(result.registers), ": ", result.registers)
        version_hex = "{:0x}".format(version_dec)
        version_str = "v{}".format(".".join("%c" %char for char in version_hex))
        print(f'[004]\t\tRegister-Layout : {version_str}', end='\n\n')
        return version_str
    
    
    def get_charging_state(self):
        '''Read out the charging State refered to EN 61851-1 standard
           Register-Adress:    5
           Datatype:           uint16; U16
           Function-Code:      0x04
        '''
        state = {2: 'A1', 3: 'A2', 4: 'B1', 5: 'B2', 6: 'C1', 7: 'C2', 8: '--', 9: 'E', 10: 'F', 11: '--'}
        
        car = { 2: 'No vehicle plugged',
                3: 'No vehicle plugged',
                4: 'Vehicle plugged without charging request',
                5: 'Vehicle plugged without charging request',
                6: 'Vehicle plugged with charging request',
                7: 'Vehicle plugged with charging request',
                8: '--',
                9: 'Error',
                10: '--',
                11: '--'}
        
        wallbox = { 2: 'Wallbox does not allow charging', 
                    3: 'Wallbox allow charging',
                    4: 'Wallbox does not allow charging',
                    5: 'Wallbox allow charging',
                    6: 'Wallbox does not allow charging',
                    7: 'Wallbox allow charging',
                    8: 'Derating',
                    9: 'Error',
                    10: 'Wallbox locked or not ready',
                    11: 'Error'}
        
        value = self.read_input_register(5, 'U16')[0]
        charge_state = (state[value], car[value], wallbox[value])
        print('[005]\t\tCharge-State : {}'.format(' '.join(charge_state)), end='\n\n')
        return charge_state
    

    def get_currents_rms(self):
        '''Read out the L1 L2 L3 Current RMS
           Register-Adress:    6
           Datatype:           uint16; U16
           Function-Code:      0x04
        '''
        current = self.read_input_register(6, 'U16', 3)
        L1_current = current[0]/10
        L2_current = current[1]/10
        L3_current = current[2]/10
        print('[006]\t\tL1 Current (rms) : {:.2f} A'.format(L1_current))
        print('[007]\t\tL2 Current (rms) : {:.2f} A'.format(L2_current))
        print('[008]\t\tL3 Current (rms) : {:.2f} A'.format(L3_current), end='\n\n')
        return (L1_current, L2_current, L3_current)
    

    def get_pcb_temperature(self):
        '''Read out the PCB temperature
           Register-Adress:    9
           Datatype:           int16; S16
           Function-Code:      0x04
        '''
        data = self.read_input_register(9, 'S16')[0]
        temperature = data/10
        print('[009]\t\tPCB temperature : {:6.2f} °C'.format(temperature), end='\n\n')
        return temperature
    

    def get_voltages_rms(self):
        '''Read out the L1-N L2-N L3-N Voltage RMS
           Register-Adress:    10
           Datatype:           uint16; U16
           Function-Code:      0x04
        '''
        voltage = self.read_input_register(10, 'U16', 3)
        L1_voltage = voltage[0]
        L2_voltage = voltage[1]
        L3_voltage = voltage[2]
        print('[010]\t\tL1 Voltage (rms) : {:.1f} V'.format(L1_voltage))
        print('[011]\t\tL2 Voltage (rms) : {:.1f} V'.format(L2_voltage))
        print('[012]\t\tL3 Voltage (rms) : {:.1f} V'.format(L3_voltage), end='\n\n')
        return (L1_voltage, L2_voltage, L3_voltage)
    

    def get_extern_lock_state(self):
        '''Read out the extern Lock State
           Register-Adress:    13
           Datatype:           uint16; U16
           Function-Code:      0x04
        '''
        lock = {0: 'System locked', 1: 'System unlocked'}
        lock_state = self.read_input_register(13, 'U16')[0]
        print(f'[013]\t\tExtern Lock State : {lock[lock_state]}', end='\n\n')
        return lock_state
    

    def get_power(self):
        '''Read out the Power of L1 + L2 + L3 in VA
           Register-Adress:    14
           Datatype:           uint16; U16
           Function-Code:      0x04
        '''
        power = self.read_input_register(14, 'U16')[0]
        print(f'[014]\t\tPower : {power} VA', end='\n\n')
        return power
    

    def get_energy_since_power_on(self):
        '''Read out the Energy since power on
           Register-Adress:    15
           Datatype:           uint16; U16
           Function-Code:      0x04

        Example:
        high Byte = 1     => 1 * 2^(16) => 65536 VAh
        low Byte  = 1000  => 1000 => 1000 VAh
        result = (65536 + 1000) = 66536 VAh
        '''
        data = self.read_input_register(15, 'U16', 2)
        energy_high_byte = data[0]
        energy_low_byte = data[1]
        energy = energy_high_byte * pow(2, 16) + energy_low_byte
        print(f'[015-016]\tEnergy since PowerOn : {energy} VAh', end='\n\n')
        return energy
    

    def get_energy_since_installation(self):
        '''Read out the Energy since Installation
           Register-Adress:    17
           Datatype:           uint16; U16
           Function-Code:      0x04

        Example:
        high Byte = 5     => 5 * 2^(16) => 327680 VAh
        low Byte  = 10  => 10 => 10 VAh
        result = (327680 + 10) = 327690 VAh
        '''
        data = self.read_input_register(17, 'U16', 2)
        energy_high_byte = data[0]
        energy_low_byte = data[1]
        energy = energy_high_byte * pow(2, 16) + energy_low_byte
        print(f'[017-018]\tEnergy since Installation : {energy} VAh', end='\n\n')
        return energy
    

    def get_hw_config_max_current(self):
        '''Read out the Hardware config for max current
           Register-Adress:    100
           Datatype:           uint16; U16
           Function-Code:      0x04
        '''
        hw_max_current = self.read_input_register(100, 'U16')[0]
        print(f'[100]\t\tHardware config max current : {hw_max_current} A', end='\n\n')
        return hw_max_current
    

    def get_hw_config_min_current(self):
        '''Read out the Hardware config for min current
           Register-Adress:    101
           Datatype:           uint16; U16
           Function-Code:      0x04
        '''
        hw_min_current = self.read_input_register(101, 'U16')[0]
        print(f'[101]\t\tHardware config min current : {hw_min_current} A', end='\n\n')
        return hw_min_current
    

    def get_application_software_revision(self):
        '''Read out the Application Software Revision
           Register-Adress:      203
           Datatype:             uint16; U16
           Function-Code:        0x04
        '''
        revision_svn = self.read_input_register(203, 'U16')[0]
        print(f'[203]\t\tAppl-SW Revision : {revision_svn}', end='\n\n')
        return revision_svn
    

    def get_watchdog_timeout(self):
        '''Read out the WatchDog Timeout Register
           Register-Adress:    257
           Datatype:           uint16; U16
           Function-Code:      0x03
        '''
        wdt = self.read_holding_register(257, 'U16')[0]
        print(f'[257]\t\tWatchDog Timeout : {wdt} ms', end='\n\n')
        return wdt

    def set_watchdog_timeout(self, timeout_ms = 0):
        '''write X ms in the WatchDog Timeout Register
           Register-Adress:    257
           Datatype:           uint16; U16
           Function-Code:      0x06
        '''
        result = self._client.write_register(257, timeout_ms, slave=self._device_unit_id)
        print(f'WatchDog Timeout set : {result} ms', end='\n\n')
        return result

    
    def get_standby_function_control(self):
        '''Read out the StandByFunction Control Register
           Register-Adress:    258
           Datatype:           uint16; U16
           Function-Code:      0x03
        '''
        standby_function = {0: 'enable StandBy Function', 4: 'disable StandBy Function'}
        standby = self.read_holding_register(258, 'U16')[0]
        print(f'[258]\t\tStandBy Function : {standby_function[standby]}', end='\n\n')
        return standby

    
    def set_standby_function_control(self, state):
        '''Set the StandByFunction Control Register
           Register-Adress:    258
           Datatype:           uint16; U16
           Function-Code:      0x06
        '''
        if state == 0:
            # enable StandBy Function Control
            _state = 0
        elif state == 4:
            # disable StandBy Function Control
            _state = 4
        else:
            # no valid value reached
            print ('ERROR: No valid value for setting the StandBy Function Control')
            return None
        result = self._client.write_register(258, _state, slave=self._device_unit_id)
        print(f'StandBy Function set : {result} ', end='\n\n')
        return result
    
    
    def set_remote_lock(self, state):
        '''Set the Remote lock state
           Register-Adress:    259
           Datatype:           uint16; U16
           Function-Code:      0x06
        '''
        if state == 0:
            # system locked by user => system does NOT go into StandBy
            _state = 0
        elif state == 1:
            # system is unlocked
            _state = 1
        else:
            # no valid value reached
            print ('ERROR: No valid value for setting the Remote Lock')
            return None
        result = self._client.write_register(259, _state, slave=self._device_unit_id)
        print(f'Remote-Lock set : {result}', end='\n\n')
        return result
    

    def get_maximal_current_command(self):
        '''Read out the Maxinmal Current command register
           Register-Adress:    261
           Datatype:           uint16; U16
           Function-Code:      0x03
        '''
        data = self.read_holding_register(261, 'U16')[0]
        max_current = data/10
        print('[261]\t\tMaximal Charging Current : {:.2f} A'.format(max_current), end='\n\n')
        return max_current


    def set_maximal_current_command(self, max_current = 16.0):
        '''write x A in the Maximal Current Command Register
           Register-Adress:    261
           Datatype:           uint16; U16
           Function-Code:      0x06

        Remark:
            Values of 0.1...5.9 are not allowed these are interpreted as 0.0 A
            Only 
        '''
        if max_current > 16.0:
            # bound value to max of 16.0 A
            max_current = 16.0
        elif max_current < 6.0:
            print (f'Your Input value ({max_current}) is interpreted a 0.0 A, because the value is below 6.0 A')
        _max_current = int(max_current * 10)

        # first read the actual regisster value if it is already the same => no need to write again
        actual_current = self.get_maximal_current_command()
        if actual_current == max_current:
            print(f'\tNo need to write into register, because the desired value {max_current} is already in register!', end='\n\n')
            return None
        else:
            result = self._client.write_register(261, _max_current, slave=self._device_unit_id)
            print(f'Maximal Charging Current set : {result} A', end='\n\n')
            return result


    def get_failsafe_current_config(self):
        '''Read out the FailSafe Current Configuration
           Register-Adress:    262
           Datatype:           uint16; U16
           Function-Code:      0x03
        '''
        data = self.read_holding_register(262, 'U16')[0]
        fs_current = data/10
        print('[262]\t\tFailSafe Current : {:.2f} A'.format(fs_current), end='\n\n')
        return fs_current

    def set_failsafe_current_config(self, fs_current = 16.0):
        '''Write x A in the Fail Safe Current Configuration Register
           Register-Adress:    262
           Datatype:           uint16; U16
           Function-Code:      0x06
        '''
        if fs_current > 16.0:
            # bound value to max of 16.0 A
            fs_current = 16.0
        elif fs_current < 6.0:
            print (f'Your Input fs_current({fs_current}) is interpreted a 0.0 A, because the value is below 6.0 A')
        _fs_current = int(fs_current * 10)
        result = self._client.write_register(262, _fs_current, slave=self._device_unit_id)
        print('FailSafe Current set : {}'.format(result), end='\n\n')
        return result
