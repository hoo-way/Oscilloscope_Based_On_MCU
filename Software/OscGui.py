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
from PySide2 import QtWidgets
from PySide2.QtWidgets import QWidget, QDesktopWidget, QPushButton, QLabel, QSpinBox
from PySide2.QtGui import QIcon, QFont
from PySide2.QtCore import QSize
from CanvasFrame import CanvasFrame
from USBReadThread import USBReadThread
from USBWriteThread import USBWriteThread
from Protocol import Protocol
import logging


class OscGui(QWidget):
    triggerEnable = 0
    ADCEnable = 0

    def __init__(self, device):
        QWidget.__init__(self)
        self.setWindowIcon(QIcon("icon/silabslogo.png"))

        self.device = device
        screen = QDesktopWidget()
        self.m_width = screen.width()
        self.m_height = screen.height()
        self.resize(self.m_width, self.m_height)
        self.showMaximized()

        self.setWindowTitle("Silabs")
        self.setObjectName("mainWindow")
        self.setStyleSheet("#mainWindow{background-color:rgb(54, 56, 60);}")

        self.layout = QtWidgets.QHBoxLayout()
        self.layout.setContentsMargins(self.m_width/200, self.m_width/200, self.m_width/200, self.m_width/20)
        self.layout.setSpacing(10)

        self.create_left_frame()
        self.create_right_frame()

        self.layout.setStretch(0, 3)
        self.layout.setStretch(1, 1)

        self.setLayout(self.layout)

        if self.device:
            logging.debug("device name:" + str(self.device))
            self.readThread = USBReadThread(self.device)
            self.readThread.updateWaveForm.connect(self.update_canvas)
            self.readThread.updateFrequency.connect(self.update_frequency)
            self.readThread.singleTrigger.connect(self.single_trigger_event)
            self.readThread.start()

            self.frequencyGet = Protocol.PREAMBLE.value \
                + Protocol.FREQUENCY_GET.value \
                + '\x00'  # '\xAA' + '\x41' + '\x00'
            self.setThread = USBWriteThread(self.device, self.frequencyGet)
            self.setThread.start()

    def create_left_frame(self):
        self.leftlayout = QtWidgets.QVBoxLayout()
        self.leftlayout.setContentsMargins(self.m_width/200, self.m_width/200, self.m_width/200, self.m_width/200)

        self.canvasFrame = CanvasFrame()
        # self.canvasFrame.setFrameStyle(QtWidgets.QFrame.StyledPanel | QtWidgets.QFrame.Plain)
        self.canvasFrame.setStyleSheet("border-radius:10px;background-color:rgb(40, 38, 39);")
        self.leftlayout.addWidget(self.canvasFrame)

        self.navigationBarFrame = QtWidgets.QFrame()
        self.navigationBarFrame.setObjectName("NBF")
        self.navigationBarFrame.setStyleSheet("#NBF{border-radius:10px;"
                                              "background-color:rgb(200, 200, 200);}")
        self.navigationBarLayout = QtWidgets.QVBoxLayout(self.navigationBarFrame)
        self.playBarLayout = QtWidgets.QHBoxLayout(self.navigationBarFrame)
        self.playBarLayout.setSpacing(self.m_width/40)

        self.playBarLayout.addStretch(1)

        self.zoomInButton = QtWidgets.QPushButton()
        self.zoomInButton.setObjectName("zoomInButton")
        self.zoomInButton.setMaximumSize(self.m_width/40, self.m_width/40)
        self.zoomInButton.setMinimumSize(self.m_width/40, self.m_width/40)
        self.zoomInButton.setStyleSheet("QPushButton{border-radius:25px;"
                                        "border-image:url(icon/ZoomIn.png);}"
                                        "QPushButton:hover{border-radius:25px;"
                                        "border-image:url(icon/ZoomIn2.png);"
                                        "background-colora:rgb(50, 50, 50,0);}")

        self.zoomInButton.clicked.connect(self.zoom_in_event)
        self.playBarLayout.addWidget(self.zoomInButton)

        self.zoomOutButton = QtWidgets.QPushButton()
        self.zoomOutButton.setObjectName("zoomOutButton")
        self.zoomOutButton.setMaximumSize(self.m_width/40, self.m_width/40)
        self.zoomOutButton.setMinimumSize(self.m_width/40, self.m_width/40)
        self.zoomOutButton.setIcon(QIcon("icon/ZoomOut.png"))
        self.zoomOutButton.setIconSize(QSize(self.m_width/40, self.m_width/40))
        self.zoomOutButton.setStyleSheet("QPushButton{border-radius:%dpx;}"
                                         "QPushButton:hover{border:1 solid red;"
                                         "border-radius:%dpx;"
                                         "background-color:rgb(250, 100, 100);}" % (self.m_width/80, self.m_width/80))
        self.zoomOutButton.clicked.connect(self.zoom_out_event)
        self.playBarLayout.addWidget(self.zoomOutButton)

        self.playButton = QtWidgets.QPushButton()
        self.playButton.setObjectName("playButton")
        self.playButton.setFixedSize(self.m_width/20, self.m_width/20)
        # self.playButton.setStyleSheet("border-radius:%dpx;" % self.m_width/40)
        self.playButton.setStyleSheet("QPushButton{border:none;"
                                      "border-radius:%dpx;"
                                      "background-color:""rgb(200, 100, 100);}"
                                      "QPushButton:hover{border:0;"
                                      "border-radius:%dpx;"
                                      "background-color:rgb(250, 100, 100);}" % (self.m_width / 40, self.m_width / 40))
        self.playButton.clicked.connect(self.play_button_event)
        self.playBarLayout.addWidget(self.playButton)

        self.triggerLayout = QtWidgets.QHBoxLayout(self.navigationBarFrame)
        self.triggerLayout.setContentsMargins(0, 0, 0, 0)
        self.triggerLayout.setSpacing(1)

        self.triggerEnable = 0
        self.triggerButton = QtWidgets.QPushButton(self.navigationBarFrame)
        # self.triggerButton.setObjectName("triggerButton")
        self.triggerButton.setFixedSize(self.m_width/12, self.m_height/20)
        self.triggerButton.setFont(QFont("New Time Roman", 10))
        self.triggerButton.setText("Single Trigger")
        self.triggerButton.setStyleSheet("QPushButton{border-top-left-radius:5px;"
                                         "border-bottom-left-radius: 5px;"
                                         "background-color:rgba(100, 100, 100,255);"
                                         "color:rgb(200, 200, 200);}"
                                         "QPushButton:hover{color: rgb(100, 200, 100);font-weight:bold}")
        self.triggerButton.clicked.connect(self.trigger_event)
        self.triggerLayout.addWidget(self.triggerButton)

        self.triggerValue = 0
        self.triggerSpinBox = QSpinBox(self.navigationBarFrame)
        self.triggerSpinBox.setFixedSize(self.m_width/10, self.m_height/20)
        self.triggerSpinBox.setMaximum(3300)
        self.triggerSpinBox.setMinimum(1)
        self.triggerSpinBox.setFont(QFont("New Time Roman", 10))
        self.triggerSpinBox.setStyleSheet("QSpinBox{border-top-right-radius:5px;"
                                          "border-bottom-left-right: 5px;"
                                          "background-color:rgb(100, 100, 100);"
                                          "color:rgb(200, 200, 200);}"
                                          "QSpinBox:drop{subcontrol-origin: padding;"
                                          "subcontrol-position: top right;"
                                          "width: 50px;border-left-style:solid;"
                                          "border-top-right-radius: 3px;"
                                          "border-bottom-right-radius: 3px;"
                                          "border-left: 2px solid gray;"
                                          "background-color: rgba(100, 25, 100, 0);}")
        self.triggerSpinBox.setMinimumWidth(30)
        self.triggerLayout.addWidget(self.triggerSpinBox)
        self.playBarLayout.addLayout(self.triggerLayout)

        self.playBarLayout.addStretch(1)
        self.navigationBarLayout.addLayout(self.playBarLayout)

        self.navigationBarLine = QtWidgets.QFrame(self.navigationBarFrame)
        self.navigationBarLine.setAutoFillBackground(True)
        self.navigationBarLine.setFixedHeight(1)
        self.navigationBarLine.setStyleSheet("background-color:rgb(150, 150, 150);")
        self.navigationBarLayout.addWidget(self.navigationBarLine)
        # self.navigationBarLayout.addStretch(1)
        self.leftlayout.addWidget(self.navigationBarFrame)
        self.leftlayout.setStretch(0, 5)
        self.leftlayout.setStretch(1, 1)
        self.leftlayout.setStretch(2, 1)
        self.leftlayout.setSpacing(self.m_width/40)
        self.layout.addLayout(self.leftlayout)

    def create_right_frame(self):

        self.rightlayout = QtWidgets.QVBoxLayout()
        self.rightlayout.setContentsMargins(self.m_width/200, self.m_width/200, self.m_width/200, self.m_width/200)

        self.dialogFrame = QtWidgets.QFrame()
        self.dialogFrame.setObjectName("dialogFrame")
        # self.dialogFrame.setAutoFillBackground(True)
        # self.dialogFrame.setStyleSheet("#dialogFrame{border-radius:10px;"
        #                                "background-color:rgb(255, 100, 100);}")
        self.dialogFrame.setStyleSheet("#dialogFrame{border-radius:10px;"
                                       "background-color:rgb(10, 10, 10);}")
        self.dialoglayout = QtWidgets.QVBoxLayout(self.dialogFrame)
        self.dialoglayout.setContentsMargins(0, self.m_width/40, 0, self.m_width/40)  # left, top, right, bottom
        self.dialoglayout.setSpacing(self.m_width/40)
        self.dialoglayout.addStretch(2)

        self.ledLayout = QtWidgets.QHBoxLayout(self.dialogFrame)

        self.ledLayout.addStretch(1)

        self.redLedState = 0
        self.redLedSwitch = QtWidgets.QPushButton(self.dialogFrame)
        self.redLedSwitch.setObjectName("redLedSwitch")
        self.redLedSwitch.setIcon(QIcon("icon/switchOFF.png"))
        self.redLedSwitch.setIconSize(QSize(self.m_width/40, self.m_width/40/1.75))
        self.redLedSwitch.setFixedSize(self.m_width/40, self.m_width/40/1.75)
        self.redLedSwitch.setStyleSheet("#redLedSwitch{border:none;}")
        self.redLedSwitch.clicked.connect(self.red_led_switch_event)
        self.ledLayout.addWidget(self.redLedSwitch)

        self.ledLayout.addStretch(1)

        self.greenLedState = 0
        self.greenLedSwitch = QtWidgets.QPushButton(self.dialogFrame)
        self.greenLedSwitch.setObjectName("greenLedSwitch")
        self.greenLedSwitch.setIcon(QIcon("icon/switchOFF.png"))
        self.greenLedSwitch.setIconSize(QSize(self.m_width/40, self.m_width/40/1.75))
        self.greenLedSwitch.setFixedSize(self.m_width/40, self.m_width/40/1.75)
        self.greenLedSwitch.setStyleSheet("#greenLedSwitch{border:none;}")
        self.greenLedSwitch.clicked.connect(self.green_led_switch_event)
        self.ledLayout.addWidget(self.greenLedSwitch)

        self.ledLayout.addStretch(1)

        self.blueLedState = 0
        self.blueLedSwitch = QtWidgets.QPushButton(self.dialogFrame)
        self.blueLedSwitch.setObjectName("blueLedSwitch")
        self.blueLedSwitch.setIcon(QIcon("icon/switchOFF.png"))
        self.blueLedSwitch.setIconSize(QSize(self.m_width/40, self.m_width/40/1.75))
        self.blueLedSwitch.setFixedSize(self.m_width/40, self.m_width/40/1.75)
        self.blueLedSwitch.setStyleSheet("#blueLedSwitch{border:none;}")
        self.blueLedSwitch.clicked.connect(self.blue_led_switch_event)
        self.ledLayout.addWidget(self.blueLedSwitch)

        self.ledLayout.addStretch(1)
        self.dialoglayout.addLayout(self.ledLayout)

        self.dialoglayout.addStretch(1)

        self.dialogLine = QtWidgets.QFrame(self.dialogFrame)
        self.dialogLine.setAutoFillBackground(True)
        self.dialogLine.setFixedHeight(1)
        self.dialogLine.setStyleSheet("background-color:rgb(50, 50, 50);")
        self.dialoglayout.addWidget(self.dialogLine)

        self.channelLayout = QtWidgets.QHBoxLayout(self.dialogFrame)
        self.channelLayout.setSpacing(0)
        self.channelLayout.setContentsMargins(self.m_width/100, 0, self.m_width/100, 0)
        # self.channelLayout.addStretch(1)

        self.channel1Enable = 0
        self.channel1Button = QPushButton(self.dialogFrame)
        self.channel1Button.setFixedHeight(self.m_width/40)
        self.channel1Button.setStyleSheet("QPushButton{border:1px solid rgb(200,200,200);"
                                          "border-top-left-radius:5px;"
                                          "border-bottom-left-radius: 5px;"
                                          "background-color:rgba(100, 100, 100,0);"
                                          "color:rgb(200, 200, 200);"
                                          "padding: 1px 20px;}"
                                          "QPushButton:hover{font-weight:bold;}")
        self.channel1Button.setFont(QFont("New Time Roman", 10))
        self.channel1Button.setText("Channel_1")
        self.channel1Button.clicked.connect(self.channel1_button_event)
        self.channelLayout.addWidget(self.channel1Button)

        self.channel2Enable = 0
        self.channel2Button = QPushButton(self.dialogFrame)
        self.channel2Button.setFixedHeight(self.m_width/40)
        self.channel2Button.setStyleSheet("QPushButton{border:1px solid rgb(200,200,200);"
                                          "border-top-right-radius: 5px;"
                                          "border-bottom-right-radius:5px;"
                                          "background-color:rgba(100, 100, 100,0);"
                                          "color:rgb(200, 200, 200);"
                                          "padding: 1px 20px;}"
                                          "QPushButton:hover{font-weight:bold;}")
        self.channel2Button.setFont(QFont("New Time Roman", 10))
        self.channel2Button.setText("Channel_2")
        self.channel2Button.clicked.connect(self.channel2_button_event)
        self.channelLayout.addWidget(self.channel2Button)
        # self.channelLayout.addStretch(1)

        self.dialoglayout.addLayout(self.channelLayout)

        self.dialogLine2 = QtWidgets.QFrame(self.dialogFrame)
        self.dialogLine2.setAutoFillBackground(True)
        self.dialogLine2.setFixedHeight(1)
        self.dialogLine2.setStyleSheet("background-color:rgb(50, 50, 50);")
        self.dialoglayout.addWidget(self.dialogLine2)

        self.configutatorLayout = QtWidgets.QVBoxLayout(self.dialogFrame)
        self.configutatorLayout.setContentsMargins(20, 0, 20, 0)
        self.configutatorLayout.setSpacing(self.m_width/100)

        self.frenquencyComboBox = QtWidgets.QComboBox()
        self.frenquencyComboBox.setObjectName("frenquencyComboBox")
        self.frenquencyComboBox.setFixedHeight(self.m_width/40)
        self.frenquencyComboBox.setFont(QFont("New Time Roman", 10))
        self.frenquencyComboBox.setStyleSheet("QComboBox{border-radius:5px;"
                                              "background-color:rgb(200, 200, 200);"
                                              "color:rgb(0, 0, 0);"
                                              "padding: 1px 20px;}"
                                              "QComboBox:drop-down{subcontrol-origin: padding;"
                                              "subcontrol-position: top right;"
                                              "width: 50px;border-left-style:solid;"
                                              "border-top-right-radius: 3px;"
                                              "border-bottom-right-radius: 3px;"
                                              "border-left: 2px solid gray;"
                                              "background-color: rgba(100, 100, 100, 0);}"
                                              "QComboBox:down-arrow{border-image:url(icon/arrow-1.png);}"
                                              )
        self.frenquencyComboBox.addItem("4Hz")
        self.frenquencyComboBox.addItem("10Hz")
        self.frenquencyComboBox.addItem("100Hz")
        self.frenquencyComboBox.addItem("1000Hz")
        self.frenquencyComboBox.setCurrentText("1000Hz")
        self.frenquencyComboBox.setFont(QFont("New Time Roman", 10))

        self.configutatorLayout.addWidget(self.frenquencyComboBox)

        self.setButton = QPushButton(self.dialogFrame)
        self.setButton.setObjectName("setButton")
        self.setButton.setFixedHeight(self.m_width/40)
        self.setButton.setStyleSheet("QPushButton{border-radius:%dpx;"
                                     "background-color:rgb(150, 255, 150);"
                                     "color:rgb(0, 0, 0);"
                                     "text-align: center center;}"
                                     "QPushButton:hover{background-color:"
                                     "rgb(100, 255, 100);color:rgb(255, 100, 100);"
                                     "font-size:20px}" % (self.m_width/80))
        self.setButton.setFont(QFont("New Time Roman", 12, QFont.Bold))
        self.setButton.setText("set")
        self.setButton.clicked.connect(self.set_button_event)
        self.setButton.setEnabled(True)
        self.configutatorLayout.addWidget(self.setButton)

        self.dialoglayout.addLayout(self.configutatorLayout)
        self.dialoglayout.addStretch(1)

        self.rightlayout.addWidget(self.dialogFrame)

        self.stateFrame = QtWidgets.QFrame()
        self.stateFrame.setObjectName("stateFrame")
        # self.dialogFrame.setAutoFillBackground(True)
        self.stateFrame.setStyleSheet("QFrame{border:2px solid rgb(200, 200, 200);"
                                      "border-radius:10px;"
                                      "background-color:rgb(200, 200, 200);}")
        self.statelayout = QtWidgets.QGridLayout(self.stateFrame)
        self.statelayout.setContentsMargins(self.m_width/40, self.m_width/40, self.m_width/40, self.m_width/40)
        self.enableLabelKey = QLabel(self.stateFrame)
        self.enableLabelKey.setText("state:")
        self.enableLabelKey.setFont(QFont("New Time Roman", 10, QFont.Bold))
        self.statelayout.addWidget(self.enableLabelKey, 0, 0)
        self.enableLabelValue = QLabel(self.stateFrame)
        self.enableLabelValue.setText("Stop")
        self.enableLabelValue.setFont(QFont("New Time Roman", 10, QFont.Bold))
        self.statelayout.addWidget(self.enableLabelValue, 0, 1)

        self.frequencyLabelKey = QLabel(self.stateFrame)
        self.frequencyLabelKey.setText("frequency:")
        self.frequencyLabelKey.setFont(QFont("New Time Roman", 10, QFont.Bold))
        self.statelayout.addWidget(self.frequencyLabelKey, 1, 0)
        self.frequencyLabelValue = QLabel(self.stateFrame)
        self.frequencyLabelValue.setText(str(self.canvasFrame.frequency) + "Hz")
        self.frequencyLabelValue.setFont(QFont("New Time Roman", 10, QFont.Bold))
        self.statelayout.addWidget(self.frequencyLabelValue, 1, 1)

        self.bitModeLabelKey = QLabel(self.stateFrame)
        self.bitModeLabelKey.setText("BitMode:")
        self.bitModeLabelKey.setFont(QFont("New Time Roman", 10, QFont.Bold))
        self.statelayout.addWidget(self.bitModeLabelKey, 2, 0)
        self.bitModeLabelValue = QLabel(self.stateFrame)
        self.bitModeLabelValue.setText("8 bit")
        self.bitModeLabelValue.setFont(QFont("New Time Roman", 10, QFont.Bold))
        self.statelayout.addWidget(self.bitModeLabelValue, 2, 1)

        self.rightlayout.addWidget(self.stateFrame)

        self.rightlayout.addStretch(1)

        self.layout.addLayout(self.rightlayout)

    def trigger_event(self):
        if self.device is None:
            logging.error("no device!!!")
            return
        if self.triggerEnable:
            self.triggerButton.setStyleSheet("QPushButton{border-top-left-radius:5px;"
                                             "border-bottom-left-radius: 5px;"
                                             "background-color:rgba(100, 100, 100,255);}"
                                             "QPushButton:hover{color: rgb(100, 200, 100);font-weight:bold}")
            self.triggerEnable = 0
            self.triggerValue = 0
            self.readThread.triggerEnable = 0
            self.readThread.triggerValue = 0
            self.triggerSpinBox.setEnabled(True)
            self.triggerSpinBox.setStyleSheet("QSpinBox{border-top-right-radius:5px;"
                                              "border-bottom-left-right: 5px;"
                                              "background-color:rgb(100, 100, 100);"
                                              "color:rgb(200, 200, 200);}")

        else:
            self.triggerButton.setStyleSheet("QPushButton{border:1px solid rgb(200,200,200);"
                                             "border-top-left-radius:5px;"
                                             "border-bottom-left-radius: 5px;"
                                             "background-color:rgba(100, 200, 100);}"
                                             "QPushButton:hover{color: rgb(100, 100, 100);font-weight:bold}")
            self.triggerEnable = 1
            self.triggerValue = self.triggerSpinBox.value()
            self.readThread.triggerEnable = 1
            self.readThread.triggerValue = self.triggerValue
            self.triggerSpinBox.setEnabled(False)
            self.triggerSpinBox.setStyleSheet("QSpinBox{border-top-right-radius:5px;"
                                              "border-bottom-left-right: 5px;"
                                              "background-color:rgb(150, 150, 150);}")
        logging.debug("triggerButtonEvent:" + str(self.readThread.triggerEnable))

    def zoom_in_event(self):
        if self.canvasFrame.scaleRatio == 1:
            self.canvasFrame.scaleRatio = 1
        else:
            self.canvasFrame.scaleRatio = self.canvasFrame.scaleRatio - 1
        self.canvasFrame.update()
        logging.debug("zoom_in_event, scaleRatio= " + str(self.canvasFrame.scaleRatio))

    def zoom_out_event(self):
        if self.canvasFrame.scaleRatio > 5:
            self.canvasFrame.scaleRatio = 6
        else:
            self.canvasFrame.scaleRatio = self.canvasFrame.scaleRatio + 1
        self.canvasFrame.update()
        logging.debug("zoom_out_event, scaleRatio= " + str(self.canvasFrame.scaleRatio))

    def play_button_event(self):
        logging.debug("playButtonEvent")
        if self.device is None:
            logging.error("no device!!!")
            return

        if self.ADCEnable:
            self.channel1Button.setEnabled(True)
            self.channel2Button.setEnabled(True)
            self.playButton.setStyleSheet("QPushButton{border-radius:%dpx;"
                                          "background-color:rgb(200, 100, 100);}"
                                          "QPushButton:hover{border:0;"
                                          "border-radius:%dpx;"
                                          "background-color:rgb(250, 100, 100);}" % (self.m_width/40, self.m_width/40))
            self.command = Protocol.PREAMBLE.value \
                + Protocol.ENABLE_ADC.value \
                + '\x01' \
                + Protocol.DISABLE.value  # '\xAA'+'\xF1'+'\x01'+'\x00'
            self.playthread = USBWriteThread(self.device, self.command)
            self.playthread.start()
            self.ADCEnable = 0
            self.enableLabelValue.setText("Stop")
            self.setButton.setStyleSheet("QPushButton{border-radius:%dpx;"
                                         "background-color:rgb(150, 255, 150);"
                                         "color:rgb(0, 0, 0);"
                                         "text-align: center center;}"
                                         "QPushButton:hover{background-color:rgb(100, 255, 100);"
                                         "color:rgb(255, 100, 100);"
                                         "font-size:20px;}" % (self.m_width/80))
            self.setButton.setEnabled(True)

            self.canvasFrame.dragEnable = True
        else:
            if self.channel1Enable == 0 and self.channel2Enable == 0:
                return

            if self.canvasFrame.frequency == 1000:
                self.freq = Protocol.FREQUENCY_1000HZ.value
            elif self.canvasFrame.frequency == 100:
                self.freq = Protocol.FREQUENCY_100HZ.value
            elif self.canvasFrame.frequency == 10:
                self.freq = Protocol.FREQUENCY_10HZ.value
            elif self.canvasFrame.frequency == 4:
                self.freq = Protocol.FREQUENCY_4HZ.value
            else:
                self.freq = Protocol.FREQUENCY_1000HZ.value

            self.frequencyCommand = Protocol.PREAMBLE.value \
                + Protocol.FREQUENCY_SET.value \
                + '\x01' \
                + self.freq  # '\xAA' + '\x43' + '\x01' + '\x03'
            self.frequencyThread = USBWriteThread(self.device, self.frequencyCommand)
            self.frequencyThread.start()

            self.channel1Button.setEnabled(False)
            self.channel2Button.setEnabled(False)
            self.playButton.setStyleSheet("QPushButton{border-radius:%dpx;"
                                          "background-color:rgb(100, 200, 100);}"
                                          "QPushButton:hover{border:0;"
                                          "border-radius:%dpx;"
                                          "background-color:rgb(100, 250, 100);}" % (self.m_width/40, self.m_width/40))
            self.command = Protocol.PREAMBLE.value \
                + Protocol.ENABLE_ADC.value \
                + '\x01' \
                + Protocol.ENABLE.value  # '\xAA'+'\xF1'+'\x01'+'\x01'
            self.playthread = USBWriteThread(self.device, self.command)
            self.playthread.start()
            self.ADCEnable = 1
            self.enableLabelValue.setText("Runing")

            self.setButton.setStyleSheet("QPushButton{border-radius:%dpx;"
                                         "background-color:rgb(150, 150, 150);"
                                         "color:rgb(0, 0, 0);"
                                         "text-align: center center;}" % (self.m_width/80))
            self.setButton.setEnabled(False)
            self.canvasFrame.dragEnable = False
            self.canvasFrame.dragBias = 0
            self.canvasFrame.dragBias_t = 0

    def red_led_switch_event(self):
        if self.device is None:
            logging.error("no device!!!")
            return
        logging.debug("redled is pressed")
        if self.redLedState:
            self.redLedSwitch.setIcon(QIcon("icon/switchOFF.png"))
            self.redLedState = 0
            self.ledCommand = Protocol.PREAMBLE.value \
                + Protocol.LED_SET.value \
                + '\x02' \
                + Protocol.LED_RED.value \
                + Protocol.LED_OFF.value  # '\xAA' + '\x13' + '\x02' + '\x01' + '\x00'
        else:
            self.redLedSwitch.setIcon(QIcon("icon/switchRedOn.png"))
            self.redLedState = 1
            self.ledCommand = Protocol.PREAMBLE.value \
                + Protocol.LED_SET.value \
                + '\x02' + Protocol.LED_RED.value \
                + Protocol.LED_ON.value  # '\xAA' + '\x13' + '\x02' + '\x01' + '\x01'

        self.ledThread = USBWriteThread(self.device, self.ledCommand)
        self.ledThread.start()

    def green_led_switch_event(self):
        if self.device is None:
            logging.error("no device!!!")
            return
        logging.debug("greenled is pressed")
        if self.greenLedState:
            self.greenLedSwitch.setIcon(QIcon("icon/switchOFF.png"))
            self.greenLedState = 0
            self.ledCommand = Protocol.PREAMBLE.value \
                + Protocol.LED_SET.value \
                + '\x02' \
                + Protocol.LED_GREEN.value \
                + Protocol.LED_OFF.value  # '\xAA' + '\x13' + '\x02' + '\x02' + '\x00'

        else:
            self.greenLedSwitch.setIcon(QIcon("icon/switchGreenOn.png"))
            self.greenLedState = 1
            self.ledCommand = Protocol.PREAMBLE.value \
                + Protocol.LED_SET.value \
                + '\x02' \
                + Protocol.LED_GREEN.value \
                + Protocol.LED_ON.value  # '\xAA' + '\x13' + '\x02' + '\x02' + '\x01'
        self.ledThread = USBWriteThread(self.device, self.ledCommand)
        self.ledThread.start()

    def blue_led_switch_event(self):
        if self.device is None:
            logging.error("no device!!!")
            return
        logging.debug("blueled is pressed")
        if self.blueLedState:
            self.blueLedSwitch.setIcon(QIcon("icon/switchOFF.png"))
            self.blueLedState = 0
            self.ledCommand = Protocol.PREAMBLE.value \
                + Protocol.LED_SET.value \
                + '\x02' \
                + Protocol.LED_BLUE.value \
                + Protocol.LED_OFF.value  # '\xAA' + '\x13' + '\x02' + '\x03' + '\x00'
        else:
            self.blueLedSwitch.setIcon(QIcon("icon/switchBlueOn.png"))
            self.blueLedState = 1
            self.ledCommand = Protocol.PREAMBLE.value \
                + Protocol.LED_SET.value \
                + '\x02' \
                + Protocol.LED_BLUE.value \
                + Protocol.LED_ON.value  # '\xAA' + '\x13' + '\x02' + '\x03' + '\x01'
        self.ledThread = USBWriteThread(self.device, self.ledCommand)
        self.ledThread.start()

    def channel1_button_event(self):
        if self.device is None:
            logging.error("no device!!!")
            return
        if self.channel1Enable:
            del self.canvasFrame.Channel1List[:]
            self.command = Protocol.PREAMBLE.value \
                + Protocol.ENABLE_CHANNEL.value \
                + '\x02' \
                + Protocol.CHANNEL1.value \
                + Protocol.DISABLE.value  # '\xAA'+'\xF1'+'\x01'+'\x00'
            self.channel1thread = USBWriteThread(self.device, self.command)
            self.channel1thread.start()
            self.channel1Enable = 0
            self.canvasFrame.channel1Enable = 0

            self.channel1Button.setStyleSheet("QPushButton{border:1px solid rgb(200,200,200);"
                                              "border-top-left-radius:5px;"
                                              "border-bottom-left-radius: 5px;"
                                              "background-color:rgba(100, 100, 100,0);"
                                              "color:rgb(200, 200, 200);"
                                              "padding: 1px 20px;}"
                                              "QPushButton:hover{font-weight:bold;}")

            logging.debug("channel1 disable")

        else:
            self.command = Protocol.PREAMBLE.value \
                           + Protocol.ENABLE_CHANNEL.value \
                           + '\x02' \
                           + Protocol.CHANNEL1.value \
                           + Protocol.ENABLE.value  # '\xAA'+'\xF1'+'\x01'+'\x00'
            self.channel1thread = USBWriteThread(self.device, self.command)
            self.channel1thread.start()
            self.channel1Enable = 1
            self.canvasFrame.channel1Enable = 1
            self.channel1Button.setStyleSheet("QPushButton{border:1px solid rgb(200,200,200);"
                                              "border-top-left-radius:5px;"
                                              "border-bottom-left-radius: 5px;"
                                              "background-color:rgba(200, 100, 100,255);"
                                              "color:rgb(200, 200, 200);"
                                              "padding: 1px 20px;}"
                                              "QPushButton:hover{font-weight:bold;}")

            logging.debug("channel1 enable")

    def channel2_button_event(self):
        if self.device is None:
            logging.error("no device!!!")
            return
        if self.channel2Enable:
            del self.canvasFrame.Channel2List[:]
            self.command2 = Protocol.PREAMBLE.value \
                + Protocol.ENABLE_CHANNEL.value \
                + '\x02' \
                + Protocol.CHANNEL2.value \
                + Protocol.DISABLE.value  # '\xAA'+'\xF1'+'\x01'+'\x00'
            self.channel2thread = USBWriteThread(self.device, self.command2)
            self.channel2thread.start()
            self.channel2Enable = 0
            self.canvasFrame.channel2Enable = 0
            self.channel2Button.setStyleSheet("QPushButton{border:1px solid rgb(200,200,200);"
                                              "border-top-right-radius:5px;"
                                              "border-bottom-right-radius: 5px;"
                                              "background-color:rgba(100, 100, 100,0);"
                                              "color:rgb(200, 200, 200);"
                                              "padding: 1px 20px;}"
                                              "QPushButton:hover{font-weight:bold;}")
            logging.debug("channel2 disable")

        else:
            self.command2 = Protocol.PREAMBLE.value \
                           + Protocol.ENABLE_CHANNEL.value \
                           + '\x02' \
                           + Protocol.CHANNEL2.value \
                           + Protocol.ENABLE.value  # '\xAA'+'\xF1'+'\x01'+'\x00'
            self.channel2thread = USBWriteThread(self.device, self.command2)
            self.channel2thread.start()
            self.channel2Enable = 1
            self.canvasFrame.channel2Enable = 1
            self.channel2Button.setStyleSheet("QPushButton{border:1px solid rgb(200,200,200);"
                                              "border-top-right-radius:5px;"
                                              "border-bottom-right-radius: 5px;"
                                              "background-color:rgba(0, 200, 255,255);"
                                              "color:rgb(200, 200, 200);"
                                              "padding: 1px 20px;}"
                                              "QPushButton:hover{font-weight:bold;}")

            logging.debug("channel2 enable")

    def set_button_event(self):
        if self.device is None:
            logging.error("no device!!!")
            return
        logging.debug("setButton is pressed" + str(self.frenquencyComboBox.currentIndex())
                      + '+' + self.frenquencyComboBox.currentText())

        if self.frenquencyComboBox.currentText() == '1000Hz':
            self.canvasFrame.frequency = 1000
            self.readThread.frequency = 1000
        elif self.frenquencyComboBox.currentText() == '100Hz':
            self.canvasFrame.frequency = 100
            self.readThread.frequency = 100

        elif self.frenquencyComboBox.currentText() == '10Hz':
            self.canvasFrame.frequency = 10
            self.readThread.frequency = 10

        elif self.frenquencyComboBox.currentText() == '4Hz':
            self.canvasFrame.frequency = 4
            self.readThread.frequency = 4

        else:
            logging.warning("error frequency value:" + self.frenquencyComboBox.currentText())

        self.frequencyLabelValue.setText(self.frenquencyComboBox.currentText())

    def update_canvas(self, state):
        logging.debug("update_canvas:" + state)
        self.canvasFrame.update()

    def update_frequency(self, frequency):
        logging.debug("update_frequency")
        if self.readThread:
            self.frequencyLabelValue.setText(str(frequency) + "(HZ)")
            if frequency == 0:
                logging.warning("receive wrong frequency:0")
            else:
                self.canvasFrame.frequency = frequency

    def single_trigger_event(self, state):
        logging.debug("single_trigger_event:" + state)
        if self.ADCEnable == 0:
            return
        self.command = Protocol.PREAMBLE.value \
            + Protocol.ENABLE_ADC.value \
            + '\x01' \
            + Protocol.DISABLE.value  # '\xAA' + '\xF2' + '\x01' + '\x00'
        self.playThread = USBWriteThread(self.device, self.command)
        self.playThread.start()
        self.ADCEnable = 0
        self.enableLabelValue.setText("Stop")
        self.playButton.setStyleSheet("QPushButton{border:none;"
                                      "border-radius:%dpx;"
                                      "background-color:rgb(200, 100, 100);}"
                                      "QPushButton:hover{border:0;"
                                      "border-radius:%dpx;"
                                      "background-color:rgb(250, 100, 100);}" % (self.m_width/40, self.m_width/40))
        self.setButton.setStyleSheet("QPushButton{border-radius:%dpx;"
                                     "background-color:rgb(150, 255, 150);"
                                     "color:rgb(0, 0, 0);"
                                     "text-align: center center;}"
                                     "QPushButton:hover{background-color:rgb(100, 255, 100);"
                                     "color:rgb(255, 100, 100);"
                                     "font-size:20px}" % (self.m_width/80))
        self.setButton.setEnabled(True)
        self.channel1Button.setEnabled(True)
        self.channel2Button.setEnabled(True)
        logging.debug("trigger!!! sample stop")

    def closeEvent(self, *args, **kwargs):
        logging.debug("this closeEvent -------------")
        if self.device:
            self.device.close()
            self.readThread.terminate()
            self.readThread.wait()

    def __del__(self):
        logging.debug("this del -------------")
        # self.readThread.terminate()
        # self.readThread.wait()
