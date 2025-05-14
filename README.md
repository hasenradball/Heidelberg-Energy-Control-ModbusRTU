# Heidelberg-Energy-Control-ModbusRTU
python solution for connecting the Heidelberg-EnergyControl Wallbox via ModbusRTU

![HD_Engery_Control](./docs/HD_EnergyControl.jpg)

## Contents
* [Prerecquisites](#prerecquisites)
* [Usage](#usage)
* [License](#license)
* [Helpful Links](#helpful-links)

## Prerecquisites
1) For the use of this python code it is necessary to install the python libs `pymodbus` and `pyserial`:

```
python3 -m pip install pymodbus
python3 -m pip install pyserial
```
>Remark: for pymodbus use minimum the version of 3.9.2, tested with pymodus==3.9.2

## Usage
Check the python code in the script `hd_energy_control_modbus_rtu.py`.<br>
Change the following line according to your serial device.

```
obj = HDEnergyControl("/dev/ttyAMA0", 1)
```
The HD_EngeryControl constructor takes two arguments:
- **port** - where the wall box is connected to (default "/dev/ttyAMA0")
- **UnitID** - the unit id in the bus (default 1)

Then you can check the communucation via:

```
python3 HD_EnergyControl_ModbusRTU.py
```

# License
This library is licensed under MIT Licence.

# Helpful Links
* [ESP8266-01-Adapter](https://esp8266-01-adapter.de)
