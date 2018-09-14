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
import sys
import usbxpress
from PySide2.QtWidgets import QApplication
from Login import Login
import logging

if __name__ == "__main__":

    app = QApplication(sys.argv)

    logging.basicConfig(filename='./log.log',
                        filemode='w',
                        level=logging.ERROR,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s    %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    console = logging.StreamHandler()
    console.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(filename)s[line:%(lineno)d] %(levelname)s    %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    Window = Login()

    # Get the number of attached USBXpress devices
    num_devices = usbxpress.USBXpressLib().get_num_devices()
    logging.info("Number of attached USBXpress devices: %d" % num_devices)
    if num_devices:
        for i in range(0, num_devices):
            device = usbxpress.USBXpressDevice(i)

            # Print device information
            logging.info("USBXpress Device: %d" % i)
            logging.info("Product Description:    %s" % (device.get_description()))
            logging.info("Serial Number:          %s" % (device.get_serial_number()))
            logging.info("Link Name:              %s" % (device.get_link_name()))
            logging.info("VID:                    %s" % (device.get_vid()))
            logging.info("PID:                    %s" % (device.get_pid()))

            pid = device.get_pid()
            vid = device.get_vid()

            Window.combobox.addItem(str(i) + "--" + vid + ":" + pid)
            Window.deviceList.append(device)

        Window.loginbtn.setEnabled(True)

    else:
        Window = Login()
        Window.loginbtn.setEnabled(False)
        Window.loginbtn.setStyleSheet("QPushButton{border-radius:25px;"
                                      "background-color:rgb(200, 200, 200);"
                                      "color:rgb(0, 0, 0);}")
        Window.combobox.addItem("None Device")

    Window.show()
    sys.exit(app.exec_())
