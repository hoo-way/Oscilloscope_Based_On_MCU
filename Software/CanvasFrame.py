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

from PySide2.QtWidgets import QFrame
from PySide2.QtGui import QPainter, QPen, QCursor, QFont, QColor
from PySide2.QtCore import Qt
import copy
import logging


ADCVALUEMAX = 3300


class CanvasFrame(QFrame):
    Channel1List = []
    Channel2List = []
    frequency = 1000
    scaleRatio = 1
    trigger = 0
    dragBias = 0
    dragEnable = False
    dragEnable_t = False
    dragBias_t = 0
    paintPointMax = 300
    channel1Enable = 0
    channel2Enable = 0

    def __init__(self):
        QFrame.__init__(self)
        self.setMouseTracking(True)
        self.dx = 0
        self.dy = 0
        self.m_width = self.width()
        self.m_height = self.height()
        self.complete = 1
        self.Channel1PaintList = []
        self.Channel1PaintList2 = []
        self.Channel2PaintList = []
        self.Channel2PaintList2 = []
        self.Channel1PaintListLen = 0
        self.Channel2PaintListLen = 0
        self.unit = 0
        self.m_DragPosition = 0
        self.period = 0
        logging.debug("CanvasFrame:" + str(self.m_width) + "+" + str(self.m_height))

    def paintEvent(self, paint_event):
        self.m_width = self.width()
        self.m_height = self.height()

        if self.channel1Enable:
            self.Channel1PaintList = []
            self.Channel1PaintList2 = []
        if self.channel2Enable:
            self.Channel2PaintList = []
            self.Channel2PaintList2 = []
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing, True)

        pen = QPen(Qt.white, 1, Qt.SolidLine)
        qp.setPen(pen)
        qp.translate(0, self.m_height / 2)
        qp.drawLine(0, 0, self.m_width, 0)
        qp.drawLine(self.m_width/2, self.m_height / 2, self.m_width/2, -self.m_height / 2)

        pen.setStyle(Qt.DashLine)
        pen.setWidth(1)
        qp.setPen(pen)
        qp.drawLine(0, -self.m_height / 4, self.m_width, -self.m_height / 4)
        qp.drawLine(0, self.m_height / 4, self.m_width, self.m_height / 4)
        qp.drawLine(self.m_width / 4, -self.m_height / 2, self.m_width / 4, self.m_height / 2)
        qp.drawLine(self.m_width * 3 / 4, -self.m_height / 2, self.m_width * 3 / 4, self.m_height / 2)

        pen.setStyle(Qt.SolidLine)
        pen.setWidth(5)
        qp.setPen(pen)
        for i in range(1, 10):
            qp.drawLine(i*(self.m_width / 10),
                        self.m_height / 2,
                        i*(self.m_width / 10),
                        self.m_height / 2 - 1)

        pen.setWidth(2)
        pen.setStyle(Qt.SolidLine)
        pen.setColor(QColor(200, 100, 100))
        qp.setPen(pen)
        self.unit = float(self.m_height) * 0.4 / ADCVALUEMAX
        self.paintPointMax = self.m_width

        if self.channel1Enable:
            if self.scaleRatio == 1:
                self.Channel1PaintList = copy.copy(self.Channel1List)
            else:
                self.Channel1PaintList2 = copy.copy(self.Channel1List)
                for i in range(0, len(self.Channel1PaintList2), self.scaleRatio):
                    self.Channel1PaintList.append(self.Channel1PaintList2[i])
            # print "self.Channel1PaintList:", self.Channel1PaintList
            self.Channel1PaintListLen = len(self.Channel1PaintList)

        if self.channel2Enable:
            if self.scaleRatio == 1:
                self.Channel2PaintList = copy.copy(self.Channel2List)
            else:
                self.Channel2PaintList2 = copy.copy(self.Channel2List)
                for i in range(0, len(self.Channel2PaintList2), self.scaleRatio):
                    self.Channel2PaintList.append(self.Channel2PaintList2[i])
            # print "self.Channel2PaintList:", self.Channel2PaintList
            self.Channel2PaintListLen = len(self.Channel2PaintList)

        if self.channel1Enable:
            if self.Channel1PaintListLen == 0:
                qp.drawLine(0, 0, self.m_width, self.m_height / 2)
            elif self.Channel1PaintListLen >= self.paintPointMax:
                if self.dragEnable is True:
                    if len(self.Channel1PaintList) - self.dragBias - self.dragBias_t < self.paintPointMax:
                        # self.dragBias_t = len(self.Channel1PaintList) - self.paintPointMax - self.dragBias
                        self.dragBias_t = 0
                        self.dragBias = len(self.Channel1PaintList) - self.paintPointMax
                    if self.dragBias + self.dragBias_t < 0:
                        self.dragBias_t = 0
                        self.dragBias = 0

                for i in range(0, self.paintPointMax):
                    qp.drawLine(self.paintPointMax-1-i,
                                -self.Channel1PaintList[self.Channel1PaintListLen
                                                        - 1 - i - self.dragBias - self.dragBias_t] * self.unit,
                                self.paintPointMax-2-i,
                                -self.Channel1PaintList[self.Channel1PaintListLen
                                                        - 2 - i - self.dragBias - self.dragBias_t] * self.unit)
                    # print "dragBias,dragBias_t:", self.dragBias,self.dragBias_t

            else:
                for i in range(self.Channel1PaintListLen-1, 0, -1):

                    qp.drawLine(i + self.paintPointMax - self.Channel1PaintListLen,
                                - self.Channel1PaintList[i] * self.unit,
                                i + self.paintPointMax - self.Channel1PaintListLen - 1,
                                - self.Channel1PaintList[i - 1] * self.unit)
                    # qp.drawPoint(i, - self.Channel1PaintList[i] * self.unit)

        if self.channel2Enable:
            pen.setColor(QColor(0, 200, 255))
            qp.setPen(pen)
            if self.Channel2PaintListLen == 0:
                qp.drawLine(0, 0, self.m_width, self.m_height / 2)
            elif self.Channel2PaintListLen >= self.paintPointMax:
                if self.dragEnable is True:
                    if len(self.Channel2PaintList) - self.dragBias - self.dragBias_t < self.paintPointMax:
                        # self.dragBias_t = len(self.Channel2PaintList) - self.paintPointMax - self.dragBias
                        self.dragBias_t = 0
                        self.dragBias = len(self.Channel2PaintList) - self.paintPointMax
                    if self.dragBias + self.dragBias_t < 0:
                        self.dragBias_t = 0
                        self.dragBias = 0

                for i in range(0, self.paintPointMax):
                    qp.drawLine(self.paintPointMax-1-i,
                                -self.Channel2PaintList[self.Channel2PaintListLen-1-i-self.dragBias-self.dragBias_t]
                                * self.unit,
                                self.paintPointMax-2-i,
                                -self.Channel2PaintList[self.Channel2PaintListLen-2-i-self.dragBias-self.dragBias_t]
                                * self.unit)
                    # print "dragBias,dragBias_t:", self.dragBias,self.dragBias_t

            else:
                for i in range(self.Channel2PaintListLen-1, 0, -1):

                    qp.drawLine(i + self.paintPointMax - self.Channel2PaintListLen,
                                - self.Channel2PaintList[i] * self.unit,
                                i + self.paintPointMax - self.Channel2PaintListLen - 1,
                                - self.Channel2PaintList[i - 1] * self.unit)
                    # qp.drawPoint(i, - self.Channel2PaintList[i] * self.unit)

        qp.setFont(QFont("NEW ROMAN TIME", 8))
        pen.setWidth(1)
        pen.setStyle(Qt.SolidLine)
        pen.setColor(Qt.yellow)
        qp.setPen(pen)
        qp.drawLine(self.dx, -self.m_height / 2, self.dx, self.m_height / 2)
        self.period = self.scaleRatio * 1000 / self.frequency  # unit:ms

        pen.setColor(QColor(200, 100, 100))
        qp.setPen(pen)

        if self.channel1Enable:
            if self.Channel1PaintListLen-(self.m_width-self.dx) >= 0:
                qp.drawText(self.dx + 5,
                            self.dy - self.m_height/2 - 20,
                            "time= -"+str(self.period * (self.m_width-self.dx)
                                          + self.period*(self.dragBias+self.dragBias_t))
                            + "ms")
                qp.drawText(self.dx + 5,
                            self.dy - self.m_height / 2,
                            "volatge= "+str(self.Channel1PaintList[self.Channel1PaintListLen
                                                                   - (self.m_width - self.dx)
                                                                   - self.dragBias - self.dragBias_t])
                            + "mV")
            else:
                qp.drawText(self.dx + 5,
                            self.dy - self.m_height / 2,
                            str(0))

        if self.channel2Enable:
            pen.setColor(QColor(0, 200, 255))
            qp.setPen(pen)
            if self.Channel2PaintListLen-(self.m_width-self.dx) >= 0:
                qp.drawText(self.dx + 5,
                            self.dy - self.m_height/2 + 20,
                            "time= -"+str(self.period * (self.m_width-self.dx)
                                          + self.period*(self.dragBias+self.dragBias_t))
                            + "ms")
                qp.drawText(self.dx + 5,
                            self.dy - self.m_height / 2 + 40,
                            "volatge= "+str(self.Channel2PaintList[self.Channel2PaintListLen
                                                                   - (self.m_width - self.dx)
                                                                   - self.dragBias - self.dragBias_t])
                            + "mV")
            else:
                qp.drawText(self.dx + 5,
                            self.dy - self.m_height / 2,
                            str(0))

    def mousePressEvent(self, event):

        if event.button() == Qt.LeftButton and self.dragEnable is True:
            self.dragEnable_t = True
            self.m_DragPosition = event.globalPos() - self.pos()

            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))

    def mouseMoveEvent(self, event):

        self.dx = event.pos().x()
        self.dy = event.pos().y()
        # print self.dx ,"+", self.dy
        if self.dragEnable_t is True:
            self.dragBias_t = event.pos().x() - self.m_DragPosition.x()

        self.update()

    def mouseReleaseEvent(self, event):
        self.dragEnable_t = False
        self.dragBias = self.dragBias + self.dragBias_t
        self.dragBias_t = 0
        self.setCursor(QCursor(Qt.ArrowCursor))
        self.update()
