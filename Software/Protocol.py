# Copyright (C) 2018 Silicon Laboratories, Inc.
# http://developer.silabs.com/legal/version/v11/Silicon_Labs_Software_License_Agreement.txt
#
# This file is part of Oscilloscope Simulation System.
#
# Oscilloscope Simulation System is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Oscilloscope Simulation System is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Oscilloscope Simulation System.  If not, see <http://www.gnu.org/licenses/>.
from enum import Enum


class Protocol(Enum):
    PREAMBLE_BYTE = 0
    COMMAND_BYTE = 1
    VALUE_LENGTH_BYTE = 2
    VALUE_BYTE0 = 3
    VALUE_BYTE1 = 4

    PREAMBLE = '\xAA'
    ENABLE_CHANNEL = '\xf1'
    ENABLE_ADC = '\xf2'
    ADC_GET = '\x01'
    CHANNEL1_VALUE = '\x02'
    CHANNEL2_VALUE = '\x03'
    LED_GET = '\x11'
    LED_STATE = '\x12'
    LED_SET = '\x13'
    GPIO_GET = '\x21'
    GPIO_STATE = '\x22'
    GPIO_SET = '\x23'
    BUTTON_EVENT = '\x31'
    FREQUENCY_GET = '\x41'
    FREQUENCY_STATE = '\x42'
    FREQUENCY_SET = '\x43'
    ACCURACY_GET = '\x51'
    ACCURACY_STATE = '\x52'
    ACCURACY_SET = '\x53'

    CHANNEL1 = '\x01'
    CHANNEL2 = '\x02'

    ENABLE = '\x01'
    DISABLE = '\x00'

    LED_RED = '\x01'
    LED_GREEN = '\x02'
    LED_BLUE = '\03'
    LED_ON = '\x01'
    LED_OFF = '\x00'

    FREQUENCY_4HZ = '\x00'
    FREQUENCY_10HZ = '\x01'
    FREQUENCY_100HZ = '\x02'
    FREQUENCY_1000HZ = '\x03'
