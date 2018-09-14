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
from PySide2.QtCore import QThread, QMutex


class USBWriteThread(QThread):
    mutex = QMutex()

    def __init__(self, device, tx_data):
        QThread.__init__(self)
        self.device = device
        self.tx_data = tx_data
        self.num_bytes_written = 0

    def run(self, *args, **kwargs):
        self.mutex.lock()
        self.num_bytes_written = self.device.write(self.tx_data)
        # print "write thread:", self.num_bytes_written, self.tx_data.encode('hex')
        self.mutex.unlock()
