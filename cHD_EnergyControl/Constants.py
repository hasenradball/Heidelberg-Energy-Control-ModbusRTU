""""Constants Module for the HD Energy Control"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-

class HdEcConstants:
    """Constants for use with pymodbus
    """
    TYPE_TO_LENGTH = {'U8': 1, 'U16': 1, 'U32': 2, 'U64': 4, \
                      'S8': 1, 'S16': 1, 'S32': 2, 'S64': 4}

    STATE = {2: 'A1', 3: 'A2', 4: 'B1', \
             5: 'B2', 6: 'C1', 7: 'C2', \
             8: '--', 9: 'E', 10: 'F', 11: '--'}

    CAR = {2: 'No vehicle plugged',
           3: 'No vehicle plugged',
           4: 'Vehicle plugged without charging request',
           5: 'Vehicle plugged without charging request',
           6: 'Vehicle plugged with charging request',
           7: 'Vehicle plugged with charging request',
           8: '--',
           9: 'Error',
           10: '--',
           11: '--'}

    WALLBOX = {2: 'Wallbox does not allow charging', \
               3: 'Wallbox allow charging', \
               4: 'Wallbox does not allow charging', \
               5: 'Wallbox allow charging', \
               6: 'Wallbox does not allow charging', \
               7: 'Wallbox allow charging', \
               8: 'Derating', \
               9: 'Error', \
               10: 'Wallbox locked or not ready', \
               11: 'Error'}
    
    STANDBY_FUNCTION = {0: 'enable StandBy Function', \
                        4: 'disable StandBy Function'}
