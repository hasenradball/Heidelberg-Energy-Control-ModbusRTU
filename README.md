# Heidelberg-Energy-Control-ModbusRTU
[![Spell Check](https://github.com/hasenradball/Heidelberg-Energy-Control-ModbusRTU/actions/workflows/spell_checker.yml/badge.svg)](https://github.com/hasenradball/Heidelberg-Energy-Control-ModbusRTU/actions/workflows/spell_checker.yml)

python solution for connecting the Heidelberg-EnergyControl Wallbox via ModbusRTU

![HD_Engery_Control](docs/HD_EnergyControl.jpg)

## Contents
* [Prerecquisites](#prerecquisites)
* [Installation Steps](#installation-steps)
* [Library Installation](#library-installation)
* [Library Usage](#library-usage)
* [License](#license)
* [Helpful Links](#helpful-links)

## Prerecquisites
1. For this library you need python3
2. For the use of this python code it is necessary to install the python libs:
    - `pymodbus v3.12.1`
    - `pyserial`
> Remark: for `pymodbus` use the minimum version of 3.12.x, testetd with pymodbus==3.12.1

## Installation steps
### Make python ready to use
1. Create a python3 virtual environment in your home folder, see:<br>
[https://docs.python.org/3/library/venv.html](https://docs.python.org/3/library/venv.html)

```
python -m venv ~/my_python_venvs
```
2. Install the needed python packages

> the pymodbus documentation you will find here:<br>
[https://pymodbus.readthedocs.io/en/v3.12.1/](https://pymodbus.readthedocs.io/en/v3.12.1/)

```
~/my_python_venvs/bin/python -m pip install pymodbus==3.12.1
~/my_python_venvs/bin/python -m pip install pyserial
```
You can check the state by:

```
~/my_python_venvs/bin/python -m pip list
```

```
~/my_python_venvs/bin/python -m pip install pymodbus==3.12.1
~/my_python_venvs/bin/python -m pip install pyserial
```
You can check the state by:

```
~/my_python_venvs/bin/python -m pip list
```

## Library Installation
Install the library from github.<br>
Lets assume you want to install it in the following path: `~/git_repos`
```
cd ~
mkdir git_repos
cd git_repos
git clone https://github.com/hasenradball/Heidelberg-Energy-Control-ModbusRTU.git
```
## Usage
Check the python code in the script `hd_energy_control_modbus_rtu.py`.<br>
Change the following line according to your serial device.

```
obj = HDEnergyControl("/dev/ttyAMA0", 1)
```
The HD_EngeryControl constructor takes two arguments:
- **port** - where the wall box is connected to (default "/dev/ttyAMA0")
- **UnitID** - the unit id in the bus (default 1)

### Check the Communication
After updated you can check the communication.

```
cd /path/to/your/installation/folder

~/my_python_venvs/bin/python HD_EnergyControl_ModbusRTU.py
```

## Usage of systemd service
to use the python code via systemd service follow the following instructions.

a) create a file in folder `/etc/systemd/system` like `wallbox.service`

b) copy the following content inside the service file

c) reload the daemon `sudo systemctl daemon-reload`

d) enable and start the service:
```
sudo systemctl start wallbox.service
sudo systemctl enable wallbox.service
```

```
[Unit]
Description=Wallbox Kommunication Service
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
User=frank
Group=frank

ExecStart=/home/frank/senv/bin/python /usr/local/bin/python/Heidelberg_EnergyControl/send_maxSystemCurrent_service.py

StandardOutput=null
StandardError=journal

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```


# License
This library is licensed under MIT Licence.

# Helpful Links
* [ESP8266-01-Adapter](https://esp8266-01-adapter.de)
