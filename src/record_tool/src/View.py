#!/usr/bin/env python

from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QInputDialog, QLineEdit, QDialog, QGridLayout, QApplication, QMainWindow, QMessageBox, QGroupBox, QVBoxLayout
from PyQt5.QtGui import QPixmap, QIcon
import rospy

class MyApp(QWidget):
    def __init__(self):  
        super(MyApp, self).__init__()        
        self.initUI()

    def closeEvent(self, _event):
        self.control.kill_all_Thread()
        _event.accept()

    def set_control(self, _control):
        self.control = _control

    def initUI(self):
        self.setWindowTitle('KIAPI logging tool')
        self.setWindowIcon(QIcon('./data/Icon.png'))
        self.setGeometry(300, 500, 300, 200)

        #kiapi_Icon = QPixmap('/home/kiapi/Documents/record_tool/src/record_tool/src/data/KIAPI.png')
        #label = QLabel()
        #label.setPixmap(kiapi_Icon.scaled(210,20)) # 이미지 세팅
        grid = QGridLayout()
        grid.addWidget(self.create_meta_group(), 0, 0)
        grid.addWidget(self.create_record_group(), 0, 1)
        #grid.addWidget(label, 1, 0, 1, 2)
        self.setLayout(grid)

        self.show()     

    def create_meta_UI(self, _type, _connect_func, _layout, _x, _y):
        #btn 정의
        btn = QPushButton(_type, self)
        btn.clicked.connect(_connect_func)
        #label 정의
        label = QLabel(_type, self)
        label.setFixedWidth(180)
        label.font().setPixelSize(30)

        _layout.addWidget(btn, _x, _y)
        _layout.addWidget(label, _x, _y + 1)

        return label

    def create_meta_group(self):
        #group box정의
        groupbox = QGroupBox('Meta data')
        layout = QGridLayout() 
        
        label_passengers = self.create_meta_UI("passengers", self.showDialog_btn_passengers, layout, 0, 0)
        label_purpose = self.create_meta_UI("purpose", self.showDialog_btn_purpose, layout, 1, 0)
        label_area = self.create_meta_UI("area", self.showDialog_btn_area, layout, 2, 0)
        label_weather = self.create_meta_UI("weather", self.showDialog_btn_weather, layout, 3, 0)
        label_situation = self.create_meta_UI("situation", self.showDialog_btn_situation, layout, 4, 0)

        groupbox.setLayout(layout)

        self.dic_label = {"passengers":label_passengers, "purpose":label_purpose, "area":label_area, "weather":label_weather, "situation":label_situation}

        return groupbox       

    def create_record_group(self):
        #group box정의    
        groupbox = QGroupBox('Logging')

        #btn 정의
        btn_manual_record = QPushButton("manual logging", self)
        btn_manual_record.clicked.connect(self.btn_manual_record_clicked)

        #btn_event_record = QPushButton("event record", self)
        #btn_event_record.clicked.connect(self.btn_event_record_clicked)

        #btn_upload = QPushButton("upload", self)
        #btn_upload.clicked.connect(self.btn_manual_record_clicked)

        #label 정의
        self.label_record_state = QLabel('Logging_state', self)
        self.label_record_state.setFixedWidth(230)
        font_record_state = self.label_record_state.font()
        font_record_state.setPointSize(30)

        self.label_space = QLabel('Free_space', self)
        self.label_space.setFixedWidth(230)
        font_space = self.label_space.font()
        font_space.setPointSize(30)

        kiapi_Icon = QPixmap('./data/KIAPI.png')
        label = QLabel()
        label.setPixmap(kiapi_Icon.scaled(210,20)) # 이미지 세팅

        layout = QGridLayout()
        layout.addWidget(btn_manual_record, 0, 0)
        #layout.addWidget(btn_event_record, 0, 1)
        #layout.addWidget(btn_upload, 1, 0)
        layout.addWidget(self.label_record_state, 1, 0)
        layout.addWidget(self.label_space, 2, 0)
        layout.addWidget(label, 3, 0)

        groupbox.setLayout(layout)
        
        return groupbox

    def create_png(self):
        groupbox = QGroupBox()
        layout = QGridLayout() 

        kiapi_Icon = QPixmap('./data/KIAPI.png')
        label = QLabel(self)
        label.setPixmap(kiapi_Icon.scaled(300,20)) # 이미지 세팅

        layout = QGridLayout()
        layout.addWidget(label,0,0)
        groupbox.setLayout(layout)

        return groupbox

    def showDialog_btn_passengers(self):
        text, ok = QInputDialog.getText(self, 'Input Dialog', 'Enter your name:')
        if ok :
            self.control.button_handler(text, "passengers")         

    def showDialog_btn_purpose(self):
        text, ok = QInputDialog.getText(self, 'Input Dialog', 'Enter your purpose:')
        if ok :        
            self.control.button_handler(text, "purpose")  

    def showDialog_btn_area(self):
        text, ok = QInputDialog.getText(self, 'Input Dialog', 'Enter your area:')
        if ok :
            self.control.button_handler(text, "area")

    def showDialog_btn_weather(self):
        text, ok = QInputDialog.getText(self, 'Input Dialog', 'Enter your weather:')
        if ok :
            self.control.button_handler(text, "weather")                                  

    def showDialog_btn_situation(self):
        text, ok = QInputDialog.getText(self, 'Input Dialog', 'Enter your situation:', text = self.control.dic_meta["situation"])
        if ok :           
            self.control.button_handler(text, "situation")     

    def btn_manual_record_clicked(self):
        #rospy.loginfo("Mannual test btn clicked, plz use car's btn")
        self.control.button_handler("", "manual_record")

    # def btn_event_record_clicked(self):
    #     print("dont use")
        #rospy.loginfo("Event btn clicked")
        #self.control.button_handler("", "event_record")  

    def update_label(self, **kwargs):
        for key, text in kwargs.items():
            self.dic_label[key].setText(text)

    def update_label_record_state(self, _text):
        self.label_record_state.setText(_text)
        self.label_record_state.update()

    def update_space(self, _text):
        self.label_space.setText(_text)
        self.label_space.update()

    def run_set_all_meta_data(self):
        dlg = set_all_meta_data()
        dlg.exec_()
        dic_dlg = {"passengers":dlg.passengers, "purpose":dlg.purpose, "area":dlg.area, "weather":dlg.weather, "situation":dlg.situation}
                
        return dic_dlg

    def run_messageBox(self):        
        QMessageBox.question(self, "Question", "not enough space left")

