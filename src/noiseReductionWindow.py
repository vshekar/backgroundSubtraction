# -*- coding: utf-8 -*-
"""
Created on Wed Aug 13 11:07:40 2014

@author: vesheka
"""
from PyQt4 import QtGui,QtCore

class noiseReductionWindow(QtGui.QDialog):
    def __init__(self):
        super(noiseReductionWindow,self).__init__()
        self.initUI()
    
    def initUI(self):
        self.setGeometry(300,300,300,150)
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.setWindowTitle('Noise Reduction')
        
        self.control_filename = QtGui.QLineEdit()
        self.control_label = QtGui.QLabel()
        self.control_label.setText("Target File:")
        self.select_control_button = QtGui.QPushButton("Select Target File")
        self.select_control_button.clicked.connect(self.selectDataControl)
        self.control_layout = QtGui.QHBoxLayout()
        self.control_layout.addWidget(self.control_filename)
        self.control_layout.addWidget(self.select_control_button)
        
        
        self.result_filename = QtGui.QLineEdit()
        self.result_label = QtGui.QLabel()
        self.result_label.setText("Result File:")
        self.select_result_button = QtGui.QPushButton("Select Result File")
        self.select_result_button.clicked.connect(self.browseDest)
        self.result_layout =  QtGui.QHBoxLayout()
        self.result_layout.addWidget(self.result_filename)
        self.result_layout.addWidget(self.select_result_button)
        
        
        self.subtract_button = QtGui.QPushButton("Begin Noise Reduction")
        self.subtract_button.clicked.connect(self.noise_reduction)
        
        self.layout = QtGui.QVBoxLayout()
        self.layout.addWidget(self.control_label)
        self.layout.addLayout(self.control_layout)
        self.layout.addWidget(self.result_label)
        self.layout.addLayout(self.result_layout)
        self.layout.addStretch(1)
        self.layout.addWidget(self.subtract_button)
        self.setLayout(self.layout)
        
    def setDataList(self,dataList):
        self.listOfMzMLFiles = dataList 
        
    def selectDataControl(self):
        sdw = SelectDataWindow(self.listOfMzMLFiles)
        if not sdw.exec_():
            self.control_filename.setText(sdw.getFile())
            self.control_index = sdw.index
            
    def browseDest(self):
        fdlg = QtGui.QFileDialog()
        fdlg.setFileMode(QtGui.QFileDialog.AnyFile)
        fname = fdlg.getSaveFileName(self, 'Save file')
        print fname
        self.result_filename.setText(fname)
            
    def noise_reduction(self):
        mzML_file = self.listOfMzMLFiles[self.control_index]
        self.settings = QtCore.QSettings('settings.ini', QtCore.QSettings.IniFormat)
        self.settings.setFallbacksEnabled(False)
        
        min_ion_count = int(self.settings.value("minimum_ion_count").toPyObject())
        scan_range = int(self.settings.value("total_scan_range").toPyObject())
        tol_window = float(self.settings.value("tol_window").toPyObject())
        output_filename = str(self.result_filename.text())
        mzML_file.reduce_noise(min_ion_count,scan_range,tol_window, output_filename)
        


class SelectDataWindow(QtGui.QDialog):
    def __init__(self,dataList):
        super(SelectDataWindow,self).__init__()
        self.selectedFile = ""
        self.listOfMzMLFiles = dataList
        self.initUI()
        
    def getFile(self):
        return self.selectedFile
        
        
    def initUI(self):
        self.setGeometry(300,300,300,150)
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.setWindowTitle('Select Data')
        self.fileListWidget = QtGui.QListWidget()
        self.okButton = QtGui.QPushButton("Ok")
        self.okButton.clicked.connect(self.select)
        self.cancelButton = QtGui.QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.cancel)
        
        self.button_layout = QtGui.QHBoxLayout()
        self.button_layout.addWidget(self.okButton)
        self.button_layout.addWidget(self.cancelButton)
        self.layout = QtGui.QVBoxLayout()
        self.layout.addWidget(self.fileListWidget)
        self.layout.addLayout(self.button_layout)
        self.setLayout(self.layout)
        self.refreshList()
        
        
    def select(self):
        self.index = self.fileListWidget.currentRow()
        print self.index
        if self.index>-1:
            self.selectedFile = self.listOfMzMLFiles[self.index].filename
        self.close()
    
    def cancel(self):
        self.close()
        
    def refreshList(self):
        self.fileListWidget.clear()
        for exp in self.listOfMzMLFiles:
            self.fileListWidget.addItem(exp.filename)              