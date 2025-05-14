"""module providing HD Energy Control ModbusRTU implementation"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.client import ModbusSerialClient as ModBusClient
from pymodbus import (FramerType, ExceptionResponse, ModbusException)
from .constants import HDEnergyControlConstants as CONSTS

class ModbusRTU:
    """Base class for ModbusRTU
    1.) make sure the python lib 'pymodbus' is installed
    2.) Please check if the an terminating resistor is needed
    3.) check Register description --> see specific documentation of manufacturer
        e.g.: https://www.amperfied.de/en/service-support-e/downloads-e/ 
    """
    def __init__(self, port = "/dev/ttyUSB0", device_unit_id = 1):
        self._client = ModBusClient(port=port, framer=FramerType.RTU, baudrate = 19200, \
                                    bytesize = 8, stopbits = 1, parity = 'E')
        self._device_unit_id = device_unit_id
        print("Device Unit: ", self._device_unit_id)


    def __del__(self):
        """ Desctructor of ModbusRTU
        """
        self.close()
        del self._client
        del self._device_unit_id


    def connect(self):
        """Establish conncetion of client
        """
        try:
            if self._client.connect():
                print("INFO: client connected successfully to Modbus-RTU Device!", end='\n\n')
            else:
                print("ERROR: client cannot connect to Modbus-RTU Device!")
        except Exception as exc:
            print(f"ERROR: received exception {exc}! Propably an Syntax Error!")

        finally:
            pass


    def close(self):
        """Close connection of client
        """
        if self._client.is_socket_open():
            self._client.close()
            print("INFO: Connection closed!")
        return None

    def read_input_register(self, register_address, datatype, count = 1):
        """Read the input register from the HD Wallbox
        """
        length = CONSTS.TYPE_TO_LENGTH[datatype] * count
        #print(f'length : {length}')
        try:
            result = self._client.read_input_registers(register_address, count=length, \
                                                     slave=self._device_unit_id)
            #print(result, type(result))
        except ModbusException as exc:
            print(f">>> read_input_register: Received ModbusException({exc}) from library")
        if result.isError():
            print(f">>> read_input_register: Received Modbus library error({result})")
        if isinstance(result, ExceptionResponse):
            print(f">>> read_input_register: Received Modbus library exception ({result})")
            # THIS IS NOT A PYTHON EXCEPTION, but a valid modbus message
            return False
        #print(type(result.registers), ": ", result.registers)
        data = self.decode_register_readings(result, datatype, count)
        return data


    def read_holding_register(self, register_address, datatype, count = 1):
        """Read the holding register from the HD Wallbox
        """
        length = CONSTS.TYPE_TO_LENGTH[datatype] * count
        #print(f'length : {length}')
        try:
            result = self._client.read_holding_registers(register_address, count=length, \
                                                     slave=self._device_unit_id)
            #print(result, type(result))
        except ModbusException as exc:
            print(f">>> read_holding_register: Received ModbusException({exc}) from library")
        if result.isError():
            print(f">>> read_holding_register: Received Modbus library error({result})")
        if isinstance(result, ExceptionResponse):
            print(f">>> read_holding_register: Received Modbus library exception ({result})")
            # THIS IS NOT A PYTHON EXCEPTION, but a valid modbus message
            return False
        #print(type(result.registers), ": ", result.registers)
        data = self.decode_register_readings(result, datatype, count)
        return data

    def decode_register_readings(self, readings, datatype, count):
        """Decode the register readings dependend on datatype
        """
        data = []
        if datatype == 'U16':
            data = self._client.convert_from_registers(readings.registers, data_type=self._client.DATATYPE.UINT16)
        elif datatype == 'U32':
            data = self._client.convert_from_registers(readings.registers, data_type=self._client.DATATYPE.UINT32)
        elif datatype == 'U64':
            data = self._client.convert_from_registers(readings.registers, data_type=self._client.DATATYPE.UINT64)
        elif datatype == 'S16':
            data = self._client.convert_from_registers(readings.registers, data_type=self._client.DATATYPE.INT16)
        elif datatype == 'S32':
            data = self._client.convert_from_registers(readings.registers, data_type=self._client.DATATYPE.INT32)
        return data

    def write_register(self, register_address, register_value):
        """Write register method (code 0x06) with error handling
        """
        try:
            result = self._client.write_registers(register_address, register_value, \
                                                     slave=self._device_unit_id)
            #print(result, type(result))
        except ModbusException as exc:
            print(f">>> write_register: Received ModbusException({exc}) from library")
        if result.isError():
            print(f">>> write_register: Received Modbus library error({result})")
        if isinstance(result, ExceptionResponse):
            print(f">>> write_register: Received Modbus library exception ({result})")
            # THIS IS NOT A PYTHON EXCEPTION, but a valid modbus message
            return False
        return True



class HDEnergyControl(ModbusRTU):
    """class for connecting the Wallbox Heidelberg Energy Control
    """
    def get_register_layout_version(self) -> str:
        """Get register layout version
        
        Read out the Register Layout Version
        -----
        Returns:
            version_str
        -----
        Register address: 4; U16
        Function-Code: 0x04
        """
        version_dec = self.read_input_register(4, 'U16')
        #print(type(result.registers), ": ", result.registers)
        version_hex = f"{version_dec:0x}"
        version_str = f"v{'.'.join(f'{char}' for char in version_hex)}"
        #print(f'[004]\t\tRegister-Layout : {version_str}', end='\n\n')
        return version_str

    def get_charging_state(self) -> tuple[str]:
        """Get charging state
        
        Read out the charging State refered to EN 61851-1 standard
        -----
        Returns:
            charge state
        -----
        Register address: 5; U16
        Function-Code:      0x04
        Unit: 1
        """
        value = self.read_input_register(5, 'U16')
        charge_state = (CONSTS.STATE[value], CONSTS.CAR[value], CONSTS.WALLBOX[value])
        #print('[005]\t\tCharge-State : {}'.format(' '.join(charge_state)), end='\n\n')
        return charge_state

    def get_currents_rms(self) -> tuple:
        """Get current
        
        Read the current i1, i2, i3 (rms)
        -----
        Returns:
            current i1, i2, i3
        -----
        Register address: 6, 7, 8; U16
        Function-Code: 0x04
        Unit: A
        """
        current_list = self.read_input_register(6, 'U16', 3)
        i = tuple(i/10 for i in current_list)
        #print(f'[006]\t\tL1 Current (rms) : {i[0]:.2f} A')
        #print(f'[007]\t\tL2 Current (rms) : {i[1]:.2f} A')
        #print(f'[008]\t\tL3 Current (rms) : {i[2]:.2f} A', end='\n\n')
        return i

    def get_pcb_temperature(self) -> float:
        """Get PCB temperature
        
        Read out the PCB temperature
        -----
        Returns:
            temperature
        -----
        Register address: 9; S16
        Function-Code: 0x04
        Unit: °C
        """
        data = self.read_input_register(9, 'S16')
        temperature = data/10
        #print(f'[009]\t\tPCB temperature : {temperature:6.2f} °C', end='\n\n')
        return temperature

    def get_voltages_rms(self) -> tuple[int]:
        """Get Voltage
        
        Read the voltages L1-N L2-N L3-N (rms)
        -----
        Returns:
            voltages u1, u2 , u3
        -----
        Register address: 10, 11, 12; U16
        Function-Code: 0x04
        Unit: V
        """
        voltage_list = self.read_input_register(10, 'U16', 3)
        u = tuple(voltage_list)
        #print(f'[010]\t\tL1 Voltage (rms) : {u[0]:.1f} V')
        #print(f'[011]\t\tL2 Voltage (rms) : {u[1]:.1f} V')
        #print(f'[012]\t\tL3 Voltage (rms) : {u[2]:.1f} V', end='\n\n')
        return u

    def get_extern_lock_state(self) -> tuple:
        """Get extern lock state
        
        Read out the extern Lock State
        -----
        Returns:
            lock_state
        0: Sytem locked
        1: System unlocked
        -----
        Register address: 13; U16
        Function-Code:      0x04
        Unit: 1
        """
        lock = {0: 'System locked', 1: 'System unlocked'}
        lock_state = self.read_input_register(13, 'U16')
        #print(f'[013]\t\tExtern Lock State : {lock[lock_state]}', end='\n\n')
        return (lock_state, lock[lock_state])

    def get_power(self) -> int:
        """Get the power (sum of all phases)
        
        Read out the Power of L1 + L2 + L3
        -----
        Returns:
            power
        -----
        Register address: 14; U16
        Function-Code: 0x04
        Unit; VA
        """
        power = self.read_input_register(14, 'U16')
        #print(f'[014]\t\tPower : {power} VA', end='\n\n')
        return power

    def get_energy_since_power_on(self) -> int:
        """Get energy since power on

        Read out the Energy since power on
        -----
        Returns:
            energy
        -----
        Register address: 15 + 16; U16
        Function-Code: 0x04
        Unit: VAh

        Example:
        high Byte = 1     => 1 * 2^(16) => 65536 VAh

        low Byte  = 1000  => 1000 => 1000 VAh

        result = (65536 + 1000) = 66536 VAh
        """
        data = self.read_input_register(15, 'U16', 2)
        energy_high_byte = data[0]
        energy_low_byte = data[1]
        energy = energy_high_byte * pow(2, 16) + energy_low_byte
        #print(f'[015-016]\tEnergy since PowerOn : {energy} VAh', end='\n\n')
        return energy

    def get_energy_since_installation(self) -> int:
        """Get energy since installation

        Read out the Energy since Installation
        -----
        Returns:
            energy
        -----
        Register address: 17 + 18; U16
        Function-Code: 0x04
        Unit: VAh
        -----
        Example:

        high Byte = 5     => 5 * 2^(16) => 327680 VAh

        low Byte  = 10  => 10 => 10 VAh

        result = (327680 + 10) = 327690 VAh
        """
        data = self.read_input_register(17, 'U16', 2)
        energy_high_byte = data[0]
        energy_low_byte = data[1]
        energy = energy_high_byte * pow(2, 16) + energy_low_byte
        #print(f'[017-018]\tEnergy since Installation : {energy} VAh', end='\n\n')
        return energy

    def get_hw_config_max_current(self) -> int:
        """Get the hw config max current

        Read the hardware switch of the maximal current
        -----
        Returns:
            hw_max_current
        -----
        Register address: 100; U16
        Function-Code: 0x04
        Unit: A
        """
        hw_max_current = self.read_input_register(100, 'U16')
        #print(f'[100]\t\tHardware config max current : {hw_max_current} A', end='\n\n')
        return hw_max_current

    def get_hw_config_min_current(self) -> int:
        """Get the hw config min current

        Read the hardware switch of the minimal current
        -----
        Returns:
            hw_min_current
        -----
        Register address: 101; U16
        Function-Code: 0x04
        Unit: A
        """
        hw_min_current = self.read_input_register(101, 'U16')
        #print(f'[101]\t\tHardware config min current : {hw_min_current} A', end='\n\n')
        return hw_min_current

    def get_application_software_revision(self) -> int:
        """Read Software Revision
        
        Read out the Application Software Revision
        -----
        Register address: 203; U16
        Function-Code: 0x04
        Unit: -
        """
        revision_svn = self.read_input_register(203, 'U16')
        #print(f'[203]\t\tAppl-SW Revision : {revision_svn}', end='\n\n')
        return revision_svn

    def get_watchdog_timeout(self) -> int:
        """Read out the WatchDog Timeout Register
        -----
        Register address: 257; U16
        Function-Code: 0x03
        Unit: ms
        """
        wdt_timeout = self.read_holding_register(257, 'U16')
        #print(f'[257]\t\tWatchDog Timeout : {wdt_timeout} ms', end='\n\n')
        return wdt_timeout

    def set_watchdog_timeout(self, timeout_ms = 0) -> bool:
        """Set the watschdog timeout
        
        Write xx ms in the WatchDog Timeout Register
        -----
        Args:
            timeout_ms (int): timeout value in ms

        Returns:
            results: True if successful, Fasle otherwise
        -----
        Register address: 257; U16
        Function-Code: 0x06
        Unit: ms
        """
        result = self.write_register(257, timeout_ms)
        #print(f'[257]\t\tWatchDog Timeout set to : {result} ms', end='\n\n')
        return result

    def get_standby_function_control(self) -> tuple:
        """Read the StandByFunction Control
        -----
        Register address: 258; U16
        Function-Code: 0x03
        Unit: -
        """
        standby = self.read_holding_register(258, 'U16')
        #print(f'[258]\t\tStandBy Function : {CONSTS.STANDBY_FUNCTION[standby]}', end='\n\n')
        return (standby, CONSTS.STANDBY_FUNCTION[standby])

    def set_standby_function_control(self, state) -> bool:
        """Set the StandByFunction Control

        Write into the StandByFunction Control Register
        -----
        Args:
            state (int): 0 = enable Standby
                         4 = disable Standby
        Remark:
            Don't use other values than 0 and 4!

        Returns:
            result: True if successful, Fasle otherwise
        -----
        Register address: 258; U16
        Function-Code: 0x06
        Unit: -
        """
        if state == 0:
            # enable StandBy Function Control
            _state = 0
        elif state == 4:
            # disable StandBy Function Control
            _state = 4
        else:
            # no valid value reached
            print ('ERROR: No valid value for setting the StandBy Function Control')
            return False
        result = self.write_register(258, _state)
        #print(f'[258]\t\tStandBy Function set to : {CONSTS.STANDBY_FUNCTION[self.get_standby_function_control()]} ', end='\n\n')
        return result


    def get_remote_lock(self) -> tuple:
        """Get the Remote lock state
        -----
        Returns:
            result: module lock state
        -----
        Register address: 259; U16
        Function-Code: 0x03
        Unit: -
        """
        result = self.read_holding_register(259, 'U16')
        #print(f'[259]\t\tRemote-Lock state : {CONSTS.REMOTE_LOCK[result]}', end='\n\n')
        return (result, CONSTS.REMOTE_LOCK[result])

    def set_remote_lock(self, state) -> bool:
        """Set the Remote lock state
        -----
        Args:
            state (int): 0 = locked / 1 = unlocked
        
        Returns:
            result: True if successful, Fasle otherwise
        -----
        Register address: 259; U16
        Function-Code: 0x06
        Unit: -
        """
        if state == 0:
            # system locked by user => system does NOT go into StandBy
            _state = 0
        elif state == 1:
            # system is unlocked
            _state = 1
        else:
            # no valid value reached
            print ('ERROR: No valid value for setting the Remote Lock')
            return False
        result = self.write_register(259, _state)
        #print(f'[259]\t\tRemote-Lock set : {CONSTS.REMOTE_LOCK[self.get_remote_lock()]}', end='\n\n')
        return result

    def get_maximal_current_command(self) -> float:
        """Get maximal current
        
        Read out the Maxinmal Current command register
        -----
        Register address: 261; U16
        Function-Code: 0x03
        Unit: A
        """
        data = self.read_holding_register(261, 'U16')
        max_current = data/10
        #print(f'[261]\t\tMaximal Charging Current : {max_current:.2f} A', end='\n\n')
        return max_current

    def set_maximal_current_command(self, max_current = 16.0) -> bool:
        """Set maximal current

        Write x A in the Maximal Current Command Register
        -----
        Args:
            max_current (float): maximal current in A
        
        Returns:
            result: True if update was successful; False if not needed 
        -----
        Register address: 261; U16
        Function-Code: 0x06
        Unit: A

        Remark:
            Values of 0.1...5.9 are not allowed these are interpreted as 0.0 A
            Only 
        """
        if max_current > 16.0:
            # bound value to max of 16.0 A
            max_current = 16.0
        elif max_current < 6.0:
            print (f'Input ({max_current}) is bound to 0 A, due to HW restriction < 6.0 A')
        _max_current = int(max_current * 10)

        # first read the actual regisster value if it is already the same => no need to write again
        actual_current = self.get_maximal_current_command()
        if actual_current == max_current:
            print(f'[set_maximal_current_command]: value not writen, {max_current} A is already set!', end='\n\n')
            return False
        else:
            result = self.write_register(261, _max_current)
            #print(f'[261]\t\tMax Charging Current set to : {self.get_maximal_current_command()} A', end='\n\n')
            return result


    def get_failsafe_current_config(self) -> bool:
        """Get FailSafe Current
        ------
        Register address: 262; U16
        Function-Code: 0x03
        Unit: A
        """
        data = self.read_holding_register(262, 'U16')
        fs_current = data/10
        #print(f'[262]\t\tFailSafe Current : {fs_current:.2f} A', end='\n\n')
        return fs_current

    def set_failsafe_current_config(self, fs_current = 16.0) -> bool:
        """Set Failsafe current
        
        Write x A in the Fail Safe Current Configuration Register
        -----
        Args:
            fs_current (float): fail safe current in A
        
        Returns:
            result: True if successful
        -----
        Register address: 262; U16
        Function-Code: 0x06
        Unit: A
        """
        if fs_current > 16.0:
            # bound value to max of 16.0 A
            fs_current = 16.0
        elif fs_current < 6.0:
            print (f'Input ({fs_current}) is bound to 0 A, due to HW restriction < 6.0 A')
        _fs_current = int(fs_current * 10)
        result = self.write_register(262, _fs_current)
        #print(f'[262]\t\tFailSafe Current set to : {self.get_failsafe_current_config()}', end='\n\n')
        return result
