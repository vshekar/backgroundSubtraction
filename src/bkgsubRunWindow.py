# -*- coding: utf-8 -*-
"""
Created on Fri Jul 18 09:02:52 2014

@author: vesheka
"""
from PyQt4 import QtGui,QtCore
import Experiment 
import math
from multiprocessing import Pool,Value
from datetime import datetime
import numpy as np
from math import ceil
from searchRT import *
from pyopenms import *


class bkgsubRunWindow(QtGui.QDialog):
    def __init__(self):
        super(bkgsubRunWindow,self).__init__()
        self.initUI()
    
    def initUI(self):
        self.setGeometry(300,300,300,150)
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.setWindowTitle('Background Subtraction')
        
        self.control_filename = QtGui.QLineEdit()
        self.control_label = QtGui.QLabel()
        self.control_label.setText("Control File:")
        self.select_control_button = QtGui.QPushButton("Select Control File")
        self.select_control_button.clicked.connect(self.selectDataControl)
        self.control_layout = QtGui.QHBoxLayout()
        self.control_layout.addWidget(self.control_filename)
        self.control_layout.addWidget(self.select_control_button)
        
        self.analyte_filename = QtGui.QLineEdit()
        self.analyte_label = QtGui.QLabel()
        self.analyte_label.setText("Analyte File:")
        self.select_analyte_button = QtGui.QPushButton("Select Analyte File")
        self.select_analyte_button.clicked.connect(self.selectDataAnalyte)
        self.analyte_layout = QtGui.QHBoxLayout()
        self.analyte_layout.addWidget(self.analyte_filename)
        self.analyte_layout.addWidget(self.select_analyte_button)
        
        self.result_filename = QtGui.QLineEdit()
        self.result_label = QtGui.QLabel()
        self.result_label.setText("Result File:")
        self.select_result_button = QtGui.QPushButton("Select Result File")
        self.select_result_button.clicked.connect(self.browseDest)
        self.result_layout =  QtGui.QHBoxLayout()
        self.result_layout.addWidget(self.result_filename)
        self.result_layout.addWidget(self.select_result_button)
        
        
        self.subtract_button = QtGui.QPushButton("Begin Subtraction")
        self.subtract_button.clicked.connect(self.subtract)
        
        self.layout = QtGui.QVBoxLayout()
        self.layout.addWidget(self.control_label)
        self.layout.addLayout(self.control_layout)
        self.layout.addWidget(self.analyte_label)
        self.layout.addLayout(self.analyte_layout)
        self.layout.addWidget(self.result_label)
        self.layout.addLayout(self.result_layout)
        self.layout.addStretch(1)
        self.layout.addWidget(self.subtract_button)
        self.setLayout(self.layout)
      
      
    def browseDest(self):
        fdlg = QtGui.QFileDialog()
        fdlg.setFileMode(QtGui.QFileDialog.AnyFile)
        fname = fdlg.getSaveFileName(self, 'Save file')
        print fname
        self.result_filename.setText(fname)
        
        
    def setDataList(self,dataList):
        self.listOfMzMLFiles = dataList        
    
    def selectDataControl(self):
        sdw = SelectDataWindow(self.listOfMzMLFiles)
        if not sdw.exec_():
            self.control_filename.setText(sdw.getFile())
            self.control_index = sdw.index
            
    def selectDataAnalyte(self):
        sdw = SelectDataWindow(self.listOfMzMLFiles)
        if not sdw.exec_():
            self.analyte_filename.setText(sdw.getFile())
            self.analyte_index = sdw.index
        
    def subtract(self):
        startTime = datetime.now()
        print(startTime)
        #self.st = SubtractThread(self.listOfMzMLFiles, self.analyte_index, self.control_index, str(self.result_filename.text()))
        #self.st.start()
        pb = ProgressBar(self.listOfMzMLFiles, self.analyte_index, self.control_index, str(self.result_filename.text()))
        pb.exec_()
        endTime = datetime.now()
        print("Endtime = " + str(endTime))
        print("Total Time = " + str(endTime-startTime))
        #self.st.taskFinished.connect(self.cleanup)
    
    def cleanup(self):
        print "Cleaning Up!"
        
        e = QtGui.QMessageBox(self)
        e.setWindowTitle("Complete")
        e.setText("Subtraction is complete")
        e.show()
        self.close()
        
class ProgressBar(QtGui.QProgressDialog):
    def __init__(self,mzml_list,analyte_index, control_index, result_filename):
        super(ProgressBar, self).__init__()
        self.listOfMzMLFiles = mzml_list
        self.analyte_index = analyte_index
        self.control_index = control_index
        self.result_filename = result_filename
        self.setRange(0,0)
        self.st = SubtractThread(self.listOfMzMLFiles, self.analyte_index, self.control_index, self.result_filename)
        self.st.start()
        self.st.taskFinished.connect(self.cleanup)
        self.st.partFinished.connect(self.updateBar)
        
    def updateBar(self,val):
        self.progressbar.setValue(val)         
        
    def cleanup(self):
        print "Cleaning Up!"
        
        e = QtGui.QMessageBox(self)
        e.setWindowTitle("Complete")
        e.setText("Subtraction is complete")
        e.show()
        self.close()
        
    
    
    
        
        
