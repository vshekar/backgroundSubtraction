# -*- coding: utf-8 -*-
"""
Created on Wed Jul 16 15:01:23 2014

@author: vesheka
"""
import sys
from PyQt4 import QtGui
import subprocess
import os
import MainWindow as mw



def main():
    app = QtGui.QApplication(sys.argv)
    main_window = mw.MainWindow()
    sys.exit(app.exec_())
    
    
if __name__ == '__main__':
    main()