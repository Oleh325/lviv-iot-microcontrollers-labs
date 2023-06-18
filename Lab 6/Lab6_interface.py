from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
import serial
import serial.tools.list_ports as ports_list
import crc8

class Application(QMainWindow):

    def __init__(self) -> None:
        super(Application, self).__init__()
        width = 400
        height = 300

        self.setGeometry(int((1920 - width) / 2), int((1080 - height) / 2), width, height)
        self.setWindowTitle("Lab 6")
        self.setStyleSheet("background-color: #000420; font-size: 22px;")
        
        self.setWindowIcon(QtGui.QIcon("mcicon.png"))

        self.initUI()

    def initUI(self):
        label_top = QtWidgets.QLabel(self)
        label_top.setGeometry(QtCore.QRect(0, 0, self.width(), 50))
        label_top.setStyleSheet("background-color: #000412;")

        label_text = QtWidgets.QLabel(label_top)
        label_text.setText("COM порт")
        label_text.move(10, int((label_top.height() - label_text.height()) / 2))
        label_text.setStyleSheet("color: #FFFFFF; background: none;")

        self.dropdown = QtWidgets.QComboBox(label_top)
        for port in ports_list.comports():
            self.dropdown.addItem(port.name)
        dropdown_width = self.dropdown.width()
        for i in range(self.dropdown.count()):
            if (self.dropdown.itemText(i).__len__() > dropdown_width / 22):
                dropdown_width = self.dropdown.itemText(i).__len__() * 22
        self.dropdown.setGeometry(label_text.width() + 20, int((label_top.height() - self.dropdown.height()) / 2), dropdown_width, self.dropdown.height())
        self.dropdown.setStyleSheet("background-color: #000412; color: #FFFFFF; border: 1px solid #FFFFFF; border-radius: 6px;")
        self.dropdown.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))

        self.open_button = QtWidgets.QPushButton(label_top)
        self.open_button.setText("Відкрити")
        self.open_button.setGeometry(label_text.width() + self.dropdown.width() + 35, int((label_top.height() - 28) / 2), self.open_button.width(), 28)
        self.open_button.setStyleSheet("color: #FFFFFF; font-size: 18px; border: 1px solid #FFFFFF; padding-bottom: 4px; border-radius: 10px;")
        self.open_button.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.open_button.installEventFilter(self)

        self.slave1_button = QtWidgets.QPushButton(self)
        self.slave1_button.setGeometry(35, label_top.height() + 30, self.slave1_button.width() + 45, 40)
        self.slave1_button.setText("Slave 1")
        self.slave1_button.setStyleSheet("color: #FFFFFF; font-size: 25px; border: 1px solid #FFFFFF; padding-bottom: 4px; border-radius: 10px;")
        self.slave1_button.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.slave1_button.installEventFilter(self)

        self.slave2_button = QtWidgets.QPushButton(self)
        self.slave2_button.setGeometry(self.width() - self.slave1_button.width() - 35, label_top.height() + 30, self.slave2_button.width() + 45, 40)
        self.slave2_button.setText("Slave 2")
        self.slave2_button.setStyleSheet("color: #FFFFFF; font-size: 25px; border: 1px solid #FFFFFF; padding-bottom: 4px; border-radius: 10px;")
        self.slave2_button.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.slave2_button.installEventFilter(self)

        self.slave1_text = QtWidgets.QLabel(self)
        self.slave1_text.setText("Slave 1: ")
        self.slave1_text.setStyleSheet("color: #ffffff; font-size: 15px;")
        self.slave1_text.setGeometry(10, label_top.height() + self.slave1_button.height() + 50, self.slave1_text.width(), self.slave1_text.height())

        self.slave1_error = QtWidgets.QLabel(self)
        self.slave1_error.setText("")
        self.slave1_error.setStyleSheet("color: #e80202; font-size: 14px;")
        self.slave1_error.setGeometry(10, label_top.height() + self.slave1_button.height() + self.slave1_text.height() + 50, self.slave1_error.width(), self.slave1_error.height())

        self.slave2_text = QtWidgets.QLabel(self)
        self.slave2_text.setText("Slave 2: ")
        self.slave2_text.setStyleSheet("color: #ffffff; font-size: 15px;")
        self.slave2_text.setGeometry(10, label_top.height() + self.slave1_button.height() + self.slave1_text.height() + self.slave1_error.height() + 50, self.slave2_text.width(), self.slave2_text.height())

        self.slave2_error = QtWidgets.QLabel(self)
        self.slave2_error.setText("")
        self.slave2_error.setStyleSheet("color: #e80202; font-size: 14px;")
        self.slave2_error.setGeometry(10, label_top.height() + self.slave1_button.height() + self.slave1_text.height() + self.slave1_error.height() + self.slave2_text.height() + 50, self.slave2_error.width(), self.slave2_error.height())

        self.exception_text = QtWidgets.QLabel(self)
        self.exception_text.setText("")
        self.exception_text.setStyleSheet("color: #e80202; font-size: 18px;")
        self.exception_text.setGeometry(int((self.width() - self.exception_text.width()) / 2), label_top.height() + self.slave1_button.height() + 30 + 70 + 40 + 30, self.exception_text.width(), self.exception_text.height())


    def eventFilter(self, obj, event):
        if (event.type() == QtCore.QEvent.Type.HoverEnter and obj is self.open_button):
            self.open_button.setStyleSheet("background-color: #000435; color: #FFFFFF; font-size: 18px; border: 1px solid #FFFFFF; padding-bottom: 4px; border-radius: 10px;")
            return True
        if (event.type() == QtCore.QEvent.Type.MouseButtonPress and obj is self.open_button):
            self.exception_text.setText("")
            self.open_button.setStyleSheet("background-color: #000460; color: #FFFFFF; font-size: 18px; border: 1px solid #FFFFFF; padding-bottom: 4px; border-radius: 10px;")
            try:
                s = serial.Serial(port = self.dropdown.currentText(), baudrate = 4800, bytesize = 8, timeout = 3)
                if self.open_button.text() == "Відкрити":
                    self.open_button.setText("Закрити")
                else:
                    self.open_button.setText("Відкрити")
            except serial.serialutil.SerialException:
                self.exception_text.setText("Serial port access denied!")
                self.exception_text.adjustSize()
                self.exception_text.setGeometry(int((self.width() - self.exception_text.width()) / 2), self.exception_text.geometry().top(), self.exception_text.width(), self.exception_text.height())
            QtCore.QTimer.singleShot(200, lambda: self.on_open_click())
            return True
        if (event.type() == QtCore.QEvent.Type.HoverLeave and obj is self.open_button):
            self.open_button.setStyleSheet("color: #FFFFFF; font-size: 18px; border: 1px solid #FFFFFF; padding-bottom: 4px; border-radius: 10px;")
            return True
        if (event.type() == QtCore.QEvent.Type.HoverEnter and obj is self.slave1_button):
            self.slave1_button.setStyleSheet("background-color: #000435; color: #FFFFFF; font-size: 25px; border: 1px solid #FFFFFF; padding-bottom: 4px; border-radius: 10px;")
            return True
        if (event.type() == QtCore.QEvent.Type.MouseButtonPress and obj is self.slave1_button):
            self.exception_text.setText("")
            self.slave1_button.setStyleSheet("background-color: #000460; color: #FFFFFF; font-size: 25px; border: 1px solid #FFFFFF; padding-bottom: 4px; border-radius: 10px;")
            try:
                s = serial.Serial(port = self.dropdown.currentText(), baudrate = 4800, bytesize = 8, timeout = 3)
                s.write(bytes([0x57]))
                res = s.read_until(b"\0")
                self.slave1_text.setText("Slave 1: " + res.decode("utf-8"))
                self.slave1_text.adjustSize()
            except serial.serialutil.SerialException:
                self.exception_text.setText("Serial port access denied!")
                self.exception_text.adjustSize()
                self.exception_text.setGeometry(int((self.width() - self.exception_text.width()) / 2), self.exception_text.geometry().top(), self.exception_text.width(), self.exception_text.height())
            QtCore.QTimer.singleShot(200, lambda: self.on_timerslave1_click())
            return True
        if (event.type() == QtCore.QEvent.Type.HoverLeave and obj is self.slave1_button):
            self.slave1_button.setStyleSheet("color: #FFFFFF; font-size: 25px; border: 1px solid #FFFFFF; padding-bottom: 4px; border-radius: 10px;")
            return True
        if (event.type() == QtCore.QEvent.Type.HoverEnter and obj is self.slave2_button):
            self.slave2_button.setStyleSheet("background-color: #000435; color: #FFFFFF; font-size: 25px; border: 1px solid #FFFFFF; padding-bottom: 4px; border-radius: 10px;")
            return True
        if (event.type() == QtCore.QEvent.Type.MouseButtonPress and obj is self.slave2_button):
            self.exception_text.setText("")
            self.slave2_button.setStyleSheet("background-color: #000460; color: #FFFFFF; font-size: 25px; border: 1px solid #FFFFFF; padding-bottom: 4px; border-radius: 10px;")
            try:
                s = serial.Serial(port = self.dropdown.currentText(), baudrate = 4800, bytesize = 8, timeout = 3)
                s.write(bytes([0x4C]))
                res = s.read_until(b"\0")
                self.slave2_text.setText("Slave 2: " + res.decode('utf-8'))
                self.slave2_text.adjustSize()
            except serial.serialutil.SerialException:
                self.exception_text.setText("Serial port access denied!")
                self.exception_text.adjustSize()
                self.exception_text.setGeometry(int((self.width() - self.exception_text.width()) / 2), self.exception_text.geometry().top(), self.exception_text.width(), self.exception_text.height())
            QtCore.QTimer.singleShot(200, lambda: self.on_timerslave2_click())
            return True
        if (event.type() == QtCore.QEvent.Type.HoverLeave and obj is self.slave2_button):
            self.slave2_button.setStyleSheet("color: #FFFFFF; font-size: 25px; border: 1px solid #FFFFFF; padding-bottom: 4px; border-radius: 10px;")
            return True
        return False

    def on_open_click(self):
        self.open_button.setStyleSheet("background-color: #000435; color: #FFFFFF; font-size: 18px; border: 1px solid #FFFFFF; padding-bottom: 4px; border-radius: 10px;")

    def on_timerslave1_click(self):
        self.slave1_button.setStyleSheet("background-color: #000435; color: #FFFFFF; font-size: 25px; border: 1px solid #FFFFFF; padding-bottom: 4px; border-radius: 10px;")
    
    def on_timerslave2_click(self):
        self.slave2_button.setStyleSheet("background-color: #000435; color: #FFFFFF; font-size: 25px; border: 1px solid #FFFFFF; padding-bottom: 4px; border-radius: 10px;")
    
    def crc8(self, data):
        crc = 0x00
        for byte in data:
            extract = byte
            for _ in range(8):
                sum = (crc ^ extract) & 0x01
                crc >>= 1
                if sum:
                    crc ^= 0x8C
                extract >>= 1
        return crc
    

def window() -> None:
    app = QApplication(sys.argv)
    win = Application()
    
    win.show()
    sys.exit(app.exec_())

window()