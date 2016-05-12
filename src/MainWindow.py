# -*- coding: utf-8 -*-
"""
Created on Wed Jul 16 14:58:56 2014

@author: vesheka
"""
import PyQt4
from PyQt4 import QtGui,QtCore
#from pyqtgraph.Qt import QtGui,QtCore
import pyqtgraph as pg
import ConvertToMzMLWindow
import OpenMzMLFileWindow
import bkgsubSettingsWindow
import bkgsubRunWindow
import noiseReductionWindow
import GraphWindow
import numpy as np
from pyqtgraph.dockarea import *

class MainWindow(QtGui.QMainWindow):
    
    def __init__(self):
        super(MainWindow,self).__init__()
        self.initUI()
        self.ListOfMzMLFiles = []
        self.show()
    def initUI(self):
        #Initialize statusbar
        self.statusBar().showMessage('Ready')
        
        #Actions for menubar
        exitAction = QtGui.QAction('&Exit', self)
        exitAction.setStatusTip('Exit Application')
        exitAction.triggered.connect(self.close)
        
        convertToMzMLAction = QtGui.QAction('&Convert to MzML',self)
        convertToMzMLAction.setStatusTip('Converts wiff file to MzML')
        convertToMzMLAction.triggered.connect(self.convertToMzML)

        openMzMLFileAction = QtGui.QAction('&Open MzML File',self)
        openMzMLFileAction.setStatusTip('Open an MzML file')
        openMzMLFileAction.triggered.connect(self.openMzMLFile)    
        
        bkgsubSettingsAction = QtGui.QAction('&Settings',self)
        bkgsubSettingsAction.setStatusTip('Configure the settings for Background Subtraction')
        bkgsubSettingsAction.triggered.connect(self.bkgsubSettings)
        
        bkgsubRunAction = QtGui.QAction('&Run',self)
        bkgsubRunAction.setStatusTip('Run the background subtraction algorithm')
        bkgsubRunAction.triggered.connect(self.bkgsubRun)
        
        noiseReductionAction = QtGui.QAction('&Noise Reduction',self)
        noiseReductionAction.setStatusTip('Perform Noise reduction on mzML file')
        noiseReductionAction.triggered.connect(self.noiseReductionRun)
        
        #Menubar display
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openMzMLFileAction)  
        fileMenu.addAction(convertToMzMLAction)                   
        fileMenu.addAction(exitAction)
        
        subtractMenu = menubar.addMenu('&Background Subtraction')
        subtractMenu.addAction(bkgsubSettingsAction)
        subtractMenu.addAction(bkgsubRunAction)
        subtractMenu.addAction(noiseReductionAction)
        
        
        #Main window settings
        
        self.setGeometry(300,300,640,480)
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.setWindowTitle('Background Subtractor')
        
        self.fileListWidget = QtGui.QListWidget()        
        self.fileLabel = QtGui.QLabel()
        self.fileLabel.setText("List of imported files: ")
        
        self.button = QtGui.QPushButton("Delete MzML File")
        self.button.clicked.connect(self.deleteMzML)
        
        self.mainlayout = QtGui.QVBoxLayout()
        self.mainlayout.addWidget(self.fileLabel)
        self.mainlayout.addWidget(self.fileListWidget)
        self.mainlayout.addWidget(self.button)
        
        self.window = QtGui.QWidget()
        self.window.setLayout(self.mainlayout)
        self.setCentralWidget(self.window)
        
        self.setWindowIcon(QtGui.QIcon('Taklogo.png'))
        
        self.fileListWidget.doubleClicked.connect(self.showGraph)
        
        
    def showGraph(self):
        self.index = self.fileListWidget.currentRow()
        print self.index
        
        #app = QtGui.QApplication([])
        #win = pg.GraphicsWindow(title="File : " + self.ListOfMzMLFiles[self.index].filename)
        #win.addPlot(title="MzML File",y=self.ListOfMzMLFiles[self.index].graph_points)
        self.sgw = GraphWindow.ShowGraphWindow(self.ListOfMzMLFiles[self.index])
        self.sgw.show()
        #pg.plot(title="LCMS Data",y=self.ListOfMzMLFiles[self.index].graph_points)
        
        
    def bkgsubSettings(self):
        bkgsubSettings_window = bkgsubSettingsWindow.bkgsubSettingsWindow()
        bkgsubSettings_window.show()
        bkgsubSettings_window.exec_()        
        
        
    def bkgsubRun(self):
        self.bkgsubRun_window = bkgsubRunWindow.bkgsubRunWindow() 
        self.bkgsubRun_window.setDataList(self.ListOfMzMLFiles)
        self.bkgsubRun_window.show()
        self.bkgsubRun_window.exec_()
        
    def deleteMzML(self):
        index = self.fileListWidget.currentRow()
        del self.ListOfMzMLFiles[index]
        self.refreshFileList()
        
    def convertToMzML(self):
        convertToMzML_window = ConvertToMzMLWindow.ConvertToMzMLWindow()
        convertToMzML_window.show()
        convertToMzML_window.exec_()
        
    def openMzMLFile(self):
        self.openMzMLFile_window = OpenMzMLFileWindow.OpenMzMLFileWindow()
        self.openMzMLFile_window.setMzMLList(self.ListOfMzMLFiles)
        self.openMzMLFile_window.show()
        self.openMzMLFile_window.exec_()
        self.refreshFileList()
        
        
    def refreshFileList(self):
        self.fileListWidget.clear()
        for exp in self.ListOfMzMLFiles:
            self.fileListWidget.addItem(exp.filename)
            
    def noiseReductionRun(self):
        self.noiseReductionRun_window = noiseReductionWindow.noiseReductionWindow()
        self.noiseReductionRun_window.setDataList(self.ListOfMzMLFiles)
        self.noiseReductionRun_window.show()
        self.noiseReductionRun_window.exec_()
        