class set_all_meta_data(QDialog):
    def __init__(self):
        super(set_all_meta_data, self).__init__()
        self.setupUI()

    def setupUI(self):
        self.setGeometry(1100, 200, 300, 300)
        self.setWindowTitle("Sign In")

        self.label_passengers = QLabel("passengers: ", self)
        self.label_purpose = QLabel("purpose: ", self)
        self.label_area = QLabel("area: ", self)
        self.label_weather = QLabel("weather: ", self)
        self.label_situation = QLabel("situation: ", self)

        self.lineEdit_passengers = QLineEdit()
        self.lineEdit_purpose = QLineEdit()
        self.lineEdit_area = QLineEdit()
        self.lineEdit_weather = QLineEdit()
        self.lineEdit_situation = QLineEdit()

        self.pushButton= QPushButton("Ok")
        self.pushButton.clicked.connect(self.pushButtonClicked)

        self.layout = QGridLayout()
        self.layout.addWidget(self.label_passengers, 0, 0)
        self.layout.addWidget(self.label_purpose, 1, 0)
        self.layout.addWidget(self.label_area, 2, 0)
        self.layout.addWidget(self.label_weather, 3, 0)
        self.layout.addWidget(self.label_situation, 4, 0)

        self.layout.addWidget(self.lineEdit_passengers, 0, 1)
        self.layout.addWidget(self.lineEdit_purpose, 1, 1)
        self.layout.addWidget(self.lineEdit_area, 2, 1)
        self.layout.addWidget(self.lineEdit_weather, 3, 1)
        self.layout.addWidget(self.lineEdit_situation, 4, 1)

        self.layout.addWidget(self.pushButton, 5, 0)
        self.setLayout(self.layout)

    def pushButtonClicked(self):
        self.passengers = self.lineEdit_passengers.text()
        self.purpose = self.lineEdit_purpose.text()
        self.area = self.lineEdit_area.text()
        self.weather = self.lineEdit_weather.text()
        self.situation = self.lineEdit_situation.text()

        if (self.passengers != "") and (self.purpose != "") and (self.area != "") and (self.weather != ""):           
            self.close()
            
        self.label_error  = QLabel("plz enter all data", self)
        self.label_error.setStyleSheet("color: #FF0000") #RRGGBB
        self.layout.addWidget(self.label_error, 5, 1)