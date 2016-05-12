# -*- coding: utf-8 -*-
"""
Created on Mon Aug 11 09:25:42 2014

@author: vesheka
"""

import PyQt4
from PyQt4 import QtGui,QtCore
#from pyqtgraph.Qt import QtGui,QtCore
import pyqtgraph as pg
import numpy as np

class ShowGraphWindow(pg.GraphicsWindow):
    def __init__(self,exp):
        super(ShowGraphWindow,self).__init__()
        self.exp = exp
        self.current_index = 0
        self.current_spec_index = 0
        self.graph_in_focus = 0
        self.initUI()
        
        
    def initUI(self):
        #self.setBackground('w')
        
        self.setGeometry(300,300,640,480)
        self.setWindowTitle("Graph of : " + self.exp.filename)
        
        
        self.label = pg.LabelItem(justify='left')
        self.addItem(self.label)
        
        
        self.addItem(self.label,row=1,col=0)
        self.p1 = self.addPlot(row=2, col=0)
        self.label2 = pg.LabelItem(justify='bottom')
        self.addItem(self.label2,row=3,col=0)
        self.p2 = self.addPlot(row=4,col=0)
        
        
        self.p1.plot(title="LCMS Data",y=self.exp.graph_points,x=self.exp.RT,pen="w")
        self.p1.setAutoVisible(y=True)
        
        
        
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        self.p1.addItem(self.vLine, ignoreBounds=True)
        self.p1.addItem(self.hLine, ignoreBounds=True)
        
        self.p2.plot(title="Retention Time = " + str(self.exp.RT[0]))
        self.barGraph = pg.BarGraphItem(x=self.exp.list_of_spectra[0][:,0],height=self.exp.list_of_spectra[0][:,1],width=0.05)      
        self.p2.addItem(self.barGraph)
        
        
        self.proxy = pg.SignalProxy(self.p1.scene().sigMouseMoved, rateLimit=100, slot=self.mouseMoved)
        self.proxy2 = pg.SignalProxy(self.p1.scene().sigMouseClicked, slot=self.mouseClicked)
        
        self.proxy3 = pg.SignalProxy(self.p2.scene().sigMouseClicked,slot=self.mouseClicked2)
        
        #self.addWidget(self.gv)
        #self.d1.addWidget(self.p1)
        #self.d2.addWidget(self.p2)        
        #self.show()
        
    def mouseClicked2(self,evt):
        
        pos =  evt[0].scenePos()
        if self.p2.sceneBoundingRect().contains(pos):
            self.graph_in_focus =1
            self.drawSpectrum()
            mousePoint = self.p2.vb.mapSceneToView(pos)
            self.current_spec_index = (np.abs(self.exp.list_of_spectra[self.current_index][:,0]-mousePoint.x())).argmin()
            self.drawArrow()


    def drawArrow(self):
        self.label2.setText("<span style='font-size: 12pt'>Retention Time (sec)=%0.4f     <span style='color: red'>M/Z = %0.4f</span>     <span style='color: red'>Intensity = %0.4f</span>"%(self.exp.RT[self.current_index],self.exp.list_of_spectra[self.current_index][self.current_spec_index,0],self.exp.list_of_spectra[self.current_index][self.current_spec_index,1]))
        arrow = pg.ArrowItem(pos=(self.exp.list_of_spectra[self.current_index][self.current_spec_index,0],self.exp.list_of_spectra[self.current_index][self.current_spec_index,1]), angle=-90)
        self.p2.addItem(arrow)        

     
    def keyPressEvent(self, e):
        print self.graph_in_focus
        if self.graph_in_focus == 1:
            if e.key() == QtCore.Qt.Key_Right:
                
                if self.current_spec_index+1 < len(self.exp.list_of_spectra[self.current_index]):
                    self.current_spec_index += 1
                
            if e.key() == QtCore.Qt.Key_Left:
                if self.current_spec_index - 1 >= 0 :
                    self.current_spec_index -= 1
            self.drawSpectrum()    
            self.drawArrow()
        elif self.graph_in_focus == 0:
            if e.key() == QtCore.Qt.Key_Right:
                if self.current_index+1 < len(self.exp.RT):
                    rt = self.exp.RT[self.current_index]
                    mz = self.exp.graph_points_mz[self.current_index]
                    inten = self.exp.graph_points[self.current_index]
                    self.current_index += 1
                    self.label.setText("<span style='font-size: 12pt'>Retention Time (sec)=%0.4f,  <span style='color: red'>Intensity=%0.4f</span>, <span style='color: red'>Intensity=%0.4f</span>" % (rt,mz ,inten))
            if e.key() == QtCore.Qt.Key_Left:
                if self.current_index-1 >= 0 :
                    self.current_index-=1
                    self.label.setText("<span style='font-size: 12pt'>Retention Time (sec)=%0.4f,   <span style='color: red'>Intensity=%0.4f</span>, <span style='color: red'>Intensity=%0.4f</span>" % (self.exp.RT[self.current_index],self.exp.graph_points_mz[self.current_index], self.exp.graph_points[self.current_index]))
            self.vLine.setPos(self.exp.RT[self.current_index])
            self.hLine.setPos(self.exp.graph_points[self.current_index])
            self.current_spec_index = 0
            self.drawSpectrum()
            self.drawArrow()


            
        
    def mouseMoved(self,evt):
        pos = evt[0]  ## using signal proxy turns original arguments into a tuple
        #print "pos = " + str(pos.x()) + "," + str(pos.y())
        if self.p1.sceneBoundingRect().contains(pos):
            mousePoint = self.p1.vb.mapSceneToView(pos)
            
            
            
            #print "MousePoint = " + str(mousePoint.x()) + "," + str(mousePoint.y())
            idx = (np.abs(self.exp.RT-mousePoint.x())).argmin()
            if idx > 0 and idx < len(self.exp.graph_points):
                self.label.setText("<span style='font-size: 12pt'>Retention Time (sec)=%0.4f,   <span style='color: red'>Intensity=%0.4f</span>" % (self.exp.RT[idx], self.exp.graph_points[idx]))
            self.vLine.setPos(mousePoint.x())
            self.hLine.setPos(self.exp.graph_points[idx])

    def mouseClicked(self,evt):
        
        pos =  evt[0].scenePos()
        if self.p1.sceneBoundingRect().contains(pos):
            self.graph_in_focus = 0
            mousePoint = self.p1.vb.mapSceneToView(pos)
            
            idx = (np.abs(self.exp.RT-mousePoint.x())).argmin()
            self.current_index = idx
            #print "MousePoint = " + str(mousePoint.x()) + "," + str(mousePoint.y())
            print (idx)
            self.drawSpectrum()
            #self.p2 = pg.BarGraphItem(x=self.exp.list_of_spectra[idx][:,0],height=self.exp.list_of_spectra[idx][:,1],width=0.1)
            #self.p2.show()
            
    def drawSpectrum(self):
        self.p2.clear()
        self.p2.plot(title="RT = " + str(self.exp.RT[self.current_index]))
        self.label2.setText("<span style='font-size: 12pt'>Retention Time (sec)=%0.1f"%(self.exp.RT[self.current_index]))
        self.barGraph = pg.BarGraphItem(x=self.exp.list_of_spectra[self.current_index][:,0],height=self.exp.list_of_spectra[self.current_index][:,1],width=0.01)      
        self.p2.addItem(self.barGraph)