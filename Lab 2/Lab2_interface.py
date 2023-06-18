from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
import serial
import serial.tools.list_ports as ports_list

class Application(QMainWindow):

    def __init__(self) -> None:
        super(Application, self).__init__()
        width = 400
        height = 300

        self.setGeometry(int((1920 - width) / 2), int((1080 - height) / 2), width, height)
        self.setWindowTitle("Lab 2")
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

        self.algo1_button = QtWidgets.QPushButton(self)
        self.algo1_button.setGeometry(35, label_top.height() + 30, self.algo1_button.width() + 45, 40)
        self.algo1_button.setText("Algorithm 1")
        self.algo1_button.setStyleSheet("color: #FFFFFF; font-size: 25px; border: 1px solid #FFFFFF; padding-bottom: 4px; border-radius: 10px;")
        self.algo1_button.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.algo1_button.installEventFilter(self)

        self.algo2_button = QtWidgets.QPushButton(self)
        self.algo2_button.setGeometry(self.width() - self.algo1_button.width() - 35, label_top.height() + 30, self.algo2_button.width() + 45, 40)
        self.algo2_button.setText("Algorithm 2")
        self.algo2_button.setStyleSheet("color: #FFFFFF; font-size: 25px; border: 1px solid #FFFFFF; padding-bottom: 4px; border-radius: 10px;")
        self.algo2_button.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.algo2_button.installEventFilter(self)

        self.pins: list[QtWidgets.QLabel] = []
        left_margin = 9
        for i in range(8):
            pin = QtWidgets.QLabel(self)
            pin.setGeometry(left_margin, label_top.height() + self.algo1_button.height() + 30 + 70, 40, 40)
            left_margin += 49
            pin.setStyleSheet("background-color: #00145e;")
            self.pins.append(pin)
        self.timer1 = QtCore.QTimer(self)
        self.timer1.timeout.connect(self.algorithm1)
        self.timer2 = QtCore.QTimer(self)
        self.timer2.timeout.connect(self.algorithm2)
        self.pin_index = 0

        self.exception_text = QtWidgets.QLabel(self)
        self.exception_text.setText("")
        self.exception_text.setStyleSheet("color: #e80202; font-size: 18px;")
        self.exception_text.setGeometry(int((self.width() - self.exception_text.width()) / 2), label_top.height() + self.algo1_button.height() + 30 + 70 + 40 + 30, self.exception_text.width(), self.exception_text.height())


    def eventFilter(self, obj, event):
        if (event.type() == QtCore.QEvent.Type.HoverEnter and obj is self.open_button):
            self.open_button.setStyleSheet("background-color: #000435; color: #FFFFFF; font-size: 18px; border: 1px solid #FFFFFF; padding-bottom: 4px; border-radius: 10px;")
            return True
        if (event.type() == QtCore.QEvent.Type.MouseButtonPress and obj is self.open_button):
            self.exception_text.setText("")
            self.open_button.setStyleSheet("background-color: #000460; color: #FFFFFF; font-size: 18px; border: 1px solid #FFFFFF; padding-bottom: 4px; border-radius: 10px;")
            try:
                s = serial.Serial(port = self.dropdown.currentText(), baudrate = 9600, bytesize = 8, stopbits = 2, timeout = 5)
                res = s.read()
                if res == bytes([0xA1]):
                    QtCore.QTimer.singleShot(200, lambda: self.on_timeralgo1_click())
                    self.pin_index = 7
                    self.timer1.start(400)
                elif res == bytes([0xA2]):
                    QtCore.QTimer.singleShot(200, lambda: self.on_timeralgo2_click())
                    self.pin_index = 0
                    self.timer2.start(400)
            except serial.serialutil.SerialException:
                self.exception_text.setText("Serial port access denied!")
                self.exception_text.adjustSize()
                self.exception_text.setGeometry(int((self.width() - self.exception_text.width()) / 2), self.exception_text.geometry().top(), self.exception_text.width(), self.exception_text.height())
            QtCore.QTimer.singleShot(200, lambda: self.on_open_click())
            return True
        if (event.type() == QtCore.QEvent.Type.HoverLeave and obj is self.open_button):
            self.open_button.setStyleSheet("color: #FFFFFF; font-size: 18px; border: 1px solid #FFFFFF; padding-bottom: 4px; border-radius: 10px;")
            return True
        
        if (event.type() == QtCore.QEvent.Type.HoverEnter and obj is self.algo1_button):
            self.algo1_button.setStyleSheet("background-color: #000435; color: #FFFFFF; font-size: 25px; border: 1px solid #FFFFFF; padding-bottom: 4px; border-radius: 10px;")
            return True
        if (event.type() == QtCore.QEvent.Type.MouseButtonPress and obj is self.algo1_button):
            self.exception_text.setText("")
            self.algo1_button.setStyleSheet("background-color: #000460; color: #FFFFFF; font-size: 25px; border: 1px solid #FFFFFF; padding-bottom: 4px; border-radius: 10px;")
            try:
                s = serial.Serial(port = self.dropdown.currentText(), baudrate = 9600, bytesize = 8, stopbits = 2)
                s.write(bytes([0xA1]))
            except serial.serialutil.SerialException:
                self.exception_text.setText("Serial port access denied!")
                self.exception_text.adjustSize()
                self.exception_text.setGeometry(int((self.width() - self.exception_text.width()) / 2), self.exception_text.geometry().top(), self.exception_text.width(), self.exception_text.height())
            return True
        if (event.type() == QtCore.QEvent.Type.HoverLeave and obj is self.algo1_button):
            self.algo1_button.setStyleSheet("color: #FFFFFF; font-size: 25px; border: 1px solid #FFFFFF; padding-bottom: 4px; border-radius: 10px;")
            return True
        
        if (event.type() == QtCore.QEvent.Type.HoverEnter and obj is self.algo2_button):
            self.algo2_button.setStyleSheet("background-color: #000435; color: #FFFFFF; font-size: 25px; border: 1px solid #FFFFFF; padding-bottom: 4px; border-radius: 10px;")
            return True
        if (event.type() == QtCore.QEvent.Type.MouseButtonPress and obj is self.algo2_button):
            self.exception_text.setText("")
            self.algo2_button.setStyleSheet("background-color: #000460; color: #FFFFFF; font-size: 25px; border: 1px solid #FFFFFF; padding-bottom: 4px; border-radius: 10px;")
            try:
                s = serial.Serial(port = self.dropdown.currentText(), baudrate = 9600, bytesize = 8, stopbits = 2)
                s.write(bytes([0xA2]))
            except serial.serialutil.SerialException:
                self.exception_text.setText("Serial port access denied!")
                self.exception_text.adjustSize()
                self.exception_text.setGeometry(int((self.width() - self.exception_text.width()) / 2), self.exception_text.geometry().top(), self.exception_text.width(), self.exception_text.height())
            return True
        if (event.type() == QtCore.QEvent.Type.HoverLeave and obj is self.algo2_button):
            self.algo2_button.setStyleSheet("color: #FFFFFF; font-size: 25px; border: 1px solid #FFFFFF; padding-bottom: 4px; border-radius: 10px;")
            return True
        return False

    def on_open_click(self):
        self.open_button.setStyleSheet("background-color: #000435; color: #FFFFFF; font-size: 18px; border: 1px solid #FFFFFF; padding-bottom: 4px; border-radius: 10px;")

    def on_timeralgo1_click(self):
        self.algo1_button.setStyleSheet("background-color: #000435; color: #FFFFFF; font-size: 25px; border: 1px solid #FFFFFF; padding-bottom: 4px; border-radius: 10px;")
    
    def on_timeralgo2_click(self):
        self.algo2_button.setStyleSheet("background-color: #000435; color: #FFFFFF; font-size: 25px; border: 1px solid #FFFFFF; padding-bottom: 4px; border-radius: 10px;")

    def algorithm1(self):
        if self.pin_index + 1 < 8:
            self.pins[self.pin_index + 1].setStyleSheet("background-color: #00145e;")
        if self.pin_index == -2:
            self.timer1.stop()
            self.pin_index = 0
            return
        
        if self.pin_index >= 0:
            self.pins[self.pin_index].setStyleSheet("background-color: #002091;")

        self.pin_index -= 1

    def algorithm2(self):
        if self.pin_index - 2 >= 0:
            self.pins[self.pin_index - 2].setStyleSheet("background-color: #00145e;")
        if self.pin_index == 8:
            self.pin_index = 1
        if self.pin_index == 9:
            self.timer2.stop()
            self.pin_index = 0
            return
        
        if self.pin_index < 8:
            self.pins[self.pin_index].setStyleSheet("background-color: #002091;")

        self.pin_index += 2



def window() -> None:
    app = QApplication(sys.argv)
    win = Application()
    
    win.show()
    sys.exit(app.exec_())

window()