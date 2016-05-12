# -*- coding: utf-8 -*-
"""
Created on Wed Jul 16 15:00:09 2014

@author: vesheka
"""
from PyQt4 import QtGui,QtCore
import threading

import Experiment

class OpenMzMLFileWindow(QtGui.QDialog):
    def __init__(self):
        super(OpenMzMLFileWindow,self).__init__()
        self.initUI()
        
    def browseSource(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', filter='MzML (*.mzml)')
        print fname
        self.source_filename.setText(fname)
        
    def setMzMLList(self,mzMLList):
        self.ListOfMzMLFiles = mzMLList
        
    def importMzML(self):
        source = str(self.source_filename.text())
        print source
        
        if source:
            self.thread = ImportThread(source,self.ListOfMzMLFiles)
            self.thread.start()
            self.thread.taskFinished.connect(self.cleanup) 
                
            
        else:
            e = QtGui.QErrorMessage(self)
            e.setWindowTitle("Error")
            e.showMessage("Please enter valid path for Source file")
       
    def cleanup(self):
        print "Cleaning Up!"
        
        e = QtGui.QMessageBox(self)
        e.setWindowTitle("Complete")
        e.setText("Import is complete")
        e.show()
        self.close()
        
    def initUI(self):
        self.setGeometry(300,300,250,150)
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.setWindowTitle('Import/Open MzML File')
        
        
        #Source file selection code
        self.source_filename = QtGui.QLineEdit()
        self.source_label = QtGui.QLabel()
        self.source_label.setText("MzML file location :")
        self.browse_source_button = QtGui.QPushButton("Browse")
        self.browse_source_button.clicked.connect(self.browseSource)
        self.l1 = QtGui.QHBoxLayout()
        self.l1.addWidget(self.source_filename)
        self.l1.addWidget(self.browse_source_button)
        
        
        
        self.button = QtGui.QPushButton("Import")
        self.button.clicked.connect(self.importMzML)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.source_label)
        layout.addLayout(self.l1)
        layout.addStretch(1)
        layout.addWidget(self.button)
        self.setLayout(layout)
        


        
      
class ImportThread(QtCore.QThread):
    taskFinished = QtCore.Signal(bool)
    def __init__(self,source,dest):
        QtCore.QThread.__init__(self)
        self.source = source
        self.dest = dest        


        
    def run(self):
        e = Experiment.Experiment()
        e.import_data_from_mzml(self.source)
        self.dest.append(e)
        
        #self.ip.close()
        self.taskFinished.emit(True)