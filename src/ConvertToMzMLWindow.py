# -*- coding: utf-8 -*-
"""
Created on Wed Jul 16 14:59:34 2014

@author: vesheka
"""

from PyQt4 import QtGui
import subprocess
import os

class ConvertToMzMLWindow(QtGui.QDialog):
    def __init__(self):
        super(ConvertToMzMLWindow,self).__init__()
        self.initUI()
        
    def browseSource(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', filter='Wiff (*.wiff)')
        print fname
        self.source_filename.setText(fname)
        
    def browseDest(self):
        fdlg = QtGui.QFileDialog()
        fdlg.setFileMode(QtGui.QFileDialog.AnyFile)
        fname = fdlg.getSaveFileName(self, 'Save file')
        
        #dname = QtGui.QFileDialog.getExistingDirectory(self,'Destination folder')
        #print(dname)
        self.destination_filename.setText(fname)
        
    def convert(self):
        source = str(self.source_filename.text())
        dest = str(self.destination_filename.text())
        if source and dest:
            absciex_exec = 'C:\\Program Files (x86)\\AB SCIEX\\MS Data Converter\\AB_SCIEX_MS_Converter.exe'
            
            subprocess.call([absciex_exec,'WIFF',source,'-profile','MZML',dest +"\\"+ os.path.basename(source)[:-4] +'mzml'])
            print("Conversion complete!")
            self.cleanup()
        else:
            e = QtGui.QErrorMessage(self)
            e.setWindowTitle("Error")
            e.showMessage("Please enter valid path for Source and Destination folder")
            
    def cleanup(self):
        print "Cleaning Up!"
        
        self.e = QtGui.QMessageBox(self)
        self.e.setWindowTitle("Complete")
        self.e.setText("Conversion complete")
        self.e.show()
        self.close()
        
        
    def initUI(self):
        self.setGeometry(300,300,250,150)
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.setWindowTitle('MzML Converter')
        
        
        #Source file selection code
        self.source_filename = QtGui.QLineEdit()
        self.source_label = QtGui.QLabel()
        self.source_label.setText("Wiff file location :")
        self.browse_source_button = QtGui.QPushButton("Browse")
        self.browse_source_button.clicked.connect(self.browseSource)
        self.l1 = QtGui.QHBoxLayout()
        self.l1.addWidget(self.source_filename)
        self.l1.addWidget(self.browse_source_button)
        
        #Destination file selection code
        self.destination_label = QtGui.QLabel()
        self.destination_filename = QtGui.QLineEdit()
        self.destination_label.setText("MzML File location: ")
        self.browse_dest_button = QtGui.QPushButton("Browse")
        self.browse_dest_button.clicked.connect(self.browseDest)
        self.l2 = QtGui.QHBoxLayout()
        self.l2.addWidget(self.destination_filename)
        self.l2.addWidget(self.browse_dest_button)
        
        
        self.button = QtGui.QPushButton("Convert")
        self.button.clicked.connect(self.convert)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.source_label)
        layout.addLayout(self.l1)
        layout.addWidget(self.destination_label)
        layout.addLayout(self.l2)
        layout.addStretch(1)
        layout.addWidget(self.button)
        self.setLayout(layout)
