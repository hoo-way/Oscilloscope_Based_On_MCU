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
from PySide2.QtWidgets import QWidget, QPushButton, QDesktopWidget, QComboBox, QVBoxLayout, QFrame, QLabel
from OscGui import OscGui
from PySide2.QtCore import Qt, QSize
from PySide2.QtGui import QCursor, QIcon, QBitmap, QPainter, QColor, QPixmap
from USBWriteThread import USBWriteThread
import logging


class Login(QWidget):
    device = None
    deviceList = []

    def __init__(self):
        QWidget.__init__(self)

        self.theme = 2

        screen = QDesktopWidget()
        logging.info("screen size:"+str(screen.width())+","+str(screen.height()))

        self.m_width = screen.height() / 2
        self.m_height = screen.height() / 2
        self.resize(self.m_width, self.m_height)
        # self.setFixedSize(self.m_width, self.m_height)
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)

        # delete title box
        self.setWindowFlags(Qt.FramelessWindowHint)
        # self.setAttribute(Qt.WA_TranslucentBackground)

        logging.info("login widget size:" + str(self.size()))
        self.bitmap = QBitmap(self.size())
        painter = QPainter(self.bitmap)

        painter.fillRect(self.rect(), Qt.white)

        painter.setBrush(QColor(0, 0, 0))
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.drawRoundedRect(self.rect(), 10, 10)
        self.setMask(self.bitmap)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, self.m_height/15)
        self.layout.setSpacing(self.m_height / 15)
        self.topframe = QFrame(self)
        self.topframe.setObjectName("topframe")
        if self.theme == 1:
            self.topframe.setStyleSheet(
                "#topframe{background-color:qlineargradient("
                "spread:pad,"
                "x1:0,y1:0,x2:1,y2:1,"
                "stop:0 #5efce8,"
                "stop:1 #736efe);}")
        elif self.theme == 2:
            self.topframe.setStyleSheet(
                "#topframe{background-color:qlineargradient("
                "spread:pad,"
                "x1:0,y1:0,x2:1,y2:0,"
                "stop:0 #3a6186,"
                "stop:1 #89253e);}")
        elif self.theme == 3:
            self.topframe.setStyleSheet(
                "#topframe{background-color:qlineargradient("
                "spread:pad,"
                "x1:0,y1:0,x2:0,y2:1,"
                "stop:0 #19547b,"
                "stop:1 #ffd89b);}")
        else:
            self.topframe.setStyleSheet(
                "#topframe{background-color:qlineargradient("
                "spread:pad,"
                "x1:0,y1:0,x2:1,y2:1,"
                "stop:0 #ff8177,"
                "stop:1 #b12a5b);}")
        self.layout.addWidget(self.topframe)

        # setup checkbox
        self.combobox = QComboBox(self)
        self.combobox.setObjectName("combobox")
        self.combobox.setFixedSize(self.m_width/1.5, self.m_height/10)
        self.combobox.setStyleSheet("QComboBox{border: 2px solid gray;"
                                    "border-radius:5px;"
                                    "background-color:rgb(255, 255, 255);"
                                    "color:rgb(0, 0, 0);"
                                    "padding: 1px 20px;}"
                                    "QComboBox:drop-down{subcontrol-origin: padding;"
                                    "subcontrol-position: top right;"
                                    "width: 50px;border-left-style:solid;"
                                    "border-top-right-radius: 3px;"
                                    "border-bottom-right-radius: 3px;"
                                    "border-left: 2px solid gray;"
                                    "background-color: rgba(100, 25, 100, 0);}"
                                    "QComboBox:down-arrow{border-image:url(icon/arrow-1.png);}"
                                    "QComboBox:item:selected{background: rgb(232, 241, 250);color: rgb(2, 65, 132);}"
                                    "QStyledItemDelegate{border: 100px solid rgb(161,161,161);}")

        # self.combobox.move(200, 200)
        self.layout.addWidget(self.combobox, 0, Qt.AlignHCenter)

        # setup login button
        self.loginbtn = QPushButton("ENTER", self)
        self.loginbtn.setObjectName("loginbtn")
        self.loginbtn.setFixedSize(self.m_width/1.5, self.m_height/10)
        self.loginbtn.setContentsMargins(200, 20, 20, 20)
        self.loginbtn.clicked.connect(self.login_event)
        self.loginbtn.setStyleSheet("QPushButton{border-radius:%dpx;"
                                    "background-color:#89253e;"
                                    "color:rgb(0, 0, 0);}"
                                    "QPushButton:hover{color:rgb(0, 255, 0);}" % (self.m_height/20))
        self.layout.addWidget(self.loginbtn, 0, Qt.AlignHCenter)

        # setup exit button
        self.exitbtn = QPushButton(self)
        # self.exitbtn.setText("Close")
        self.exitbtn.setToolTip("Close the widget")
        self.exitbtn.setFixedSize(40, 40)
        self.exitbtn.setIcon(QIcon("icon/close.png"))
        self.exitbtn.setIconSize(QSize(40, 40))
        self.exitbtn.clicked.connect(self.exit_event)
        logging.info("topframesize:" + str(self.topframe.size()))
        self.exitbtn.move(self.width()-40, 0)
        # self.exitbtn.setGeometry(self.topframe.width()-40, 0, 100, 40)
        self.exitbtn.setStyleSheet("background-color: #600")
        self.exitbtn.setStyleSheet("background-color: transparent")
        self.exitbtn.isEnabled()

        self.logoImage = QPixmap("icon/silabslogo.png")
        self.logo = self.logoImage.scaled(self.m_width/5, self.m_height/5, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self.logoLable = QLabel(self)
        self.logoLable.setObjectName("logoLable")
        self.logoLable.setAlignment(Qt.AlignCenter)
        self.logoLable.setPixmap(self.logo)
        self.logoLable.setFixedSize(self.m_width/4, self.m_height/4)
        # self.logo.setScaledContents(True)
        self.logoLable.setStyleSheet("#logoLable{border: 2px solid gray;"
                                     "border-radius:75px;"
                                     "background-color:rgb(100, 100, 100);"
                                     "color:rgb(0, 0, 0);}")
        self.logoLable.move(self.m_width / 2 - self.m_width/8, self.m_height / 6)

        self.m_drag = False
        self.m_DragPosition = 0
        self.MainWindow = 0

    def login_event(self):
        if self.combobox.currentText() == "None":
            return
        self.hide()
        self.device = self.deviceList[self.combobox.currentIndex()]
        self.device.open()
        command = '\xAA' + '\xF2' + '\x01' + '\x00'
        play_thread = USBWriteThread(self.device, command)
        play_thread.start()
        self.MainWindow = OscGui(self.device)
        self.MainWindow.show()

    def exit_event(self):
        exit(0)

    def mousePressEvent(self, event):

        if event.button() == Qt.LeftButton:
            self.m_drag = True
            self.m_DragPosition = event.globalPos() - self.pos()
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))

    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.m_drag:
            self.move(event.globalPos() - self.m_DragPosition)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.m_drag = False
        self.setCursor(QCursor(Qt.ArrowCursor))
