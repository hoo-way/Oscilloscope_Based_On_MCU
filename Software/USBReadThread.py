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
from PySide2.QtCore import QThread, Signal
from CanvasFrame import CanvasFrame
from Protocol import Protocol
import logging
import copy
import threading

ADCVALUEMAX = 3300
Channel1ListMAX = 10000
Channel2ListMAX = 10000


class USBReadThread(QThread):

    bitMode = 8
    redLed = 0
    greenLed = 0
    blueLed = 0
    triggerEnable = 0
    triggerValue = 0

    updateWaveForm = Signal(str)
    updateFrequency = Signal(int)
    singleTrigger = Signal(str)

    def __init__(self, device):
        QThread.__init__(self)
        self.ADCPointList = []
        self.device = device

        self.canvas = CanvasFrame()
        self.oldChannel1Value = -1
        self.oldChannel2Value = -1

        self.frequency = 1000
        self.dataList = []
        self.dataListLen = 0
        self.rxLen = 0
        self.rxData = 0
        self.dataList_t = 0
        self.dataByteAmount = 0
        self.channel = 0
        self.dataH = 0
        self.dataL = 0
        self.data = 0
        self.triggerTimer = 0
        self.oldChannel1Value = 0

    def run(self, *args, **kwargs):
        while True:

            self.dataList = []

            self.rxLen, self.rxData = self.device.read(4096)
            # print "rxdata", self.rxLen, self.rxData.encode('hex')

            self.dataList = list(self.rxData)

            self.dataListLen = len(self.dataList)

            if self.dataListLen < 3:
                logging.warning("received data too short:" + str(self.dataListLen))
                continue

            if self.dataList[Protocol.PREAMBLE_BYTE.value].encode('hex') != Protocol.PREAMBLE.value.encode('hex'):
                logging.error("Start byte error: expected:0xaa, received: "
                              + self.dataList[Protocol.PREAMBLE_BYTE.value].encode('hex'))
                continue

            self.dataByteAmount = ord(self.dataList[Protocol.VALUE_LENGTH_BYTE.value])

            if self.dataByteAmount < self.dataListLen - 3:
                logging.error("receive length doesn't match:" + str(self.dataList))
                self.dataList_t = copy.deepcopy(self.dataList)
                while True:
                    del self.dataList[:]
                    self.dataList = copy.copy(self.dataList_t[0:self.dataByteAmount + 3])
                    self.parse_command()
                    del self.dataList_t[0:self.dataByteAmount + 3]
                    if len(self.dataList_t) < 3:
                        logging.warning("received data too short:" + str(self.dataListLen))
                        break
                    if self.dataList[Protocol.PREAMBLE_BYTE.value].encode('hex') \
                            != Protocol.PREAMBLE.value.encode('hex'):
                        break
                    self.dataByteAmount = ord(self.dataList[Protocol.VALUE_LENGTH_BYTE.value])
                    if self.dataByteAmount > self.dataListLen - 3:
                        break

                continue

            self.parse_command()

    def parse_command(self):
        if ord(self.dataList[Protocol.COMMAND_BYTE.value]) == ord(Protocol.CHANNEL1_VALUE.value)\
                or ord(self.dataList[Protocol.COMMAND_BYTE.value]) == ord(Protocol.CHANNEL2_VALUE.value):
            self.channel = ord(self.dataList[Protocol.COMMAND_BYTE.value]) - 1
            for i in range(0, self.dataByteAmount - 1, 2):
                self.dataH = ord(self.dataList[i+Protocol.VALUE_BYTE0.value])
                self.dataL = ord(self.dataList[i+Protocol.VALUE_BYTE1.value])
                self.data = self.dataH * 256 + self.dataL
                # print "data:", self.dataH, self.dataL, self.data
                if self.data > ADCVALUEMAX:
                    logging.error("receive adc value is bigger than max voltage:" + str(self.data))
                if self.channel == 1:
                    self.canvas.Channel1List.append(self.data)
                else:
                    self.canvas.Channel2List.append(self.data)
                if self.triggerEnable:
                    if self.channel == 1:
                        if self.oldChannel1Value == -1:
                            self.oldChannel1Value = self.data
                            continue
                        if (self.data > self.triggerValue and self.triggerValue > self.oldChannel1Value) \
                                or (self.data < self.triggerValue and self.triggerValue < self.oldChannel1Value):
                            self.triggerTimer = threading.Timer(400 / float(self.frequency), self.trigger_timer_event)
                            self.triggerTimer.start()

                        self.oldChannel1Value = self.data
                    else:
                        if self.oldChannel2Value == -1:
                            self.oldChannel2Value = self.data
                            continue
                        if (self.data > self.triggerValue and self.triggerValue > self.oldChannel2Value) \
                                or (self.data < self.triggerValue and self.triggerValue < self.oldChannel2Value):
                            self.triggerTimer = threading.Timer(400 / float(self.frequency), self.trigger_timer_event)
                            self.triggerTimer.start()
                        self.oldChannel2Value = self.data

            if self.channel == 1:
                if len(self.canvas.Channel1List) > Channel1ListMAX:
                    self.delete_channel1_list()
            else:
                if len(self.canvas.Channel2List) > Channel2ListMAX:
                    self.delete_channel2_list()

            self.updateWaveForm.emit("ok")
        elif ord(self.dataList[Protocol.COMMAND_BYTE.value]) == ord(Protocol.FREQUENCY_STATE.value):
            self.frequency = ord(self.dataList[Protocol.VALUE_BYTE0.value])
            if self.frequency == ord(Protocol.FREQUENCY_4HZ.value):
                self.frequency = 4
            elif self.frequency == ord(Protocol.FREQUENCY_10HZ.value):
                self.frequency = 10
            elif self.frequency == ord(Protocol.FREQUENCY_100HZ.value):
                self.frequency = 100
            elif self.frequency == ord(Protocol.FREQUENCY_1000HZ.value):
                self.frequency = 1000
            else:
                self.frequency = 0
                logging.error("error:get error frequency")
            self.updateFrequency.emit(self.frequency)

        elif ord(self.dataList[Protocol.COMMAND_BYTE.value]) == ord(Protocol.ACCURACY_STATE.value):
            self.bitMode = ord(self.dataList[Protocol.VALUE_BYTE0.value])

        else:
            logging.error("received wrong command:" + str(ord(self.dataList[Protocol.COMMAND_BYTE.value])))

    def delete_channel1_list(self):
        del self.canvas.Channel1List[0:len(self.canvas.Channel1List) - Channel1ListMAX]

    def delete_channel2_list(self):
        del self.canvas.Channel2List[0:len(self.canvas.Channel2List) - Channel2ListMAX]

    def trigger_timer_event(self):
        self.singleTrigger.emit("ok")
