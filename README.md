# Heidelberg-Energy-Control-ModbusRTU
python solution for connecting the Heidelberg-EnergyControl Wallbox via ModbusRTU


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
    
>Remark: for pymodbus use minimum the version of 3.6.x

## Usage
Check the python code in the script `HD_EnergyControl_ModbusRTU.py` and change the settings if necessary.<br>
Then you can check the communucation via:

```
python3 HD_EnergyControl_ModbusRTU.py
```

# License
This library is licensed under MIT Licence.

# Helpful Links
* [ESP8266-01-Adapter](https://esp8266-01-adapter.de)
