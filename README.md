# Oscilloscope Simulation System

## 1 Introduction

The Oscilloscope Simulation System base on EFM8UB1 is intended to bring a tool to sample ADC value and display it as waveform on a computer screen, Through a combination of hardware and software, it looks like a real oscilloscope.

The software architecture of system consist of firmware running on EFM8UB1 STK and application running on a computer. The GUI application running on a computer is developed by python 2.7, pyside2, Qt5, and USBxpress library.

The hardware consists of a computer host and a EFM8UB1EK device, the EFM8UB1EK is connected with the computer with USB cable. Use EFM8UB1 to sample the adc voltage value, send the collected data to the host via USB. The block is illustrated below.

![hardware architecture][architecture_png]

## 2 Preparation

### 2.1 Install Python 2.7 32-bit


There are most of library made by Silabs is developed with Python 2.7 32-bit. Please download and install Python 2.7 32-bit, the download link is below.
https://www.python.org/downloads/release/python-2715/ 

### 2.2 Install Pyside2 and Qt

Official release wheels of Qt For Python can be installed regularly via pip:

```shell
pip install pyside2
```

Pre-release (snapshot) wheels containing the latest code changes are available at http://download.qt.io/snapshots/ci/pyside/

For example you can install the latest 5.11 snapshot wheel using:

```shell
pip install --index-url=http://download.qt.io/snapshots/ci/pyside/5.11/latest/ pyside2 --trusted-host download.qt.io
```

See more info from http://wiki.qt.io/Qt_for_Python/GettingStarted.

### 2.3 Firmware Programming

The compiled firmware is located directory Bin/, program the Hex file to EFM8 Universal Bee Starter Kit (SLSTK2000A) to make it as a oscilloscope device.

### Connection

Connect the EFM8UB1EK device and a computer with USB cable.

### 2.4 Execute GUI application

Download the software/ to local and run the application with command below.

```python
python.exe main.py
```

## 3 Overview GUI

Application starts with a login widget as shown below. The component 1 is device combobox which shows the connected EFM8UB1EK device, the component 2 is a pushbutton.

![login][login_widget]

The device shown in combobox will be open and application jump to a main widget when the pushbutton is pressed.

![main widget][main_widget]

District 1 is a canvas which used to display the waveform, when cursor is in this district the time and ADC value of cursor position will be shown.

District 2 is display district.They are zoom in pushbutton, zoom out pushbutton, enable ADC  pushbutton and single trigger button from left to right in this district.

District 3 is used to control 3 LED on EFM8UB1EK device.

District 4 is used to enable channel, there are two channel available which routed to GPIO pin1.7 and GPIO pin1.2 respectively.

District 5 is frequency district, the sample frequency will be set to the value shown in combobox when the set pushbutton is pushed.

The current information will be shown in the district 6.

## 4 Start sampling

Suppose have all the required environments and equipment, you can start sampling by following the steps below.

* Connect the device and host
* Execute GUI application
* Choose the required device in combobox and press enter button
* Check the required channel
* Choose the appropriate frequency and then press set button
* Push the enable ADC button in district 2

After that, the waveform will be display in district 1.

## 5 Software development and functional development

In order to facilitate the later function expansion, a flexible protocol was developed.Every operation will be a item of command which consists of preamble byte, command byte, value length and value. The preamble byte is a fixed value 0xAA, the command byte shows the specific operation, the third byte followed by value is length of value.
The table shown below lists the command has been taken. If one want to develop a new command, he can just start with 0x60.

![protocol table][protocol_table]

## 6 Conclusion

The oscilloscope simulation system is used to sample analog voltage and show it as waveform. It provides two channel to sample the voltage signal, supports zoom out and zoom and is able to display voltage and time information on mouse cursor point. which make it looks like a real oscilloscope. It is significant tool to measure analog voltage for engineer.

[architecture_png]:img/architecture.png
[login_widget]:img/login_widget.png
[main_widget]:img/main_widget.png
[protocol_table]:img/protocol.png