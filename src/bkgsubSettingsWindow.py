# -*- coding: utf-8 -*-
"""
Created on Thu Jul 17 15:29:52 2014

@author: vesheka
"""

from PyQt4 import QtGui,QtCore
import multiprocessing



class bkgsubSettingsWindow(QtGui.QDialog):
    def __init__(self):
        super(bkgsubSettingsWindow,self).__init__()
        self.initUI()
        
        
    def initUI(self):
        self.setGeometry(300,300,250,200)
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.setWindowTitle('Background Subtraction Settings')
        self.settings = QtCore.QSettings('settings.ini', QtCore.QSettings.IniFormat)
        self.settings.setFallbacksEnabled(False)
        self.mz_window_val = QtGui.QLineEdit()
        self.mz_window_label = QtGui.QLabel()
        self.mz_window_val.setText(str(self.settings.value("tol_window").toPyObject()))
        self.mz_window_label.setText("M/Z tolerance window (ppm) :  +/-")
        self.time_window_val = QtGui.QLineEdit()
        self.time_window_val.setText(str(self.settings.value("time_window").toPyObject()))
        self.time_window_label = QtGui.QLabel()
        self.time_window_label.setText("Time window (seconds)         :  +/-" )
        
        self.scaling_factor_val = QtGui.QLineEdit()
        self.scaling_factor_label = QtGui.QLabel()
        self.scaling_factor_val.setText(str(self.settings.value("scaling_factor").toPyObject()))
        self.scaling_factor_label.setText("Scaling factor                        :       " )
        
        self.num_cores_label = QtGui.QLabel()
        self.num_cores_label.setText("Number of cores available on this computer: " )
        self.num_cores = QtGui.QLabel()
        self.num_cores.setText(str(multiprocessing.cpu_count()))
        
        self.num_threads_label = QtGui.QLabel()
        self.num_threads_label.setText("Number of threads (Ideally 1 less than cores) :")
        self.num_threads_val = QtGui.QLineEdit()
        self.num_threads_val.setText(str(self.settings.value("num_threads").toPyObject()))
        
        self.minimum_ion_count_label = QtGui.QLabel()
        self.minimum_ion_count_label.setText("Minimum number of ions in adjacent scans : ")        
        self.minimum_ion_count_val = QtGui.QLineEdit()
        self.minimum_ion_count_val.setText(str(self.settings.value("minimum_ion_count").toPyObject()))
        
        self.total_scan_range_label = QtGui.QLabel()
        self.total_scan_range_label.setText("Total Scan range (should be more than min. ion count) :" )
        self.total_scan_range_val = QtGui.QLineEdit()
        self.total_scan_range_val.setText(str(self.settings.value("total_scan_range").toPyObject()))
        

        self.mz_layout = QtGui.QHBoxLayout()
        self.mz_layout.addWidget(self.mz_window_label)
        self.mz_layout.addWidget(self.mz_window_val)
        
        self.time_layout = QtGui.QHBoxLayout()
        self.time_layout.addWidget(self.time_window_label)
        self.time_layout.addWidget(self.time_window_val)
        
        self.scaling_layout = QtGui.QHBoxLayout()
        self.scaling_layout.addWidget(self.scaling_factor_label)
        self.scaling_layout.addWidget(self.scaling_factor_val)
        
        self.num_cores_layout = QtGui.QHBoxLayout()
        self.num_cores_layout.addWidget(self.num_cores_label)
        self.num_cores_layout.addWidget(self.num_cores)
        
        self.num_threads_layout = QtGui.QHBoxLayout()
        self.num_threads_layout.addWidget(self.num_threads_label)
        self.num_threads_layout.addWidget(self.num_threads_val)
        
        self.minimum_ion_count_layout = QtGui.QHBoxLayout()
        self.minimum_ion_count_layout.addWidget(self.minimum_ion_count_label)
        self.minimum_ion_count_layout.addWidget(self.minimum_ion_count_val)
        
        self.total_scan_range_layout =  QtGui.QHBoxLayout()
        self.total_scan_range_layout.addWidget(self.total_scan_range_label)
        self.total_scan_range_layout.addWidget(self.total_scan_range_val)
        
        
        
        self.button_save = QtGui.QPushButton("Save Settings")
        self.button_cancel = QtGui.QPushButton("Cancel")
        self.button_save.clicked.connect(self.saveSettings)
        self.button_cancel.clicked.connect(self.cancel)
        self.button_layout =  QtGui.QHBoxLayout()
        self.button_layout.addWidget(self.button_save)
        self.button_layout.addWidget(self.button_cancel)
        
        self.window_layout = QtGui.QVBoxLayout()
        self.window_layout.addLayout(self.mz_layout)
        self.window_layout.addLayout(self.time_layout)
        self.window_layout.addLayout(self.scaling_layout)
        self.window_layout.addLayout(self.num_cores_layout)
        self.window_layout.addLayout(self.num_threads_layout)
        self.window_layout.addLayout(self.minimum_ion_count_layout)
        self.window_layout.addLayout(self.total_scan_range_layout)
        self.window_layout.addStretch(1)
        self.window_layout.addLayout(self.button_layout)
        self.setLayout(self.window_layout)
        
        
        
        
    def saveSettings(self):
        self.settings.setValue("tol_window",float(self.mz_window_val.text()))
        self.settings.setValue("time_window", float(self.time_window_val.text()))
        self.settings.setValue("scaling_factor",float(self.scaling_factor_val.text()))
        self.settings.setValue("num_threads",int(self.num_threads_val.text()))
        self.settings.setValue("minimum_ion_count",int(self.minimum_ion_count_val.text()))
        self.settings.setValue("total_scan_range",int(self.total_scan_range_val.text()))
        self.close()
        
    def cancel(self):
        self.close()
        
        
        
        
        