class SubtractThread(QtCore.QThread):
    taskFinished = QtCore.Signal(bool)
    partFinished = QtCore.Signal(int)
    def __init__(self,mzml_list,analyte_index, control_index, result_filename):
        QtCore.QThread.__init__(self)
        self.listOfMzMLFiles = mzml_list
        self.analyte_index = analyte_index
        self.control_index = control_index
        self.result_filename = result_filename
        

    def run(self):
        self.settings = QtCore.QSettings('settings.ini', QtCore.QSettings.IniFormat)
        self.settings.setFallbacksEnabled(False)
        
        
        time_window = float(self.settings.value("time_window").toPyObject())
        scaling_factor = float(self.settings.value("scaling_factor").toPyObject())
        tol_window = float(self.settings.value("tol_window").toPyObject())
        
        self.e = self.pick_peaks(self.listOfMzMLFiles[self.analyte_index])
        self.c = self.pick_peaks(self.listOfMzMLFiles[self.control_index])
        """        
        for experiment in self.listOfMzMLFiles:
            if experiment.filename is str(self.analyte_filename.text()):
                self.e = experiment
            elif experiment.filename is str(self.analyte_filename.text()):
                self.c = experiment
        """
        time_slices = []
        smallest_density = float("inf")
        density_list = []
        for time in range(0,int(math.ceil(self.e.RT[-1])),10):
            time_slices.append((time,time+10))
            den = self.get_density(self.e.RT,self.e.list_of_spectra,time,time+10)
            density_list.append(den)
            
        smallest_density = sum(density_list)/len(density_list)
        final_time_slices = []
        for i,den in enumerate(density_list):
            print den
            pieces = ceil(den/smallest_density)
            print pieces
            if pieces!=0:
                time_step = 10.0/pieces
            
            for p in range(int(pieces)):
                print "Adding time slice : " + str(time_slices[i][0]+(p*time_step)) + " - " + str(time_slices[i][0]+((p+1)*time_step))
                final_time_slices.append((time_slices[i][0]+(p*time_step),time_slices[i][0]+((p+1)*time_step)))
        
        print len(final_time_slices)
        arguments = []
        completed_tasks = Value('i',0)
        for i,time in enumerate(final_time_slices):
            arguments.append([self.c.RT, self.c.list_of_spectra, self.e.RT, self.e.list_of_spectra, time[0], time[1], i, tol_window, time_window, scaling_factor])
        pool = Pool(processes=int(self.settings.value("num_threads").toPyObject()), initializer= Experiment.init, initargs = (completed_tasks, ))
        results = pool.map(Experiment.subtract_multi,iter(arguments))
        #e.write_to_file("C:\\Users\\vesheka\\Desktop\\realdata\\Numpy_result.mzML")
        while(completed_tasks.value < len(final_time_slices)-1):
            self.partFinished.emit(float(a)/(len(final_time_slices)-1)*100)

        pool.close()
        pool.join()
        #print results
        print "Final count : " + str(completed_tasks.value)
        
        total_RT = np.ndarray([0])
        total_spectra = np.ndarray([0,])
        for rt,spec in results:
            total_RT = np.concatenate((total_RT,rt))
            total_spectra = np.concatenate((total_spectra,spec))
        op = Experiment.Experiment()
        op.RT = total_RT
        op.list_of_spectra = total_spectra
        op.write_to_file(self.result_filename)    
        self.taskFinished.emit(True)
        print "Subtracting Complete!"
    
    def get_density(self,analyte_RT,analyte_list_of_spectra,start_time,end_time):
        sliced_rt_indices = np.where(np.logical_and(analyte_RT[:]>=start_time, analyte_RT[:]<=end_time))
        sliced_spectra = analyte_list_of_spectra[sliced_rt_indices]
        sliced_rt = analyte_RT[sliced_rt_indices]
        total_points = 0
        for spec in sliced_spectra:
            total_points += spec.shape[0]
        return float(total_points)/float(end_time-start_time)    
        
    def pick_peaks(self,ip_exp):
        #Converting full mzml to processed mzml.....
        mzmlfilename = ip_exp.filename
        exp = MSExperiment()            #Input experiment to peak picker
        picked_exp = MSExperiment()     #Output experiment to peak picker
        
        mzmlFile = MzMLFile()
        mzmlFile.load(mzmlfilename,exp)
        paramAnalyte = Param()
        paramAnalyte.setValue("signal_to_noise",1.0,"") #S/N ratio
        p = PeakPickerHiRes()
        p.setParameters(paramAnalyte)
        p.pickExperiment(exp,picked_exp) #Result of peak picking is stored in picked_exp
        #picked_exp = exp
        op_exp = Experiment.Experiment()
        op_exp.import_data(picked_exp)
        return op_exp
        #self.import_data(picked_exp)
        

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
        